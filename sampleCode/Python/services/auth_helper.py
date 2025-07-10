import logging
import os.path
from urllib.request import Request

import requests
from requests.auth import AuthBase


class AuthHelper:
    """
    This class contains the information needed to authorize to Implan's Impact API
    """

    def __init__(self, username: str, password: str):
        """
        Construct `ImplanAuth` by passing in your Implan Username and Password
        :param username: Your Implan Username
        :param password: Your Implan Password
        """
        self.username = username
        self.password = password
        self.base_url = "https://api.implan.com"
        self.token_path = "implan_auth.jwt"


    def validate_token(self, token: str) -> bool:
        """
        This method validates whether our stored JWT Bearer Token is valid
        """
        # noinspection PyBroadException

        try:
            # Hit a small endpoint
            url = f"{self.base_url}/api/v1/region/RegionTypes"
            headers = {"Authorization": token}
            response = requests.get(url, headers=headers)
            # We do not care about the response's content, only its Status
            response.raise_for_status()
            return True
        except:
            # Any error of any kind indicates failure
            return False


    def get_bearer_token(self) -> str:
        """
        Gets a valid JWT Bearer Token that must be used for all Endpoint Requests
        :return: A string containing "Bearer {token}"

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication
        """

        # The JWT Bearer Token we're going to return
        token: str

        # Check if we have a stored token
        if os.path.exists(self.token_path):
            # If the path exists, load the contents of that file as our token
            with open(self.token_path, "r", encoding="utf-8") as file:
                token = file.read()
            # Verify if this token is still valid
            if self.validate_token(token):
                logging.debug("Auth: Stored Token is valid")
                return token
            logging.debug("Auth: Stored Token is invalid")

        # We must retrieve a new token

        # The Implan API auth endpoint
        url = f"{self.base_url}/auth"
        # Body contains the specified username and password
        body = {
            "username": self.username,
            "password": self.password
        }

        # Send the request
        try:
            response = requests.post(url, json=body)
        except Exception as ex:
            print(ex)

        # If we got a 200 OK, this is a valid token
        if response.status_code == 200:
            # Save this token for re-use
            response.encoding = "utf-8"
            token = response.text
            with open(self.token_path, "w", encoding="utf-8") as file:
                file.write(token)
            # Then return it
            logging.debug("Auth: Retrieved and Stored new Token")
            return token

        # A 500 is service unavailable
        if response.status_code == 500:
            logging.warn("Auth: Implan Impact API Auth service is temporarily unavailable")
            raise Exception("Auth Service Unavailable")

        # Something else went wrong, log this and raise an error
        logging.error("Auth: Invalid username and/or password")
        response.raise_for_status()

        assert False, "unreachable"

class JWTAuth(AuthBase):
    """
    A custom AuthBase provider for the requests library that passed along a JWT Bearer Token
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, request: Request) -> Request:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request