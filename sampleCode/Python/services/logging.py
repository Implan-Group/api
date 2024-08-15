import os
import sys
import json
import requests
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Type
from requests.models import Request, Response

class Logging:
    _log_file_path = None

    @staticmethod
    def initialize_logging():
        # Ensure that the Console can display all UTF8 characters
        sys.stdout.reconfigure(encoding='utf-8')

        # Start with the directory we're executing from
        dir_path = Path(__file__).resolve().parent
        # We want to be in the same root as the /bin/ directory
        try:
            bin_index = str(dir_path).index('/bin')
            dir_path = dir_path[:bin_index]
        except ValueError:
            pass

        log_dir = os.path.join(dir_path, "logs")
        
        # Ensure that directory exists so that we can write log files to it
        os.makedirs(log_dir, exist_ok=True)

        # Log file uses the day's timestamp
        file_name = f"Log_{datetime.datetime.now():%Y%m%d}.txt"
        Logging._log_file_path = os.path.join(log_dir, file_name)

    @staticmethod
    def log_request_response(client: requests.Session, request: Request, response: Response, response_data: Optional[Any], elapsed_time: float, response_data_type: Optional[Type] = None):
        log = []

        # Timestamp header
        log.append("-------------")
        log.append(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}]")

        # Request
        method = request.method.upper()
        log.append(f"Request: {method} '{request.url}'")
        
        for key, value in request.headers.items():
            if key.lower() == "authorization":
                continue
            log.append(f"-H {key} {value}")

        if request.body:
            log.append(f"-Body: '{request.headers.get('Content-Type')}'")
            body_content = json.dumps(request.body, indent=2)
            log.append(body_content)

        # Response
        log.append(f"Response: '{response.status_code} {response.reason}' in {elapsed_time:.1f}ms")

        # Failed?
        if not response.ok or response.text or response.content:
            if response.text:
                log.append(f"-Error Message: {response.text}")
            if response.content:
                log.append(f"-Content: '{response.headers.get('Content-Type')}'")
                if response_data_type:
                    log.append(f" as {response_data_type.__name__}")
                else:
                    log.append('')
                
                if response_data:
                    response_json = json.dumps(response_data, indent=2)
                    log.append(response_json)
                else:
                    log.append(response.content.decode('utf-8'))

        # Final empty line
        log.append("")

        log_message = "\n".join(log)

        # Write the final log to the Console
        print(log_message)

        # Append to the log file
        with open(Logging._log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "\n")

# Ensure logging is initialized at the start
Logging.initialize_logging()
