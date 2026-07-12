# --- 1. Imports ---
import os
import uuid
import asyncio
import json
import logging # Import the logging module

from dotenv import load_dotenv
from quart import Quart, request, jsonify, Response, make_response
from quart_cors import cors

# Your existing agent imports
from agent import HierarchicalAgent
import time
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY, Gauge
import psutil 

from redis import asyncio as aioredis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver


from mongo_config import initialize_mongodb, log_initial_request, update_final_log
from logging_config import setup_logging, request_id_var, original_request_id_var

# --- 2. Configuration and App Setup ---
load_dotenv()

# Call the setup function to configure logging for the entire application
setup_logging()
logger = logging.getLogger(__name__) # Get a logger instance for this module

app = Quart(__name__)
app = cors(app, allow_origin="*")


# --- ADD PROMETHEUS METRIC DEFINITIONS ---
# A Counter to count the total number of HTTP requests.
REQUESTS = Counter(
    'http_requests_total',
    'Total number of HTTP requests.',
    ['method', 'endpoint', 'http_status']
)
# A Histogram to measure the latency of HTTP requests.
LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds.',
    ['method', 'endpoint'],
    buckets=(0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0, float('inf'))
)

IN_PROGRESS_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['service']
)

STREAM_PROCESSING_SECONDS_TOTAL = Counter(
    'stream_processing_seconds_total',
    'Total time spent processing streams in seconds'
)

PROCESS_CPU_USAGE = Gauge(
    'process_cpu_percent',
    'Current CPU usage of the Quart application process (%)'
)
PROCESS_MEMORY_USAGE = Gauge(
    'process_memory_percent',
    'Current memory usage of the Quart application process (%)'
)

async def update_resource_metrics():
    """Periodically updates the CPU and Memory usage metrics for the current process."""
    logger.info("Starting resource metrics collection task.") # Add a log to confirm it starts
    while True:
        # --- MODIFIED: Get the current process *inside* the loop ---
        # This ensures each worker process monitors itself correctly.
        current_process = psutil.Process()
        
        # Get current usage. The first call to cpu_percent should have a non-zero interval.
        cpu_percent = current_process.cpu_percent(interval=1.0)
        memory_percent = current_process.memory_percent()

        # Update the gauges
        PROCESS_CPU_USAGE.set(cpu_percent)
        PROCESS_MEMORY_USAGE.set(memory_percent)
        
        # Wait for a defined interval before the next update
        await asyncio.sleep(15) # Update every 15 seconds

# Declare global variables, but initialize them as None
expert_agent = None
api_log_collection = None
checkpointer_context = None

@app.before_serving
async def startup():
    """
    This function runs once before the server starts serving requests.
    It's the perfect place for async initializations.
    """
    global expert_agent, api_log_collection, checkpointer_context
    
    logger.info("Server starting up... Initializing components.")

    # Build Redis URL from environment variables
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_url = f"redis://{redis_host}:{redis_port}/0"
    
    # TTL configuration
    ttl_config = {
        "default_ttl": 120,  # Expire checkpoints after 120 seconds (2 minutes)
        "refresh_on_read": True,  # Reset expiration time when reading checkpoints
    }

    # Use the async context manager pattern
    checkpointer_context = AsyncRedisSaver.from_conn_string(redis_url, ttl=ttl_config)
    checkpointer = await checkpointer_context.__aenter__()

    # Initialize components inside this async function
    expert_agent = HierarchicalAgent(
        checkpointer=checkpointer,
        model_router="gpt-4.1-mini", 
        model_selector="gpt-4.1-mini",
        model_worker="gpt-4.1-mini", 
        model_supervisor="gpt-4.1", 
        verbose=True
    )
    
    # Correctly await the async database initialization
    api_log_collection = await initialize_mongodb()
    asyncio.create_task(update_resource_metrics())
    logger.info("Agent and Database initialized successfully. Server is ready.")


