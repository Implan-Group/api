import logging

from endpoints.Authentication import ImplanAuthentication, Authentication

# This Workflow example shows off how to send in your IMPLAN Username and Password and retrieve the Bearer Token that
# needs to included with all other Requests to the ImpactApi

class AuthenticationWorkflow:
    @staticmethod
    def get_bearer_token():
        # You need to fill in your own IMPLAN Username and Password below
        auth = ImplanAuthentication(
            username="",
            password=""
        )
       
        # Retrieve the token
        bearer_token = Authentication.get_bearer_token(auth)
        logging.info(f"Retrieved Bearer Token: {bearer_token}")

        # Extract the actual token if it has "Bearer" prefix
        if bearer_token.startswith("Bearer "):
            bearer_token = bearer_token[len("Bearer "):]

        # Return the bearer token for use in other workflows
        return bearer_token