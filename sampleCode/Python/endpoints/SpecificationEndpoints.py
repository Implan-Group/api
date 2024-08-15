import requests

class Specification:
    def __init__(self, name, code):
        self.name = name
        self.code = code

class SpecificationEndpoints:
    @staticmethod
    def get_specifications(project_id, event_type, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_id}/eventtype/{event_type}/specification"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            specifications = [Specification(**item) for item in response_data]
            return specifications
        else:
            response.raise_for_status()
