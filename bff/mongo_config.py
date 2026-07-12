import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
from quart import Request
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def initialize_mongodb():
    """
    Establishes a connection to MongoDB and returns the collections for requests and reports.
    
    Returns:
        tuple: A tuple containing (requests_collection, reports_collection), or (None, None) if connection fails.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        logger.warning("MONGO_URI environment variable not set. Logging to MongoDB is disabled.")
        return None, None ### MODIFIED ###
    
    try:
        logger.info("Connecting to MongoDB for logging...")
        mongo_client = AsyncIOMotorClient(mongo_uri)
        mongo_client.admin.command('ismaster') # Check connection
        db = mongo_client['chat_logs']
        
        ### MODIFIED ###
        # Get both collections
        requests_collection = db['bff_requests']
        reports_collection = db['reports'] # New collection for reports
        
        logger.info("Successfully connected to MongoDB.")
        return requests_collection, reports_collection # Return a tuple of collections
    
    except Exception as e:
        logger.error(f"Could not connect to MongoDB. Logging will be disabled. Error: {e}")
        return None, None
    
    

def log_initial_request(collection, request_id, session_id, user_input, source, fastapi_request: Request):
    """
    Logs the initial incoming request details to MongoDB.
    
    Args:
        collection (pymongo.collection.Collection): The MongoDB collection to log to.
        request_id (str): The unique ID for the request.
        session_id (str): The session ID from the client.
        user_input (str): The user's message.
        fastapi_request (Request): The FastAPI request object to get client info.
    """
    if collection is None:
        return # Do nothing if MongoDB is not connected

    try:
        log_document = {
            'request_id': request_id,
            'session_id': session_id,
            'user_input': user_input,
            'timestamp_utc': datetime.now(timezone.utc),
            'source': source,
            'payload': None, # To be filled in later
            'metrics': None # To be filled in later
        }
        collection.insert_one(log_document)
        logger.info(f"Logged initial request to MongoDB.")
    except Exception as e:
        logger.error(f"An error occurred while logging initial request to MongoDB: {e}")

def update_final_log(collection, request_id, final_response_data, metrics=None):
    """
    Updates the MongoDB log with the final processed response from the BFF.
    
    Args:
        collection (pymongo.collection.Collection): The MongoDB collection.
        request_id (str): The unique ID of the request to update.
        final_response_data (dict): A dictionary containing the final processed data.
    """
    if collection is None:
        return # Do nothing if MongoDB is not connected

    try:
        collection.update_one(
            {'request_id': request_id},
            {'$set': {
                'payload': final_response_data,
                'response_timestamp_utc': datetime.now(timezone.utc),
                'metrics': metrics
            }}
        )
        logger.info(f"Updated log with parsed response and metadata.")
    except Exception as e:
        logger.error(f"Failed to update log with final response: {e}")

def log_report(reports_collection, request_id: str, session_id: str, report_data: dict):
    """
    Inserts a new report document into the dedicated reports collection.

    Args:
        reports_collection: The MongoDB collection instance for reports.
        request_id: The ID of the original request being reported.
        report_data: A dictionary containing the report details.
    """
    if reports_collection is None:
        logger.warning("Reports collection is not available. Skipping report logging.")
        return

    try:
        # Create a full new document for the report
        report_document = {
            "request_id": request_id, # Link back to the original request
            "reason": report_data.get("reason"),
            "sessionId": session_id,
            "reported_at": datetime.now(timezone.utc)
        }
        
        # Insert the new report document into the 'bff_reports' collection
        reports_collection.insert_one(report_document)
        logger.info(f"Successfully logged report for request_id: {request_id}")

    except Exception as e:
        logger.error(f"Failed to log report for request_id {request_id}: {e}")