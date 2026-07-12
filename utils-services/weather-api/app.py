import os
import json
import requests
import threading
import redis
from flask import Flask, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration ---
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
# Maps your desired city name (key) to the name the API expects (value)
CITIES_MAPPING = {
    "chefchaoune": "chaouen",
    "agadir": "agadir",
    "casablanca": "casablanca",
    "marrakech": "marrakech",
    "ouarzazate": "ouarzazate",
    "rabat": "rabat",
    "tangier": "tangier",
    "fez": "fez",
    "essaouira": "essaouira",
    "taroudant": "taroudant",
    "dakhla": "dakhla",
    "tafraout": "tafraout",
    "tiznit": "tiznit"
}

# --- Redis Configuration ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_KEY_EXPIRY = 5400  # 1.5 hours

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# --- Redis Client Initialization ---
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    print("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Error: Could not connect to Redis. Please ensure it's running. Details: {e}")
    redis_client = None

def update_weather_data():
    """
    Fetches fresh weather data using API-specific names and stores it in Redis
    using desired display names.
    """
    if not redis_client:
        print("Cannot update weather data: Redis client is not connected.")
        return

    print(f"[{threading.current_thread().name}] Starting weather data update...")

    # Iterate over the mapping dictionary
    for display_name, api_name in CITIES_MAPPING.items():
        api_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={api_name}"
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Use the desired display_name for the Redis key, e.g., "weather:chefchaouen"
            redis_key = f"weather:{display_name.lower()}"
            json_data = json.dumps(data)

            redis_client.setex(redis_key, REDIS_KEY_EXPIRY, json_data)
            print(f"Successfully fetched for '{api_name}' and cached as '{display_name}' in Redis.")

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {api_name}: {e}")
        except redis.exceptions.RedisError as e:
            print(f"Failed to write data for {display_name} to Redis: {e}")

    print("Weather data update cycle finished.")

# --- API Endpoint ---
@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Serves the cached weather data by fetching it from Redis using display names.
    """
    if not redis_client:
        return jsonify({"error": "Service is unavailable: Cannot connect to data store."}), 503

    all_weather_data = {}
    try:
        # Create a list of Redis keys using the desired display names (the dict keys)
        redis_keys = [f"weather:{city.lower()}" for city in CITIES_MAPPING.keys()]
        
        results = redis_client.mget(redis_keys)

        # Reconstruct the dictionary using your desired display names
        for city, data_json in zip(CITIES_MAPPING.keys(), results):
            if data_json:
                all_weather_data[city] = json.loads(data_json)

        if not all_weather_data or len(all_weather_data) != len(CITIES_MAPPING):
            return jsonify({"error": "Weather data is not fully populated yet. Please try again in a moment."}), 404

        return jsonify(all_weather_data)

    except redis.exceptions.RedisError as e:
        print(f"Error reading from Redis: {e}")
        return jsonify({"error": "An error occurred while retrieving weather data."}), 500

if __name__ == '__main__':
    # --- Scheduler Setup ---
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(update_weather_data, 'interval', hours=1)
    scheduler.start()

    # --- Initial Data Fetch ---
    print("Triggering initial weather data fetch...")
    initial_fetch_thread = threading.Thread(target=update_weather_data)
    initial_fetch_thread.start()

    # --- Start Flask App ---
    app.run(host='0.0.0.0', port=5055, debug=False)