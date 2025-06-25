import http
from email.headerregistry import ContentTypeHeader

import requests
import logging

from typing import Any
from datetime import datetime, timedelta
from requests import Session, Request, PreparedRequest, Response
from services.logging_helper import LoggingHelper


class RestHelper:
    BASE_URL = "https://api.implan.com/"

    def __init__(self, token: str, logging_helper: LoggingHelper, base_url: str | None = None):
        self.token = token
        self.logging_helper = logging_helper
        self.base_url: str = base_url or self.BASE_URL


    def get_session(self) -> requests.Session:
        """
        Gets an authorized HTTP Session
        """
        # Create the session
        session = requests.sessions.Session()
        # Set the authorization
        session.headers["Authorization"] = self.token
        return session

    def send_http_request(self,
                          http_method: http.HTTPMethod,
                          url: str,
                          params: dict[str, Any] | None = None,
                          data: Any | None = None,
                          json_data: str | None = None) -> Any:
        """
        Send an HTTP Request to an api endpoint
        :param http_method:
        :param url:
        :param params:
        :param data:
        :param json_data:
        :return:
        """

        # The relative url was passed in, we need the absolute url
        url = self.base_url + url
        # Get the starting time (so we know how long this entire process takes)
        start: datetime = datetime.now()

        # Start a new HTTP Session
        with self.get_session() as session:

            # Try to create the request
            try:
                request: Request = Request(method=http_method, url=url, params=params, data=data, json=json_data)
            except Exception as ex:
                logging.error(f"Could not create a {http_method} Request to {url}: {ex}")
                raise

            # Use the session to Prepare it
            try:
                prepared_request: PreparedRequest = session.prepare_request(request)
            except Exception as ex:
                logging.error(f"Could not prepare Request `{request}`: {ex}")
                raise

            # Send the Request
            try:
                response: Response = session.send(prepared_request, timeout=self.timeout_sec)
            except Exception as ex:
                logging.error(f"Could not send Request `{request}`: {ex}")
                raise

            # If it is not a 200 OK, log and raise an error
            if response.status_code != http.HTTPStatus.OK:
                logging.warning(f"Response `{response}` was not a 200 OK")
                response.raise_for_status()

            # Get the ending + total time taken
            end: datetime = datetime.now()
            elapsed_time: timedelta = end - start

            # Log this
            self.logging_helper.log_request_response(prepared_request, response, elapsed_time)

            # Return the response body
            response_content_type = response.headers.get("Content-Type")

            if response_content_type == "json":
                return response.json()

            if response_content_type == "text":
                return response.text

            return response

    def send_get_request(self,
                         url: str,
                         data: Any | None = None,
                         json_data: str | None = None) -> Any:
        return self.send_http_request(http.HTTPMethod.GET, url, data, json_data)

    def send_post_request(self,
                          url: str,
                          data: Any | None = None,
                          json_data: str | None = None) -> Any:
        return self.send_http_request(http.HTTPMethod.POST, url, data, json_data)

    def send_put_request(self,
                         url: str,
                         data: Any | None = None,
                         json_data: str | None = None) -> Any:
        return self.send_http_request(http.HTTPMethod.PUT, url, data, json_data)
