import requests
from requests.exceptions import HTTPError
import logging

class ImplanAuthentication:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class Authentication:
    @staticmethod
    def get_bearer_token(auth):
        url = "https://api.implan.com/beta/auth"
        headers = {"Content-Type": "application/json"}
        data = {
            "username": auth.username,
            "password": auth.password
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
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

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

