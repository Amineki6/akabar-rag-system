# --- 1. Imports ---
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import redis

from dotenv import load_dotenv
import redis
import time

from logging_config import setup_logging
from mongo_config import log_report
import logging
import httpx

setup_logging()
logger = logging.getLogger(__name__)

# --- 2. Configuration and App Setup ---
load_dotenv()


class TokenBuffer:
    """Handles streaming token buffering with special code pattern detection"""
    
    def __init__(self):
        self.buffer = ''
        self.displayed_text = ''
        self.code_patterns = [
            re.compile(r'!audio\{[^}]*\}'),
            re.compile(r'!\s*conversion\s*\{.*?\}', re.DOTALL),
            re.compile(r'!\s*loc\s*\{[^}]*\}')
        ]
    
    def reset(self):
        self.buffer = ''
        self.displayed_text = ''
    
    def add_token(self, token: str) -> str:
        self.buffer += token
        return self.get_safe_display_text()
    
    def get_full_text(self) -> str:
        return self.buffer
    
    def is_conversion_code_complete(self, text: str, start_index: int) -> tuple[bool, int]:
        substring = text[start_index:]
        conversion_match = re.match(r'!\s*conversion\s*(\{)', substring)
        if not conversion_match:
            return False, -1
        
        json_start_index = start_index + conversion_match.start(1)
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(json_start_index, len(text)):
            char = text[i]
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"':
                in_string = not in_string
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return True, i + 1
        return False, -1

    def get_safe_display_text(self) -> str:
        safe_text = self.buffer
        buffer_needed = False
        complete_code_ending_patterns = [
            re.compile(r'(!audio\{[^}]*\})\s*$'),
            re.compile(r'(!\s*loc\s*\{[^}]*\})\s*$')
        ]
        
        for pattern in complete_code_ending_patterns:
            match = pattern.search(safe_text)
            if match:
                safe_text = safe_text[:match.end(1)]
                buffer_needed = True
                break
        
        if not buffer_needed:
            conv_starts = list(re.finditer(r'!\s*conversion\s*\{', safe_text))
            if conv_starts:
                is_complete, end_index = self.is_conversion_code_complete(safe_text, conv_starts[-1].start())
                if is_complete:
                    trailing_text = safe_text[end_index:]
                    if trailing_text and trailing_text.isspace():
                        safe_text = safe_text[:end_index]
                        buffer_needed = True

        if not buffer_needed:
            conversion_starts = list(re.finditer(r'!\s*conversion\s*\{', safe_text))
            if conversion_starts:
                is_complete, _ = self.is_conversion_code_complete(safe_text, conversion_starts[-1].start())
                if not is_complete:
                    safe_text = safe_text[:conversion_starts[-1].start()]
                    buffer_needed = True

        if not buffer_needed:
            partial_patterns = [
                re.compile(r'!audio\{[^}]*$'),
                re.compile(r'!\s*loc\s*\{[^}]*$'),
                re.compile(r'!audio$'),
                re.compile(r'!\s*conversion$'),
                re.compile(r'!\s*loc$'),
                re.compile(r'!$')
            ]

            for pattern in partial_patterns:
                match = pattern.search(safe_text)
                if match:
                    safe_text = safe_text[:match.start()]
                    break

        new_text = safe_text[len(self.displayed_text):]
        self.displayed_text = safe_text
        return new_text


