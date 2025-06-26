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


    def get(self,
            url: str,
            return_type: AnyResponseType,
            headers: dict[str, Any] | None = None,
            query_params: dict[str, Any] | None = None,
            body: str | Any | None = None,
            ) -> AnyResponseType:

        response = self._send(HTTPMethod.GET, url, headers, query_params, body)
        if return_type is str:
            response.encoding="utf-8"
            return response.text
        if return_type is Any:
            response.encoding = "utf-8"
            json_text = response.text
            JsonHelper.deserialize(json_text, return_type)


