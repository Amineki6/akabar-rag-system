import os
import requests
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import json
import redis # Import the redis library
import logging

logger = logging.getLogger(__name__)
# --- Redis Configuration ---
# It's recommended to pull these from environment variables for flexibility
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_DURATION_SECONDS = 86400  # Cache duration remains 1 day

# Establish a connection to the Redis server
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    # Ping the server to check the connection
    redis_client.ping()
    logger.info("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    logger.warning(f"Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}. Caching will be disabled. Error: {e}")
    redis_client = None

def get_exchange_rate_api_key():
    """Fetches the API key from environment variables."""
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        raise ValueError("EXCHANGERATE_API_KEY not found in environment variables. Please add it to your .env file.")
    return api_key

class CurrencyConversionInput(BaseModel):
    """Input model for the currency converter tool."""
    amount: float = Field(description="The amount of money to convert.")
    base_currency: str = Field(description="The currency code to convert from (e.g., 'MAD', 'USD').")
    target_currency: str = Field(description="The currency code to convert to (e.g., 'EUR', 'GBP').")

@tool("currency_converter", args_schema=CurrencyConversionInput)
def currency_converter_tool(amount: float, base_currency: str, target_currency: str) -> str:
    """
    Use this tool ONLY when a user explicitly asks to convert a specific amount of money from one currency to another.
    """
    base_upper = base_currency.upper()
    target_upper = target_currency.upper()
    cache_key = f"exchange_rate:{base_upper}_TO_{target_upper}"
    
    # --- Check for a valid rate in the Redis cache first ---
    if redis_client:
        try:
            cached_rate_json = redis_client.get(cache_key)
            if cached_rate_json:
                cached_data = json.loads(cached_rate_json)
                cached_rate = cached_data['rate']
                converted_amount = amount * cached_rate
                output_data = {
                    "from_amount": amount,
                    "from_currency": base_upper,
                    "to_amount": round(converted_amount, 2),
                    "to_currency": target_upper,
                    "rate": cached_rate
                }
                return f"!conversion{{{json.dumps(output_data)}}}"
        except redis.exceptions.RedisError as e:
            logger.warning(f"Redis error during cache lookup: {e}. Proceeding without cache.")

    # --- If not in cache or Redis is unavailable, call the API ---
    try:
        api_key = get_exchange_rate_api_key()
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_upper}/{target_upper}/{amount}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if data.get("result") == "success":
            conversion_result = data.get("conversion_result")
            conversion_rate = data.get("conversion_rate")

            # Update and save the cache with the new rate using Redis
            if redis_client:
                try:
                    # Create the data payload to cache
                    cache_payload = json.dumps({"rate": conversion_rate})
                    # Set the key with an expiration time (TTL)
                    redis_client.setex(cache_key, CACHE_DURATION_SECONDS, cache_payload)
                except redis.exceptions.RedisError as e:
                    logger.warning(f"Could not save to Redis cache: {e}")

            output_data = {
                "from_amount": amount,
                "from_currency": base_upper,
                "to_amount": round(conversion_result, 2),
                "to_currency": target_upper,
                "rate": conversion_rate
            }
            return f"!conversion{{{json.dumps(output_data)}}}"
        else:
            error_type = data.get("error-type", "unknown error")
            return f"Error: Could not perform currency conversion. Reason: {error_type}"

    except requests.exceptions.RequestException as e:
        return f"Error: A network error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"