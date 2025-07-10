import http
from email.headerregistry import ContentTypeHeader
from http import HTTPMethod

import requests
import logging

from typing import Any, TypeVar, Type
from datetime import datetime, timedelta
from requests import Session, Request, PreparedRequest, Response

from services.json_helper import JsonHelper
from services.logging_helper import LoggingHelper


class RestHelper:
    def __init__(self, token: str, logging_helper: LoggingHelper, base_url: str | None = None):
        self.token = token
        self.logging_helper = logging_helper
        self.timeout_sec: float = 30.0

    def _get_session(self) -> requests.Session:
        """
        Gets an authorized HTTP Session
        """
        # Create the session
        session = requests.sessions.Session()
        # Set the authorization
        session.headers["Authorization"] = self.token
        return session

    def _send(self,
              http_method: HTTPMethod,
              url: str,
              headers: dict[str, Any] | None = None,
              query_params: dict[str, Any] | None = None,
              body: str | Any | None = None,
              ) -> Response:
        # Time this process for logging and debugging
        start: datetime = datetime.now()

        # Start a new HTTP session
        with self._get_session() as session:
            # Create the request
            request: Request = Request(http_method, url, headers=headers, params=query_params)
            # Prepare it with our session
            prepped: PreparedRequest = session.prepare_request(request)

            # If body is a string, treat it as raw json
            if body is str:
                prepped.headers["Content-Type"] = "application/json"
                prepped.body = body

            # If body is Any, jsonify it
            if body is Any:
                prepped.headers["Content-Type"] = "application/json"
                prepped.body = JsonHelper.serialize(body)

            # Send the Request
            response: Response = session.send(prepped, timeout=self.timeout_sec)

            # End timing
            end: datetime = datetime.now()
            total: timedelta = end - start

            # Log this
            self.logging_helper.log_request_response(prepped, response, total)

            # raise an error for non-200 status codes
            response.raise_for_status()

            # return the response
            return response

    # Used for generic typing for response deserialization
    AnyResponseType = TypeVar('AnyResponseType', None, str, Any)
    T = TypeVar('T')

    def get(self,
            url: str,
            return_type: Type[T],
            headers: dict[str, Any] | None = None,
            query_params: dict[str, Any] | None = None,
            body: str | Any | None = None,
            ) -> AnyResponseType:

        response = self._send(HTTPMethod.GET, url, headers, query_params, body)

        if return_type is str:
            response.encoding = "utf-8"
            return response.text

        if return_type is Any:
            response.encoding = "utf-8"
            json_text = response.text
            instance = JsonHelper.deserialize(json_text, return_type)
            return instance

        # Just return the bytes
        return response.content

    def send_http_request(self,
                          http_method: http.HTTPMethod,
                          url: str,
                          params: dict[str, Any] | None = None,
                          data: Any | None = None,
                          json_str: str | None = None) -> Any:
        """
        Send an HTTP Request to an api endpoint
        :param http_method:
        :param url:
        :param params:
        :param data:
        :param json_str:
        :return:
        """

        # Get the starting time (so we know how long this entire process takes)
        start: datetime = datetime.now()

        # Start a new HTTP Session
        with self._get_session() as session:

            # Try to create the request
            try:
                request: Request = Request(method=http_method, url=url, params=params, data=data, json=json_str)
            except Exception as ex:
                logging.error(f"Could not create a {http_method} Request to {url}: {ex}")
                raise

            # Ensure we've set the right content-type
            if data is not None or json_str is not None:
                request.headers["Content-Type"] = "application/json"

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
            # We know that the API endpoints all work in UTF8
            response.encoding = "utf-8"

            return response.content
