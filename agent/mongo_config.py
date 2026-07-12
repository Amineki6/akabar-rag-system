import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from quart import request

# 1. Get a logger instance for this module
logger = logging.getLogger(__name__)

load_dotenv()

async def initialize_mongodb():
    """
    Establishes a connection to the MongoDB database using the MONGO_URI from environment variables.
    
    Returns:
        pymongo.collection.Collection or None: The collection object for logging, or None if connection fails.
    """
    mongo_user = os.getenv("MONGO_USER")
    mongo_password = os.getenv("MONGO_PASSWORD")
    if not mongo_user or not mongo_password:
        logger.warning("MONGO_USER or MONGO_PASSWORD environment variable not set. Logging to MongoDB is disabled.")
        return None
    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@mongo:27017/maindb?authSource=admin"
    try:
        # 2. Replaced print with logger.info
        logger.info("Connecting to MongoDB...")
        mongo_client = AsyncIOMotorClient(mongo_uri)
        mongo_client.admin.command('ismaster') # Check connection
        db = mongo_client['chat_logs']
        collection = db['chat_requests']
        logger.info("Successfully connected to MongoDB.")
        return collection
    except Exception as e:
        # 2. Replaced print with logger.error, adding exc_info for the full traceback
        logger.error(f"Could not connect to MongoDB. Logging will be disabled. Error: {e}", exc_info=True)
        return None

# --- 4. Logging Helper Functions ---

async def log_initial_request(collection, request_id, session_id, original_request_id, user_input, mode, circuit):
    """
    Logs the initial incoming request details to MongoDB.
    
    Args:
        collection (pymongo.collection.Collection): The MongoDB collection to log to.
        request_id (str): The unique ID for the request.
        session_id (str): The session ID from the client.
        original_request_id (str): The original request ID from the client.
        user_input (str): The user's message.
    """
    if collection is None:
        return

    try:
        log_document = {
            'request_id': request_id,
            'session_id': session_id,
            'original_request_id': original_request_id,
            'user_input': user_input,
            'mode': mode,
            'circuit': circuit,
            'timestamp_utc': datetime.now(timezone.utc),
            'user_agent': request.headers.get('User-Agent'),
            'model_response': None,
            'metadata': None,
            'response_metrics': None,
        }

        await collection.insert_one(log_document)
        # 2. Replaced print with logger.info
        logger.info(f"Logged initial request to MongoDB.")
    except Exception as e:
        # 2. Replaced print with logger.error
        logger.error(f"An error occurred while logging initial request to MongoDB: {e}", exc_info=True)

async def update_final_log(collection, request_id, response_text, metadata, response_metrics = None):
    """
    Updates the MongoDB log with the final response and metadata.
    
    Args:
        collection (pymongo.collection.Collection): The MongoDB collection.
        request_id (str): The unique ID of the request to update.
        response_text (str): The complete, clean text of the model's response.
        metadata (dict): The metadata object received from the stream.
    """
    if collection is None:
        return

    try:
        await collection.update_one(
            {'request_id': request_id},
            {'$set': {
                'model_response': response_text,
                'metadata': metadata,
                'response_metrics': response_metrics,
                'response_timestamp_utc': datetime.now(timezone.utc)
            }}
        )

        logger.info(f"Updated log with parsed response and metadata.")
    except Exception as e:
        logger.error(f"Failed to update log with parsed response: {e}", exc_info=True)