import json
from typing import Optional

import requests
import logging

from datetime import datetime, timedelta
from requests import Session, Request, PreparedRequest, Response
from requests.auth import AuthBase

from implan_logging import LoggingHelper


class BearerTokenAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request


class RestHelper:
    BASE_URL = "https://api.implan.com/"

    @staticmethod
    def get_response_json(response: Response):
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            return None

    def __init__(self, base_url: Optional[str] = None):
        self.base_url: str = base_url or self.BASE_URL
        self.auth: BearerTokenAuth = BearerTokenAuth("BAD_TOKEN")
        self.session: Session = requests.session()
        self.session.headers.update({"Accept": "application/json"})
        self.timeout_sec: int = 60

    def validate_token(self) -> bool:
        # noinspection PyBroadException
        try:
            self.send_request('GET', 'api/v1/region/RegionTypes')
            return True
        except:
            return False

    def set_bearer_token(self, bearer_token: str):
        self.auth = BearerTokenAuth(bearer_token)
        self.session.auth = self.auth
        # test the token by hitting a small endpoint
        valid: bool = self.validate_token()
        if not valid:
            print("The specified Bearer Token is invalid")
            raise RuntimeError("Invalid Bearer Token")

    def send_request(self, method: str, url: str, data=None, json_data=None) -> Response:
        url = self.base_url + url

        start: datetime = datetime.now()

        try:
            request: Request = Request(method, url, data=data, json=json_data)
        except Exception as e:
            logging.error(f"Could not create Request `{method} to {url}`: {e}")
            raise

        try:
            prepped: PreparedRequest = self.session.prepare_request(request)
        except Exception as e:
            logging.error(f"Could not prepare Request `{request}`: {e}")
            raise

        try:
            response: Response = self.session.send(prepped, timeout=self.timeout_sec)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Could not send Request `{request}`: {e}")
            raise

        end: datetime = datetime.now()
        elapsed: timedelta = end - start

        LoggingHelper.log_request_response(self.session, request, response, elapsed_time=elapsed.total_seconds(),
                                           response_data=None, response_data_type=None)

        return response

    def get(self, url: str) -> Response:
        return self.send_request('GET', url)

    def post(self, url: str) -> Response:
        return self.send_request('POST', url)