def instrument_streaming_endpoint(func):
    """
    Correctly instruments a streaming endpoint by capturing the request context
    before the stream begins.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # --- CAPTURE request context here, while it's still valid ---
        req_path = request.path
        req_method = request.method
        
        start_time = time.time()
        IN_PROGRESS_REQUESTS.labels(service='agent').inc()
        http_status = 200

        # This async generator will wrap the original one
        async def metrics_wrapper_generator(original_response):
            try:
                async for chunk in original_response.response:
                    yield chunk
            except Exception:
                nonlocal http_status
                http_status = 500
                raise
            finally:
                latency = time.time() - start_time
                # --- USE the captured variables inside the finally block ---
                STREAM_PROCESSING_SECONDS_TOTAL.inc(latency)
                REQUESTS.labels(method=req_method, endpoint=req_path, http_status=http_status).inc()
                LATENCY.labels(method=req_method, endpoint=req_path).observe(latency)
                IN_PROGRESS_REQUESTS.labels(service='agent').dec()

        # Call the original endpoint function to get the streaming Response object
        original_response = await func(*args, **kwargs)

        # Return a new Response, replacing the original generator with our wrapper
        return Response(metrics_wrapper_generator(original_response),
                        mimetype=original_response.mimetype,
                        status=original_response.status_code,
                        headers=original_response.headers)

    return wrapper

# --- Middleware for NON-STREAMING endpoints ---

@app.before_request
async def start_instrumentation_middleware():
    """Runs before non-streaming requests to start the timer and gauge."""
    if request.path in ['/chat', '/metrics']:
        return
    IN_PROGRESS_REQUESTS.labels(service='agent').inc()
    request.start_time = time.time()

@app.after_request
async def record_successful_request_middleware(response):
    """Runs after successful non-streaming requests to record final metrics."""
    if request.path in ['/chat', '/metrics']:
        return response
    
    latency = time.time() - request.start_time
    LATENCY.labels(method=request.method, endpoint=request.path).observe(latency)
    REQUESTS.labels(method=request.method, endpoint=request.path, http_status=response.status_code).inc()
    return response

@app.teardown_request
async def finish_instrumentation_middleware(exception=None):
    """
    Runs after non-streaming requests, even on exceptions.
    This is the safety net to decrement the in-progress gauge.
    """
    if request.path in ['/chat', '/metrics']:
        return

    # This ensures the gauge is decremented even if an error occurs in a non-streaming endpoint
    IN_PROGRESS_REQUESTS.labels(service='agent').dec()

# --- 6. Quart Route ---
@app.route('/chat', methods=['POST'])
@instrument_streaming_endpoint
async def chat():
    """
    Handles the main chat logic, receiving a user message and streaming a response.
    """
    # Generate request_id first to use it in all subsequent logs for this request
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    data = await request.get_json()
    if not data:
        logger.warning("Request received with invalid JSON.")
        return jsonify({"error": "Invalid JSON provided"}), 400

    user_input = data.get('message')
    session_id = data.get('session_id')
    original_request_id = data.get('original_request_id')
    original_request_id_var.set(original_request_id)
    mode = data.get('mode', 'default')
    circuit = data.get('circuit', None)

    logger.info(f"INPUT RECEIVED")
    logger.debug(f"Received message: '{user_input}' with session ID: {session_id}")

    if not user_input or not session_id:
        logger.warning("Request missing 'message' or 'session_id'.")
        return jsonify({"error": "Missing 'message' or 'session_id' in request body"}), 400

    # Log the initial request using the helper function
    await log_initial_request(api_log_collection, request_id, session_id, original_request_id, user_input, mode, circuit)

    async def stream_response_generator():
        """
        An async generator that streams the agent's response and handles final logging.
        """
        full_response_text = ""
        response_metadata = {}
        response_metrics = {}

        # 1. Yield initial context data
        try:
            context_data = {
                "type": "context",
                "data": {"session_id": session_id, "original_request_id": original_request_id}
            }
            yield f"{json.dumps(context_data)}\n"
        except Exception as e:
            logger.error(f"Error yielding context: {e}")
    
        # 2. Stream and process the agent's response
        try:
            async for chunk in expert_agent.stream_response(user_input, session_id, mode, circuit):
                try:
                    data_obj = json.loads(chunk)
                    chunk_type = data_obj.get("type")
                    chunk_data = data_obj.get("data")

                    if chunk_type == "token":
                        full_response_text += chunk_data
                    elif chunk_type == "metadata":
                        response_metadata = chunk_data
                    elif chunk_type == "metrics":
                        response_metrics = chunk_data
                        continue
                    
                    yield chunk 
                
                except json.JSONDecodeError:
                    yield chunk
        except Exception as e:
            logger.error(f"An error occurred during streaming: {e}", exc_info=True)
            error_message = {"type": "error", "data": "Sorry, an error occurred."}
            yield f"{json.dumps(error_message)}\n"
        
        # 3. Update the log after the stream is complete
        finally:
            logger.info("Stream finished. Updating final log in database.")
            await update_final_log(api_log_collection, request_id, full_response_text, response_metadata, response_metrics)

    return Response(stream_response_generator(), mimetype='application/x-ndjson')

@app.route('/metrics')
async def metrics():
    """
    This endpoint exposes Prometheus metrics.
    """

    content = generate_latest(REGISTRY)
    response = await make_response(content)
    response.headers['Content-Type'] = 'text/plain; version=0.0.4'
    return response



# --- 7. Main Execution ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)