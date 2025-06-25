import logging
import os.path
import requests

class ImplanAuth:
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
        self.token = None
        self.token_path = "bearer.jwt"

    def validate_token(self) -> bool:
        """
        This method validates whether our stored JWT Bearer Token is valid
        """
        # noinspection PyBroadException

        try:
            # Hit a small endpoint
            url = f"{self.base_url}/api/v1/region/RegionTypes"
            headers = {"Authorization": self.token}
            response = requests.get(url, headers=headers)
            # We do not care about the response's content, only its Status
            response.raise_for_status()
            return True
        except:
            # Any error of any kind indicates failure
            return False


    def get_bearer_token(self) -> str | None:
        """
        Gets a valid JWT Bearer Token that must be used for all Endpoint Requests
        :return: A string containing "Bearer {token}"

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication
        """

        # The JWT Bearer Token we're going to return
        token: str

        # First, verify if we have a stored token
        if os.path.exists(self.token_path):
            # If the path exists, load the contents as our token
            with open(self.token_path, "r", encoding="utf-8") as file:
                token = file.read()
            # Verify the token is still valid by hitting one of the smallest endpoints
            url = f"{self.base_url}/api/v1/region/RegionTypes"
            headers = {"Authorization": token}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # This token is still valid
                logging.info("Authenticated to Implan Impact API")
                return token
            logging.info(f"Stored token is invalid, retrieving a new one...")

        # We must retrieve a new token

        # The Implan API auth endpoint
        url = f"{self.base_url}/auth"
        # Body contains the username + password
        body = {
            "username": self.username,
            "password": self.password
        }

        # Send the request
        response = requests.post(url, json=body)
        # If we got a 200 OK, this is a valid token
        if response.status_code == 200:
            # Save this token for re-use
            response.encoding = "utf-8"
            token = response.text
            with open(self.token_path, "w", encoding="utf-8") as file:
                file.write(token)
            # Then return it
            logging.info("Authenticated to Implan Impact API")
            return token

        # Something is wrong
        logging.error(f"Could not Authenticate to the Implan Impact API: Service unavailable or username or password are incorrect")
        return None