# authentication_workflow.py
from endpoints.authentication import ImplanAuthentication, Authentication
import logging
from workflows.iworkflow import IWorkflow

class AuthenticationWorkflow(IWorkflow):
    @staticmethod
    def examples():
        # Example Implan Authentication
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
