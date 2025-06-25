import os
import sys
import datetime
import logging
import json

from datetime import timedelta
from requests import PreparedRequest
from requests.models import Request, Response


class LoggingHelper:

    def __init__(self):
        # Configure logging to show all messages INFO severity or higher with a specific format
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # Ensure that the Console can display all UTF8 characters
        sys.stdout.reconfigure(encoding='utf-8')
        # We're going to be logging to local files in a logs directory
        self.log_directory = os.path.join(os.getcwd(), "logs")
        # Ensure that directory exists
        if not os.path.exists(self.log_directory):
            os.mkdir(self.log_directory)
        # Create the file name (changes each day)
        file_name = f"Log_{datetime.datetime.now():%Y%m%d}.txt"
        self.log_path = os.path.join(self.log_directory, file_name)


    def log_request_response(self,
                             request: PreparedRequest,
                             response: Response,
                             elapsed_time: timedelta):
        message: list[str] = []

        # Header
        message.append("--------")
        message.append(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}]")

        # Request Information
        message.append(f"{request.method} Request to {request.url}")
        # Log the headers
        if len(request.headers) > 1:    # There will always be at least an Authorization Header
            for key, value in request.headers.items():
                # Do not print the auth header
                if key.lower() == "authorization":
                    continue
                message.append(f"  {key}: {value}")
        # If we sent a payload with the request, log it
        if request.body:
            message.append(f"{request.headers.get("Content-Type")} Body:")
            message.append(json.dumps(request.body, indent=2))

        # Response Information
        message.append(f"Response {response.status_code} {response.reason} in {elapsed_time:.1f}ms")

        # Failed?
        if not response.ok:
            message.append(f"Failed: {response.text}")
        # Success!
        else:
            message.append(f"{response.headers.get("Content-Type")} Body:")
            message.append(json.dumps(response.content, indent=2))

        # Turn the messages into a log
        msg = "\r\n".join(message)
        # Write this log message to the console
        logging.info(msg)
        # Append in the log file
        with open(self.log_path, "a", encoding="utf-8") as file:
            file.write(msg + "\r\n")  # With an extra newline for readability