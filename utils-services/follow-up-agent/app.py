import os
import uuid
from datetime import datetime, timezone
import json
from contextlib import asynccontextmanager
import time
import asyncio 

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import Response 
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY, Gauge
import psutil 

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
import logging

from mongo_config import log_suggestion_request, update_suggestion_log
from logging_config import setup_logging, request_id_var, original_request_id_var

setup_logging()
logger = logging.getLogger(__name__)

# --- Configuration and Setup ---
load_dotenv()

SERVICE_NAME = "follow-up"

REQUESTS = Counter(
    'http_requests_total',
    'Total number of HTTP requests.',
    ['method', 'endpoint', 'http_status']
)
LATENCY = Histogram(
    'http_request_latency_seconds',
    'HTTP request latency in seconds.',
    ['method', 'endpoint'],
    buckets=(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)
IN_PROGRESS_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently in progress.',
    ['service']
)
PROCESS_CPU_USAGE = Gauge(
    'process_cpu_percent',
    'Current CPU usage of the application process (%)',
    ['service']
)
PROCESS_MEMORY_USAGE = Gauge(
    'process_memory_percent',
    'Current memory usage of the application process (%)',
    ['service']
)

# --- Global Variables for DB Connection ---
mongo_client = None
log_collection = None

async def update_resource_metrics():
    """Periodically updates the CPU and Memory usage metrics for the current process."""
    logger.info("Starting resource metrics collection task.")
    while True:
        current_process = psutil.Process()
        
        cpu_percent = current_process.cpu_percent(interval=1.0)
        memory_percent = current_process.memory_percent()

        logger.debug(f"Resource Metrics Update: CPU={cpu_percent}%, Memory={memory_percent}%")

        PROCESS_CPU_USAGE.labels(service=SERVICE_NAME).set(cpu_percent)
        PROCESS_MEMORY_USAGE.labels(service=SERVICE_NAME).set(memory_percent)
        
        await asyncio.sleep(15)

# --- Lifespan Manager for Startup/Shutdown Tasks ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles async startup and shutdown events.
    Connects to MongoDB on startup and closes the connection on shutdown.
    """
    global mongo_client, log_collection
    logger.info("Connecting to MongoDB...")
    try:
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")
        if not user or not password:
            logger.warning("MONGO_USER or MONGO_PASSWORD environment variable not set. Logging is disabled.")
        else:
            mongo_uri = f"mongodb://{user}:{password}@mongo:27017/maindb?authSource=admin"
            mongo_client = AsyncIOMotorClient(mongo_uri)
            await mongo_client.admin.command('ping')
            db = mongo_client['chat_logs']
            log_collection = db['suggestion_requests']
            logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB. Logging will be disabled. Error: {e}")
        mongo_client = None
        log_collection = None
        
    asyncio.create_task(update_resource_metrics())
    yield

    if mongo_client:
        print("Closing MongoDB connection.")
        mongo_client.close()

# --- FastAPI App Initialization ---
app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def instrument_requests(request: Request, call_next):
    # Bypass instrumentation for the metrics endpoint
    excluded_paths = ["/metrics", "/favicon.ico"]
    if request.url.path in excluded_paths:
        return await call_next(request)
        
    IN_PROGRESS_REQUESTS.labels(service=SERVICE_NAME).inc() # INCREMENT GAUGE
    start_time = time.time()
    status_code = 500 # Default to 500 for unhandled exceptions
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency = time.time() - start_time
        
        # Record all metrics
        LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)
        REQUESTS.labels(method=request.method, endpoint=request.url.path, http_status=status_code).inc()
        IN_PROGRESS_REQUESTS.labels(service=SERVICE_NAME).dec() # DECREMENT GAUGE

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models for Data Validation ---
class SuggestionItem(BaseModel):
    question: str = Field(description="The generated follow-up question.")
    keyword: str = Field(description="The keyword from the original text that prompted the question.")


class Suggestions(BaseModel):
    suggestions: List[SuggestionItem] = Field(description="A list of suggestion items.")


class SuggestionRequestInput(BaseModel):
    text: str
    session_id: str
    original_request_id: str


# --- Core AI Logic (LangChain) ---
def create_suggestion_chain():
    """
    Creates a LangChain pipeline (chain) to extract keywords and format questions.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are a highly specialized assistant for identifying explicit choices offered in a question. Your task is to analyze the provided text and determine if it presents two or more distinct, clickable options for a user.

        Primary Rules:

        Only extract keywords if the question presents a clear, binary, or multiple-choice option, often connected by "or".

        Do NOT extract keywords from open-ended questions (e.g., "What would you like to know?").

        The question field in your output must be a complete sentence formulated as a direct request from the user's perspective. It should be the query the user would send to the AI after clicking the suggestion. Use imperative forms like "Tell me about..." or "Explain...". Crucially, do not phrase it as a question back to the user (e.g., avoid "Would you like to know...?").

        GOOD Example (A Clear Choice):

        Input Text: "Would you like to hear more about the history or the geography of Morocco?"

        Explanation: "History" and "geography" are distinct options. The generated questions are correctly phrased as user commands.

        Correct Output:

        {{
        "suggestions": [
        {{
        "question": "Tell me more about the history of Morocco.",
        "keyword": "history"
        }},
        {{
        "question": "Tell me more about the geography of Morocco.",
        "keyword": "geography"
        }}
        ]
        }}
        BAD Example (An Open-Ended Question):

        Input Text: "What aspect of Moroccan culture or adventure are you most excited to explore?"

        Explanation: This is an open-ended question asking for the user's opinion. It does not offer clickable choices.

        Correct Output:

        {{
        "suggestions": []
        }}
        Analyze the following text based on these rules. You must format your response as a valid JSON object.

        IMPORTANT THE QUESTION MUST BE OF THE SAME LANGUAGE AS THE INPUT TEXT.

        Text to analyze:
        "{text}"
        """
    )

    parser = JsonOutputParser(pydantic_object=Suggestions)
    chain = prompt | llm | parser
    return chain


suggestion_chain = create_suggestion_chain()


# --- API Endpoint ---

@app.get("/metrics")
async def metrics():
    """
    Exposes Prometheus metrics.
    """
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")


@app.post("/generate-suggestions/", response_model=Suggestions)
async def generate_suggestions_endpoint(input_data: SuggestionRequestInput):
    """
    Receives text and context IDs, logs the request, gets suggestions,
    updates the log, and returns the response.
    """
    suggestion_request_id = str(uuid.uuid4())
    request_id_var.set(suggestion_request_id)
    original_request_id_var.set(input_data.original_request_id)

    logger.info(f"INPUT RECEIVED")
    await log_suggestion_request(log_collection, suggestion_request_id, input_data)

    try:
        response_data = await suggestion_chain.ainvoke({"text": input_data.text})
        logger.info(f"Generated Suggestions")
        logger.debug(f"Suggestions: {response_data}")

        await update_suggestion_log(log_collection, suggestion_request_id, response_data)

        return response_data
    except Exception as e:
        logger.error(f"An error occurred while generating suggestions for {suggestion_request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate suggestions."
        )