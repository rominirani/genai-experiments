import datetime
import json
from google.cloud.logging import logger

def write_entry(logger_name, log_payload):
    """Writes log entries to the given logger."""

    logger_client = logger.Client()
    logger = logger_client.logger(logger_name)

    # Convert datetime objects to strings before logging
    for key, value in log_payload.items():
        if isinstance(value, datetime.datetime):
            log_payload[key] = value.isoformat()

    # Struct log. The struct can be any JSON-serializable dictionary.
    logger.log_struct(
        log_payload,
        severity="INFO",
    )
