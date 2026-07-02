import requests
import logging

from http import HTTPMethod, HTTPStatus
from typing import Any
from datetime import datetime, timedelta
from requests import Request, PreparedRequest, Response
from utilities.auth_helper import AuthHelper
from utilities.logging_helper import LoggingHelper


class RestHelper:
    """
    A utility for making REST calls
    """

    def __init__(self, logging_helper: LoggingHelper, base_url: str | None = None):
        self.logging_helper = logging_helper
        self.timeout_sec: float = 30.0
        self.auth: AuthHelper = AuthHelper()
        self.token = self.auth.get_bearer_token()

    def _refresh_token(self):
        """
        Refresh the existing token
        """
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
              body: str | Any | None = None,
              ) -> Response:
        """
        The base implementation for preparing, sending, retrieving, and understanding REST communication
        :param http_method: The HTTP Method that will be used for the request
        :param url: The absolute path to the API Endpoint
        :param headers: Optional additional headers to attach to the request
        :param query_params: Optional additional query parameters to attach to the request
        :param body: An optional body to attach to the request
        """

        # Time this process for logging and debugging
        start: datetime = datetime.now()

        if body is not None:
            # A string is json
            if isinstance(body, str):
                if headers is None:
                    headers = {}
                headers['Content-Type'] = 'application/json'
            else:
                print('debug')

        # Start a new HTTP session
        with self._get_session() as session:

            # Create the request
            request: Request
            try:
                request = Request(http_method, url,
                                  headers=headers,
                                  params=query_params,
                                  data=body,
                                  )
            except Exception as ex:
                logging.error(f"Unable to create a {http_method} Request to {url}: {ex}", exc_info=True)
                raise ex

            # Use the Session to prepare it
            prepped: PreparedRequest
            try:
                prepped = session.prepare_request(request)
            except Exception as ex:
                logging.error(f"Unable to prepare '{request}': {ex}", exc_info=True)
                raise ex

            # Send the Request (with timeout)
            response: Response
            try:
                response = session.send(prepped, timeout=self.timeout_sec)
            except requests.Timeout as timeout_ex:
                logging.warn(f"Timed out attempting to send to {url}: {timeout_ex}")
                raise timeout_ex
            except Exception as ex:
                logging.error(f"Unable to send '{prepped}': {ex}", exc_info=True)
                raise ex

            # End timing
            end: datetime = datetime.now()
            total: timedelta = end - start

            # Log this
            self.logging_helper.log_request_response(prepped, response, total)

            # It is possible that the auth token has expired
            if response.status_code == HTTPStatus.UNAUTHORIZED.value:
                print('DEBUG')
                # TODO: Add a system for re-authenticating and retrying this HTTP Request

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
        """
        Send a GET Request and receive the returned content bytes
        """
        response: Response = self._send(HTTPMethod.GET, url, headers, query_params, body)
        return response.content

    def post(self,
             url: str,
             headers: dict[str, Any] | None = None,
             query_params: dict[str, Any] | None = None,
             body: str | Any | None = None,
             ) -> bytes:
        """
        Send a POST Request and receive the returned content bytes
        """
        response: Response = self._send(HTTPMethod.POST, url, headers, query_params, body)
        return response.content

    def put(self,
            url: str,
            headers: dict[str, Any] | None = None,
            query_params: dict[str, Any] | None = None,
            body: str | Any | None = None,
            ) -> bytes:
        """
        Send a PUT Request and receive the returned content bytes
        """
        response: Response = self._send(HTTPMethod.PUT, url, headers, query_params, body)
        return response.content

    def delete(self,
               url: str,
               headers: dict[str, Any] | None = None,
               query_params: dict[str, Any] | None = None,
               body: str | Any | None = None,
               ) -> bytes:
        """
        Send a DELETE Request and receive the returned content bytes
        """
        response: Response = self._send(HTTPMethod.DELETE, url, headers, query_params, body)
        return response.content

    def patch(self,
              url: str,
              headers: dict[str, Any] | None = None,
              query_params: dict[str, Any] | None = None,
              body: str | Any | None = None,
              ) -> bytes:
        """
        Send a PATCH Request and receive the returned content bytes
        """
        response: Response = self._send(HTTPMethod.PATCH, url, headers, query_params, body)
        return response.content
