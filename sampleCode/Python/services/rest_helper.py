import http
from http import HTTPMethod, HTTPStatus

import requests
import logging

from typing import Any
from datetime import datetime, timedelta
from requests import Request, PreparedRequest, Response

from services.auth_helper import AuthHelper
from services.logging_helper import LoggingHelper
from utilities.prelude import JsonHelper


class RestHelper:
    def __init__(self, token: str, logging_helper: LoggingHelper, base_url: str | None = None):
        self.token = token
        self.logging_helper = logging_helper
        self.timeout_sec: float = 30.0
        self.auth: AuthHelper = AuthHelper()

    def _refresh_token(self):
        self.token = self.auth.get_fresh_token()

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
              json_body: str | None = None,
              data_body: Any | None = None,
              ) -> Response:
        # Time this process for logging and debugging
        start: datetime = datetime.now()

        # Start a new HTTP session
        with self._get_session() as session:

            # Create the request
            request: Request
            try:
                request = Request(http_method, url,
                                  headers=headers,
                                  params=query_params,
                                  json=json_body,
                                  data=data_body,
                                  )
            except Exception as ex:
                logging.error(f"Unable to create a {http_method} Request to {url}: {ex}")
                raise

            # Use the Session to prepare it
            prepped: PreparedRequest
            try:
                prepped= session.prepare_request(request)
            except Exception as ex:
                logging.error(f"Unable to prepare '{request}': {ex}")
                raise

            # Send the Request (with timeout)
            response: Response
            try:
                response = session.send(prepped, timeout=self.timeout_sec)
            except requests.Timeout as timeout_ex:
                logging.warn(f"Timed out attempting to send to {url}: {timeout_ex}")
                raise
            except Exception as ex:
                logging.error(f"Unable to send '{prepped}': {ex}")
                raise

            # End timing
            end: datetime = datetime.now()
            total: timedelta = end - start

            # Log this
            self.logging_helper.log_request_response(prepped, response, total)

            # It is possible that the auth token has expired
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                # In this case, we'll get a new bearer token
                self._refresh_token()
                # And then

            # raise an error for non-200 status codes
            if response.status_code != 200:
                logging.error(f"Response Failed - {response.status_code} - {response}")
                response.raise_for_status()

            # return the response
            return response

    def get(self,
            url: str,
            headers: dict[str, Any] | None = None,
            query_params: dict[str, Any] | None = None,
            body: str | Any | None = None,
            ) -> bytes:
        response: Response = self._send(HTTPMethod.GET, url, headers, query_params, body)
        return response.content

    def post(self,
             url: str,
             headers: dict[str, Any] | None = None,
             query_params: dict[str, Any] | None = None,
             body: str | Any | None = None,
             ) -> bytes:
        response: Response = self._send(HTTPMethod.POST, url, headers, query_params, body)
        return response.content

    def put(self,
            url: str,
            headers: dict[str, Any] | None = None,
            query_params: dict[str, Any] | None = None,
            body: str | Any | None = None,
            ) -> bytes:
        response: Response = self._send(HTTPMethod.PUT, url, headers, query_params, body)
        return response.content

    def delete(self,
               url: str,
               headers: dict[str, Any] | None = None,
               query_params: dict[str, Any] | None = None,
               body: str | Any | None = None,
               ) -> bytes:
        response: Response = self._send(HTTPMethod.DELETE, url, headers, query_params, body)
        return response.content

    def patch(self,
              url: str,
              headers: dict[str, Any] | None = None,
              query_params: dict[str, Any] | None = None,
              body: str | Any | None = None,
              ) -> bytes:
        response: Response = self._send(HTTPMethod.PATCH, url, headers, query_params, body)
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
