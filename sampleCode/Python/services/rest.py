import requests
from requests.auth import AuthBase
import json
import logging
from datetime import datetime
from time import time
from functools import wraps

class BearerAuth(AuthBase):
    """Custom authentication class for bearer token."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

class RestClient:
    BASE_URL = "https://api.implan.com/beta/"
    
    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL
        self.auth = BearerAuth("BAD_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self.timeout = 60  # Timeout in seconds

    def set_authentication(self, bearer_token):
        self.auth = BearerAuth(bearer_token)
        self.session.auth = self.auth
        try:
            # Test the authentication by hitting a small endpoint
            self.get_region_types()
        except Exception as ex:
            raise Exception("Invalid Bearer Token", ex)

    def _handle_response(self, response):
        if not response.ok:
            try:
                error_data = response.json()
            except ValueError:
                error_data = response.text
            logging.error(f"Error Response: {error_data}")
            response.raise_for_status()
        return response

    def request(self, method, url, **kwargs):
        url = self.base_url + url
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            self._handle_response(response)
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, data=None, json_data=None, **kwargs):
        return self.request("POST", url, data=data, json=json_data, **kwargs)

    def get_response_content(self, response):
        return response.text

    def get_response_data(self, response, data_type=None):
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return None

    def get_region_types(self):
        response = self.get("api/v1/region/RegionTypes")
        return self.get_response_data(response)
