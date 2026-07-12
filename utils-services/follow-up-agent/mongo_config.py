from datetime import datetime, timezone
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class SuggestionRequestInput(BaseModel):
    text: str
    session_id: str
    original_request_id: str

# --- Logging Helper Functions ---
async def log_suggestion_request(collection, request_id: str, input_data: SuggestionRequestInput):
    """Asynchronously logs the initial incoming suggestion request."""
    if collection is None:
        return
    try:
        log_document = {
            'request_id': request_id,
            'session_id': input_data.session_id,
            'original_request_id': input_data.original_request_id,
            'input_text': input_data.text,
            'timestamp_utc': datetime.now(timezone.utc),
            'generated_suggestions_response': None,
        }
        await collection.insert_one(log_document)
        logger.info(f"Logged initial request to MongoDB.")
    except Exception as e:
        logger.error(f"Error logging initial suggestion request: {e}")


async def update_suggestion_log(collection, request_id: str, response_data: dict):
    """
    Asynchronously updates the log with the generated suggestions.
    Accepts a dict directly, as this is what LangChain returns.
    """
    if collection is None:
        return
    try:
        await collection.update_one(
            {'request_id': request_id},
            {'$set': {
                'generated_suggestions_response': response_data.get('suggestions'),
                'response_timestamp_utc': datetime.now(timezone.utc)
            }}
        )
        logger.info(f"Updated log with parsed response and metadata.")
    except Exception as e:
        # This is where the error was being reported from.
        logger.error(f"Error updating suggestion log: {e}")