class WeatherService:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self._weather_data = None
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

    def get_weather_for_city(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetches and simplifies weather data for a specific city from the Redis cache.

        Args:
            self: The instance of the class, expected to have a 'redis_client' attribute.
            city: The name of the city to look up.

        Returns:
            A dictionary with simplified weather data, or None if the city is not found
            or if there is a Redis error.
        """
        # Handle the special case where 'morocco' should default to 'rabat'
        city_key = 'rabat' if city.lower() == 'morocco' else city.lower()
        
        # Construct the key used to store the city's data in Redis
        redis_key = f"weather:{city_key}"

        try:
            # Fetch the JSON string data from Redis using the key
            data_json = self.redis_client.get(redis_key)

            # If the key doesn't exist in Redis, .get() returns None
            if not data_json:
                return None
            
            # Parse the retrieved JSON string into a Python dictionary
            city_data = json.loads(data_json)
            
            # Create the simplified dictionary from the full data set
            simplified_weather = {
                "name": city_data["location"]["name"],
                "temp_c": city_data["current"]["temp_c"],
                "condition": city_data["current"]["condition"]
            }
            
            return simplified_weather

        except redis.exceptions.RedisError as e:
            # Handle potential Redis connection errors or other issues
            logger.error(f"Error reading from Redis: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            # Handle cases where the data in Redis is malformed or missing expected keys
            logger.error(f"Error processing cached data for {city}: {e}")
            return None


class AudioTitleService:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        """
        Initializes the service and the connection to Redis.
        """
        # The 'decode_responses=True' argument makes redis-py return strings instead of bytes
        self._redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self._titles: Optional[Dict[str, str]] = None

    def load_audio_titles(self) -> Dict[str, str]:
        """
        Retrieves audio titles from the in-memory cache or fetches them from Redis.

        Returns:
            A dictionary of audio titles. Returns an empty dictionary if the data
            is not in Redis or if a connection cannot be established.
        """
        # Return from cache if already loaded
        if self._titles is not None:
            return self._titles
        
        try:
            # 1. Fetch the JSON string from Redis
            REDIS_KEY = 'audio_titles'
            titles_json = self._redis_client.get(REDIS_KEY)

            # 2. Check if the key exists and parse the JSON
            if titles_json:
                self._titles = json.loads(titles_json)
                logger.info(f"Successfully loaded and cached {len(self._titles)} titles from Redis.")
            else:
                # Handle case where the key doesn't exist in Redis
                logger.warning(f"Warning: Audio titles key '{REDIS_KEY}' not found in Redis.")
                self._titles = {}

        except redis.exceptions.ConnectionError as e:
            logger.error(f"Error connecting to Redis: {e}")
            self._titles = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from Redis key '{REDIS_KEY}': {e}")
            self._titles = {}
            
        return self._titles


class TextProcessor:
    @staticmethod
    def extract_conversion_data(text: str) -> List[Dict[str, Any]]:
        conversion_regex = re.compile(r'!\s*conversion\s*(\{\{.*?\}\}|\{.*?\})', re.DOTALL)
        conversions = []
        for match in conversion_regex.finditer(text):
            try:
                json_string = match.group(1).strip()
                if json_string.startswith('{{') and json_string.endswith('}}'):
                    json_string = json_string[1:-1]
                conversions.append(json.loads(json_string))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse conversion JSON: {e}")
        return conversions
    
    @staticmethod
    def clean_text_for_display(text: str) -> str:
        text = re.sub(r'\s*!\s*loc\s*\{[^}]+\}', '', text)
        text = re.sub(r'!\s*conversion\s*(\{\{.*?\}\}|\{.*?\})', '', text, flags=re.DOTALL)
        return text
    
    @staticmethod
    def extract_audio_codes(text: str) -> List[str]:
        audio_regex = re.compile(r'!audio\{([^}]+)\}')
        return [match.group(1) for match in audio_regex.finditer(text)]
    
    @staticmethod
    def should_generate_suggestions(text: str) -> Tuple[bool, Optional[str]]:
        clean_text = TextProcessor.clean_text_for_display(text)
        sentences = re.findall(r'[^.!?؟]+[.!?؟]+', clean_text)
        
        if not sentences:
            return (False, None)
            
        last_sentence = sentences[-1].strip()
        
        is_question = last_sentence.endswith('?') or last_sentence.endswith('؟')
        
        if is_question:
            return (True, last_sentence)
        else:
            return (False, None)
        


class SuggestionService:
    def __init__(self, followup_hostname: str = "127.0.0.1"):
        self.follow_up_api_url = f"http://{followup_hostname}:8000/generate-suggestions/"
    
    async def _generate_suggestions_logic(self, last_sentence: str, session_id: str, original_request_id: str) -> Dict[str, Any]:
        """Generate suggestions based on the last sentence of a conversation."""
        if not last_sentence:
            logger.warning("No final sentence found to generate suggestions.")
            return {"suggestions": []}

        
        payload = {"text": last_sentence, "session_id": session_id, "original_request_id": original_request_id}
        logger.info(f"Calling Follow-Up API")
        logger.debug(f"Follow-Up API payload: {payload}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.follow_up_api_url, json=payload, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"An error occurred while calling the suggestion API: {e}")
            return {"suggestions": []}
        except httpx.HTTPStatusError as e:
            logger.error(f"Suggestion API returned an error: {e.response.status_code} - {e.response.text}")
            return {"suggestions": []}
        

class StreamingService:
    def __init__(self, agent_hostname: str = "127.0.0.1", followup_hostname: str = "127.0.0.1"):
        self.rag_api_url = f"http://{agent_hostname}:5005/chat"
        self.suggestion_service = SuggestionService(followup_hostname)
        self.text_processor = TextProcessor()
    

    async def stream_rag_response(
        self, 
        message: str, 
        session_id: str, 
        request_id: str, 
        mode: str,
        circuit: str | None,
        weather_service: WeatherService,
        audio_service: AudioTitleService,
        master_locations: Dict[str, Any]
    ):
        """
        Enhanced streaming function with real-time business logic and final logging.
        Logs the exact data yielded to the client.
        """
        payload = {"message": message, "session_id": session_id, "original_request_id": request_id, "mode": mode, "circuit": circuit}
        logger.info(f"Forwarding request to Agent API")
        logger.debug(f"Agent API payload: {payload}")

        token_buffer = TokenBuffer()
        original_request_id, current_session_id = None, None
        pending_weather_event, weather_event_sent = None, False
        pending_conversions = []
        location_tags = []
        final_suggestions = None

        # --- EDITED: Variables to capture yielded data for final logging ---
        yielded_text_parts = []
        yielded_audio_data = []
        yielded_weather_data = None
        final_compiled_locations = []
        # --- END EDIT ---

        audio_titles = audio_service.load_audio_titles()
        mid_stream_code_pattern = re.compile(r'(!audio\{[^}]*\}|!\s*loc\s*\{[^}]*\})')
        processed_token_streaming_duration = None
        suggestion_generation_duration = None

        logger.info("Connecting to Agent API for streaming response...")
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.rag_api_url, json=payload, timeout=60) as response:
                    response.raise_for_status()
                    logger.info("Connection to Agent API successful")
                    logger.info("Streaming response from Agent API")

                    start_time = time.perf_counter()
                    async for line in response.aiter_lines():
                        if not line or not line.strip():
                            continue
                        try:
                            event = json.loads(line.strip())
                            
                            if event['type'] == 'context':
                                original_request_id, current_session_id = event['data'].get('original_request_id'), event['data'].get('session_id')
                                event_data = json.loads(line)
                                if 'session_id' in event_data.get('data', {}):
                                    del event_data['data']['session_id']
                                modified_line = json.dumps(event_data)
                                yield modified_line + '\n'                            
                            elif event['type'] == 'metadata':
                                identified_city = event['data'].get('city', "rabat").lower()

                                if identified_city and not weather_event_sent:
                                    weather_data = weather_service.get_weather_for_city(identified_city)
                                    if weather_data:
                                        pending_weather_event = {'type': 'weather', 'data': weather_data}
                            
                            elif event['type'] == 'token':
                                safe_text_chunk = token_buffer.add_token(event['data'])
                                if safe_text_chunk:
                                    parts = mid_stream_code_pattern.split(safe_text_chunk)
                                    for part in parts:
                                        if not part: continue

                                        audio_match = re.fullmatch(r'!audio\{([^}]+)\}', part)
                                        conversion_match = re.fullmatch(r'!conversion\{(.+)\}', part, re.DOTALL)
                                        loc_match = re.fullmatch(r'!loc\{([^}]+)\}', part)

                                        if audio_match:
                                            code = audio_match.group(1)
                                            audio_payload = {'code': code, 'title': audio_titles.get(code, 'Unknown Title'), 'src': f'/playlist/{code}.mp3'}
                                            
                                            # --- EDITED: Capture data before yielding ---
                                            yielded_audio_data.append(audio_payload)
                                            yield json.dumps({'type': 'audio_data', 'data': [audio_payload]}) + '\n'
                                        
                                        elif conversion_match:
                                            json_data_string = conversion_match.group(1)
                                            try:
                                                # This part remains the same as pending_conversions already captures the final data
                                                pending_conversions.append(json.loads(json_data_string))
                                            except json.JSONDecodeError:
                                                pass

                                        elif loc_match:
                                            location_tags.append(loc_match.group(1))
                                        
                                        else:
                                            # --- EDITED: Capture data before yielding ---
                                            yielded_text_parts.append(part)
                                            yield json.dumps({'type': 'processed_token', 'data': part}) + '\n'
                                            
                                            if pending_weather_event and not weather_event_sent:
                                                # --- EDITED: Capture data before yielding ---
                                                yielded_weather_data = pending_weather_event['data']
                                                yield json.dumps(pending_weather_event) + '\n'
                                                pending_weather_event, weather_event_sent = None, True
                            
                            elif event['type'] == 'end':
                                logger.info("End of token streaming")
                                # Yielding final structured data blocks
                                if pending_conversions:
                                    yield json.dumps({'type': 'conversions', 'data': pending_conversions}) + '\n'
                                
                                if location_tags:
                                    compiled_locations = [loc for loc in [master_locations.get(tag) for tag in location_tags] if loc is not None]
                                    if compiled_locations:
                                        # --- EDITED: Capture data before yielding ---
                                        final_compiled_locations = compiled_locations
                                        logger.debug(f"Yielding map data for locations: {compiled_locations}")
                                        yield json.dumps({'type': 'map_data', 'data': {'locations': compiled_locations}}) + '\n'
                                
                                end_time = time.perf_counter()
                                processed_token_streaming_duration = (end_time - start_time) * 1000
                                logger.debug(f"Total streaming duration: {processed_token_streaming_duration:.2f} ms")

                                is_question, last_sentence = self.text_processor.should_generate_suggestions(token_buffer.get_full_text())

                                if is_question and current_session_id and original_request_id:
                                    start_time = time.perf_counter()
                                    suggestions_data = await self.suggestion_service._generate_suggestions_logic(last_sentence, current_session_id, original_request_id)
                                    end_time = time.perf_counter()
                                    suggestion_generation_duration = (end_time - start_time) * 1000
                                    logger.debug(f"Suggestion generation took {suggestion_generation_duration:.2f} ms")
                                    final_suggestions = suggestions_data 

                                    logger.debug(f"Yielding suggestions: {suggestions_data}")
                                    yield json.dumps({'type': 'suggestions', 'data': suggestions_data}) + '\n'
                                    
                                yield line + '\n'
                            
                            else:
                                yield line + '\n'
                        except json.JSONDecodeError as e:
                            logger.error(f"ERROR: Failed to parse JSON: {line}, Error: {e}")
                            yield line + '\n'
                            
        except Exception as e:
            logger.error(f"ERROR: Exception in stream_rag_response: {e}")
            error_event = {"type": "error", "data": "An internal error occurred."}
            yield json.dumps(error_event) + '\n'
        finally:
            # --- EDITED: Final logging now uses the captured yielded data ---
            final_display_text = "".join(yielded_text_parts)

            final_log_data = {
                'clean_response_text': final_display_text,
                'generated_events': {
                    'audio_data': yielded_audio_data,
                    'weather_data': yielded_weather_data,
                    'conversions': pending_conversions,
                    'locations': final_compiled_locations,
                    'suggestions': final_suggestions
                },
                'metrics': {
                    'processed_token_streaming_duration': processed_token_streaming_duration,
                    'suggestion_generation_duration': suggestion_generation_duration if final_suggestions else None
                }
            }

            yield final_log_data


class ReportService:
    @staticmethod
    def log_report_to_db(report_collection, request_id: str, session_id: str, report_data: Dict[str, Any]) -> None:
        """Log a report to the database using the existing mongo_config function."""
        log_report(
            reports_collection=report_collection,
            request_id=request_id,
            session_id=session_id,
            report_data=report_data
        )