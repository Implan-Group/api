from http import HTTPMethod

from endpoints.api_endpoints import ApiEndpoint
from endpoints.endpoints_root import EndpointsHelper
from models.project_models import Project
from services.json_helper import JsonHelper


class ProjectEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def create(self, project: Project) -> Project:
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/impact/project"
        # Turn our Project into json
        project_json = JsonHelper.serialize(project)
        # Send the request
        content = self.rest_helper.send_http_request(HTTPMethod.POST, url, data=project_json)
        # Deserialize
        output = JsonHelper.deserialize(content, Project)
        return output
