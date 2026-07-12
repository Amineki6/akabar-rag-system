# --- 1. Imports ---
import os
import uuid
import json
import asyncio

import time
import redis
import psutil


from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Cookie
from typing import Optional
from fastapi.responses import StreamingResponse
from starlette.responses import Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY, Gauge
import redis
from bff import (
    WeatherService, AudioTitleService, TextProcessor, 
    StreamingService, ReportService
)

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


from mongo_config import initialize_mongodb, log_initial_request, update_final_log
from logging_config import setup_logging, request_id_var
import logging

setup_logging()
logger = logging.getLogger(__name__)


# --- 2. Configuration and App Setup ---
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
AGENT_HOSTNAME = os.getenv("AGENT_HOSTNAME", "127.0.0.1")
FOLLOWUP_HOSTNAME = os.getenv("FOLLOWUP_HOSTNAME", "127.0.0.1")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

limiter = Limiter(key_func=get_remote_address, storage_uri=f"redis://{REDIS_HOST}:{REDIS_PORT}/1")


# --- ADD PROMETHEUS METRIC DEFINITIONS ---
REQUESTS = Counter(
    'http_requests_total',
    'Total number of HTTP requests.',
    ['method', 'endpoint', 'http_status']
)
LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds.',
    ['method', 'endpoint'],
    buckets=(0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 45.0, 60.0, float('inf'))
)

IN_PROGRESS_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently in progress.'
)
STREAM_PROCESSING_SECONDS_TOTAL = Counter(
    'stream_processing_seconds_total',
    'Total time spent processing streams in seconds.'
)
PROCESS_CPU_USAGE = Gauge(
    'process_cpu_percent',
    'Current CPU usage of the FastAPI application process (%)'
)
PROCESS_MEMORY_USAGE = Gauge(
    'process_memory_percent',
    'Current memory usage of the FastAPI application process (%)'
)

# --- Background Task for Resource Monitoring ---
async def update_resource_metrics():
    """Periodically updates the CPU and Memory usage metrics for the current process."""
    logger.info("Starting resource metrics collection task.")
    while True:
        current_process = psutil.Process()
        
        cpu_percent = current_process.cpu_percent(interval=1.0)
        memory_percent = current_process.memory_percent()

        PROCESS_CPU_USAGE.set(cpu_percent)
        PROCESS_MEMORY_USAGE.set(memory_percent)
        
        await asyncio.sleep(15)

