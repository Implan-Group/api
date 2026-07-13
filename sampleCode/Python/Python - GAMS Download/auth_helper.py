import logging
import os.path
import requests

from requests import Response


class AuthHelper:
    """
    This class contains the information needed to authorize to Implan's Impact API
    https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication
    """

    def __init__(self):
        """
        Upon init, we gather connection information from environment variables, with some sane defaults
        """
        self.username: str = os.getenv("IMPLAN_USERNAME")
        self.password: str = os.getenv("IMPLAN_PASSWORD")
        self.base_url: str = os.getenv("IMPLAN_API_URL") or "https://api.implan.com"
        self.token_path: str = os.getenv("IMPLAN_AUTH_TOKEN_PATH") or "implan_auth.jwt"


    def _validate_token(self, token: str) -> bool:
        """
        Validates whether a JWT token is still valid
        :param token: The full text of the jwt bearer token
        """

        if not token.startswith("Bearer "):
            token = f"Bearer {token}"

        try:
            # Send a request to a fast endpoint
            url = f"{self.base_url}/api/v1/region/RegionTypes"
            headers = {"Authorization": token}
            response = requests.get(url, headers=headers)
            # We do not care about the response's content, only that it was OK
            response.raise_for_status()
            return True
        except Exception as ex:
            # Any error of any kind indicates failure, but do not log anything that could be sensitive
            logging.debug(f"API Auth Token is Invalid")
            return False

    def get_fresh_token(self) -> str:
        """
        Gets a fresh (uncached) auth token
        """
        # The Implan API auth endpoint
        url = f"{self.base_url}/api/auth"
        # Body contains the username and password
        body = {
            "username": self.username,
            "password": self.password
        }

        # Send the request to the auth endpoint
        response: Response
        try:
            response = requests.post(url, json=body)
        except Exception as ex:
            logging.error(f"Unable to connect to Auth endpoint: {ex}")
            raise

        # 200 OK indicates a valid token
        if response.status_code == 200:
            # Save this token for re-use
            response.encoding = 'utf-8'
            token = response.text
            # Ensure the token starts with Bearer
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"
            # Save this token for re-use
            with open(self.token_path, "w", encoding="utf-8") as file:
                file.write(token)
            # Then return it
            logging.debug("Auth: Retrieved and Stored new Token")
            return token

        # 500 indicates the Auth service is temporarily unavailable.
        # This may occur if a user attempts to authenticate too many times in a row,
        # hence why we want to store and re-use the token.
        if response.status_code == 500:
            logging.warn("Auth: Implan Impact API Auth service is temporarily unavailable")
            raise Exception("Auth Service Unavailable")

        # Something else went wrong, log this and raise an error
        logging.error("Auth: Invalid username and/or password")
        response.raise_for_status()

        assert False, "unreachable"


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
            if self._validate_token(token):
                logging.debug("Auth: Stored Token is valid")
                return token
            logging.debug("Auth: Stored Token is invalid")

        # We do not
        return self.get_fresh_token()
