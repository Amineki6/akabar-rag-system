import json
import redis
from typing import Dict
import os
from dotenv import load_dotenv
load_dotenv()
# --- Configuration ---
AUDIO_TITLES_PATH = 'titles.txt'
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_KEY = 'audio_titles'

def parse_titles_file(file_path: str) -> Dict[str, str]:
    """Parses the text file into a dictionary."""
    titles = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and ' : ' in line:
                    parts = line.split(' : ', 1)
                    if len(parts) == 2:
                        code, title = parts[0].strip(), parts[1].strip()
                        titles[code] = title
    except FileNotFoundError:
        print(f"Error: Audio titles file not found at {file_path}")
        return {}
    return titles

def load_titles_to_redis():
    """
    Parses the titles file, converts it to JSON, and stores it in Redis.
    """
    # 1. Parse the source file into a Python dictionary
    titles_dict = parse_titles_file(AUDIO_TITLES_PATH)
    if not titles_dict:
        print("No titles to load. Exiting.")
        return

    # 2. Serialize the dictionary to a JSON string
    titles_json = json.dumps(titles_dict, indent=2)

    try:
        # 3. Connect to Redis and set the key
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.set(REDIS_KEY, titles_json)
        print(f"Successfully loaded {len(titles_dict)} titles into Redis key '{REDIS_KEY}'.")
    except redis.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}. Details: {e}")

if __name__ == '__main__':
    # To run this script, save the provided text content as 'titles.txt'
    # in the same directory, then execute 'python load_to_redis.py'
    load_titles_to_redis()