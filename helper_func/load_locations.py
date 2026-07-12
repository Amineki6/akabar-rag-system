import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))

# Connect to your local Redis instance
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    print("Successfully connected to Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    exit(1)

# Define the key we will use in Redis
REDIS_KEY = 'locations'

# Load the JSON data from the file
try:
    with open('locations.json', 'r') as f:
        locations_data = json.load(f)
except FileNotFoundError:
    print("Error: locations.json not found in the current directory.")
    exit(1)

# Convert the Python dictionary to a JSON string
json_string = json.dumps(locations_data)

# Store the JSON string in Redis
r.set(REDIS_KEY, json_string)

print(f"Data from locations.json has been loaded into Redis under the key '{REDIS_KEY}'.")