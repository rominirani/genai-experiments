import datetime
import json
from google.cloud.logging import logger

def extract_gemini_payload(response, prompt, uri_path, mime_type, generation_config,
                           safety_settings,prompt_token_count,time, prompt_tag, prompt_note, prompt_uuid,
                           query_cost):
  """Extracts relevant payload from a Gemini API response."""
  payload = {
      "uuid": prompt_uuid,
      "timestamp": datetime.datetime.now(),
      "prompt_tag": prompt_tag,
      "prompt_note": prompt_note,
      "apx_cost_dollar": float(query_cost),
      "input_prompt": prompt,  # Assuming you have access to the original prompt
      "gcs_path": uri_path,  # If applicable
      "mime_type": mime_type,  # If applicable
      "max_output_tokens": int(generation_config['max_output_tokens']),
      "temperature": generation_config['temperature'],
      "top_p": float(generation_config['top_p']),
      "top_k": float(generation_config['top_k']),
      "input_prompt_token_count": int(prompt_token_count),
      "model_output": response.text,
      "prompt_token_count": int(response.usage_metadata.prompt_token_count),
      "candidates_token_count": int(response.usage_metadata.candidates_token_count),
      "total_token_count": int(response.usage_metadata.total_token_count),
      "prompt_feedback": str(response.prompt_feedback),
      "total_processing_time_sec": float(time),
      "finish_reason": str(response.candidates[0].finish_reason),
      "input_safety_settings": str(safety_settings),
      "output_safety_rating": str(response.candidates[0].safety_ratings)
  }

  return payload

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

# Defining main function
def main():
    payload = extract_gemini_payload(responses, prompt, uri_path, mime_type, generation_config,
                           safety_settings,prompt_token_count,processing_time, prompt_tag, prompt_note, prompt_uuid, cost_of_query)

    write_entry("gemini_app_log",payload)
    print("Payload written to log")
    
if __name__=="__main__":
    main()
