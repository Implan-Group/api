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
        bearer_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5EZzFRakpGUVRCRk1VUTVNVUl4TVVJNU9UaEJRekJDTlRsQk5rUkZPVU01UWprNE5EQTNOUSJ9.eyJzZXNzaW9uTGlmZXRpbWUiOjgsImlkbGVTZXNzaW9uTGlmZXRpbWUiOjgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL2VtYWlsYWRkcmVzcyI6InRpbW90aHkuamF5QGltcGxhbi5jb20iLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9naXZlbm5hbWUiOiJUaW1vdGh5IiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvc3VybmFtZSI6IkpheSIsImlzRXpQcm94eVVzZXIiOmZhbHNlLCJpc3MiOiJodHRwczovL2xvZ2luLmltcGxhbi5jb20vIiwic3ViIjoiYXV0aDB8NjRhZDlmOTM3OTlkMDA4ZDNlNjBkNWQ5IiwiYXVkIjpbImh0dHBzOi8vc2VydmljZXMuaW1wbGFuLmNvbSIsImh0dHBzOi8vaW1wbGFuLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3NDQ5OTAxOTYsImV4cCI6MTc0NTA3NjU5Niwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImF6cCI6InZkR2p5aFNNa3BOdlkwVXdYcTl6V0gzYWZMVnNSdEhiIn0.ZZflnKu24NsHUt7pwyu_WNsZcfLn06ygzQrXZBuWtGvpn9Qf4AtLTiOr52xq4hN0J4EQgzVBJ4dCnC_KAwxDRZjLaRbk5jvTp4wihNVQLubK_pECAW_x09QjTbAwxOZNnUT5by6K-gCakR-pQS-H6QdgSF_y0QDLI0agC9MsypMh-XRt8jnWVgzlM2Vcp9FX8XQGApJJkyNCWJmqrnlCOY9W1uUIeVSdFbAAhTWSR7jIYMCGVNO6cbWo-4XZWU0OCXnPWfobxXv9GvwqwxHtw9BbkumfvpNjp6flj3DKHNwXRTKrkoAX7u-T-voi9horNKobnZQ8emGfAayJXiL-mA"

        # bearer_token = Authentication.get_bearer_token(auth)
        # logging.info(f"Retrieved Bearer Token: {bearer_token}")

        # Extract the actual token if it has "Bearer" prefix
        if bearer_token.startswith("Bearer "):
            bearer_token = bearer_token[len("Bearer "):]

        # Return the bearer token for use in other workflows
        return bearer_token