import requests
import logging

from requests.exceptions import HTTPError

# This class hold onto the username and password used for Authentication
class ImplanAuthentication:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# This class retrieves a Bearer Token from a valid ImplanAuthentication
class Authentication:
    @staticmethod
    def get_bearer_token(auth):
        url = "https://api.implan.com/auth"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "username": auth.username,
            "password": auth.password
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status() # will raise any errors caught during the request
            token = response.text
            if not token:
                raise HTTPError("Cannot currently authenticate to Impact Api")
            return token
        except HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Other error occurred: {err}")
            raise