# --- Application Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events.
    """
    # --- Code to run on startup ---
    logger.info("Application startup: starting background tasks...")
    asyncio.create_task(update_resource_metrics())
    
    yield # The application runs while the lifespan context is active
    
    # --- Code to run on shutdown (if any) ---
    logger.info("Application shutdown.")

# --- FastAPI App Setup ---
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # 1. Try to get the session ID from the cookies
    session_id = request.cookies.get("sessionId")
    
    # 2. If no session ID, create a new one
    if not session_id:
        session_id = str(uuid.uuid4())
        # Add the new ID to the request's state so the endpoint can use it
        request.state.session_id = session_id
        # Mark that we need to set a cookie on the response
        request.state.new_session = True 
    else:
        # If a cookie already exists, just add it to the state
        request.state.session_id = session_id

    # 3. Continue to the actual endpoint
    response = await call_next(request)

    # 4. If we created a new session, set the cookie on the response
    if hasattr(request.state, "new_session"):
        is_production = os.getenv("ENVIRONMENT") == "production"
        response.set_cookie(
            key="sessionId",
            value=request.state.session_id,
            httponly=True,
            secure=is_production,
            samesite="lax"
        )
        logger.info(f"Setting new session cookie (Secure={is_production})")
        
    return response



# --- CORS Middleware ---
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://akabar.ai",
    "https://www.akabar.ai",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- ADD INSTRUMENTATION MIDDLEWARE ---
@app.middleware("http")
async def instrument_requests(request: Request, call_next):
    # Bypass instrumentation for metrics and the streaming endpoint
    if request.url.path in ["/metrics", "/api/chat"]:
        return await call_next(request)
    
    IN_PROGRESS_REQUESTS.inc()
    start_time = time.time()
    status_code = 500  # Default to 500 in case of an unhandled exception
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency = time.time() - start_time
        # Record metrics for non-streaming endpoints
        LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)
        REQUESTS.labels(method=request.method, endpoint=request.url.path, http_status=status_code).inc()
        IN_PROGRESS_REQUESTS.dec()


# --- Initialize Services and Data ---
try:
    MASTER_LOCATIONS = json.loads(redis_client.get("locations"))
except (TypeError, json.JSONDecodeError) as e:
    logger.error(f"Failed to load master locations from Redis: {e}")
    MASTER_LOCATIONS = {}


weather_service = WeatherService(REDIS_HOST, REDIS_PORT)
audio_service = AudioTitleService(REDIS_HOST, REDIS_PORT)
text_processor = TextProcessor()
streaming_service = StreamingService(AGENT_HOSTNAME, FOLLOWUP_HOSTNAME)
api_log_collection, report_collection = initialize_mongodb()


# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str
    source: str
    mode: str
    circuit: str | None

class ReportRequest(BaseModel):
    """Defines the expected data structure for a report submission."""
    reason: str
    requestId: str

# --- API Routes ---
@app.post('/api/chat')
@limiter.limit("20/minute")
async def chat_endpoint(chat_req: ChatRequest, request: Request):
    """
    Handles chat requests, logs them, and streams back a processed response.
    Now also handles timing and final logging.
    """
    session_id = request.state.session_id 
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    logger.info(f"INPUT RECEIVED")
    logger.debug(f"Received message: '{chat_req.message}'")
    
    log_initial_request(
        api_log_collection,
        request_id,
        session_id,
        chat_req.message,
        chat_req.source,
        request
    )
    print(f"Logged initial request with mode: {chat_req.mode}")
    # This is the original generator that produces the stream and returns the log data
    original_generator = streaming_service.stream_rag_response(
        message=chat_req.message, 
        session_id=session_id,
        request_id=request_id,
        mode=chat_req.mode,
        circuit=chat_req.circuit,
        weather_service=weather_service,
        audio_service=audio_service,
        master_locations=MASTER_LOCATIONS
    )


    # A more robust wrapper to correctly capture the generator's return value
    async def robust_timed_streamer():
        # --- START of instrumentation ---
        IN_PROGRESS_REQUESTS.inc()
        start_time = time.perf_counter()
        status_code = 200 # Assume success unless an error occurs
        # --- END of instrumentation ---
        
        log_data_from_generator = None
        try:
            async for chunk in original_generator:
                if isinstance(chunk, dict):
                    log_data_from_generator = chunk
                    metrics_value = log_data_from_generator.pop('metrics')
                else:
                    yield chunk
        except Exception:
            status_code = 500 # Mark as failed on exception
            raise # Re-raise to ensure the client gets an error
        finally:
            # --- START of final metric recording ---
            end_time = time.perf_counter()
            latency = end_time - start_time
            total_end_to_end_duration_ms = latency * 1000
            
            # Record all the metrics for this stream
            STREAM_PROCESSING_SECONDS_TOTAL.inc(latency)
            LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)
            REQUESTS.labels(method=request.method, endpoint=request.url.path, http_status=status_code).inc()
            IN_PROGRESS_REQUESTS.dec()
            
            logger.debug(f"Response streaming finished in {total_end_to_end_duration_ms:.2f} ms")

            if log_data_from_generator:
                metrics_value['total_end_to_end_duration_ms'] = total_end_to_end_duration_ms
                update_final_log(api_log_collection, request_id, log_data_from_generator, metrics=metrics_value)
            else:
                logger.warning("No log data dictionary was yielded; skipping final log update.")
            # --- END of final metric recording ---


    logger.info("Response streaming initiated...")
    return StreamingResponse(robust_timed_streamer(), media_type="application/x-ndjson")


@app.post('/api/report')
@limiter.limit("20/minute")
async def report_endpoint(report_req: ReportRequest, request: Request):
    """
    Receives a report from the client and logs it to the corresponding
    request document in MongoDB.
    """
    # --- 1. Get the session_id from the request state ---
    session_id = request.state.session_id 

    # Set request_id for logging context
    request_id_var.set(report_req.requestId)
    # --- 2. Update logging to include the session_id ---
    logger.info(f"Received report for request_id: {report_req.requestId} (Session: {session_id})")
    logger.debug(f"Report details: {report_req.model_dump()}")
    
    try:
        ReportService.log_report_to_db(
            report_collection=report_collection,
            request_id=report_req.requestId,
            session_id=session_id, 
            report_data=report_req.model_dump()
        )
        return {"status": "ok", "message": "Report logged successfully."}
    except Exception as e:
        logger.error(f"Internal server error while logging report for request_id {report_req.requestId}: {e}")
        # Return a 500 error if something goes wrong
        raise HTTPException(status_code=500, detail="An internal error occurred while logging the report.")
    

@app.post("/api/session/new")
async def create_new_session(response: Response):
    """
    Expires the old session and creates a new one by setting a new cookie.
    """
    # 1. Generate a brand new, secure session ID
    new_session_id = str(uuid.uuid4())
    is_production = os.getenv("ENVIRONMENT") == "production"

    # 2. Set the new cookie on the response object
    response.set_cookie(
        key="sessionId",
        value=new_session_id,
        httponly=True,
        secure=is_production,
        samesite="lax"
    )
    logger.info(f"New session explicitly requested. New ID: {new_session_id}")
    
    # 3. Return a success message
    return {"status": "ok", "message": "New session created."}
    

@app.get("/metrics")
async def metrics():
    """
    Exposes Prometheus metrics.
    """
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")



# --- 8. Run the Server ---
if __name__ == '__main__':
    logger.info("Enhanced Server starting")
    logger.info("Loading services...")
    audio_service.load_audio_titles()
    logger.info("Services loaded successfully")
    # Note: For production, use a proper ASGI server like Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8070)