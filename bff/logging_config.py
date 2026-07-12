import logging
import os
from contextvars import ContextVar
from pythonjsonlogger.json import JsonFormatter


# 1. Create a ContextVar to hold the request ID.
#    The default 'None' will be used for logs outside a request context (e.g., at startup).
request_id_var = ContextVar('request_id', default='None')


# 2. Create a custom logging Filter
class RequestIdFilter(logging.Filter):
    """
    A logging filter that injects the request_id and original_request_id 
    from their context variables.
    """
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

# 3. Create a setup function to configure the logger
def setup_logging():
    log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    format_choice = os.getenv('LOG_FORMAT', 'json').lower()
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) 

    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # --- Now, add your own custom handler ---
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    
    if format_choice == 'json':
        # Use the JSON formatter
        formatter = JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            rename_fields={
                'asctime': 'timestamp',
                'levelname': 'level',
                'name': 'logger_name'
            }
        )
    else:
        # Use the plain text formatter
        formatter = logging.Formatter(
            '[%(asctime)s] - [%(levelname)s] - [%(name)s] - [rid:%(request_id)s] - %(message)s'
        )

    # Tell the filter to add fields that the formatter can find
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            record.request_id = request_id_var.get()
            return True

    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())
    
    if not logger.handlers:
        logger.addHandler(handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)