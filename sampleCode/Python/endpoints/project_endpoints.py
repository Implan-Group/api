from uuid import UUID

from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.project_models import Project
from utilities.json_helper import JsonHelper


class ProjectEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def create_project(self, project: Project) -> Project:

        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/impact/project"

        # Turn our Project into json
        project_json = JsonHelper.serialize(project)

        # Send the request
        content = self.rest_helper.post(url, body=project_json)

        # Deserialize
        output = JsonHelper.deserialize(content, Project)
        return output

    def get_project(self, project_id: UUID) -> Project | None:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # Deserialize the response
        project: Project | None = JsonHelper.deserialize(content, Project)

        return project

    def get_all_projects(self) -> list[Project]:
        """
        Returns all Projects created by the current User
        """

        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/project"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # Deserialize the response
        projects: list[Project] = JsonHelper.deserialize_list(content, Project)

        return projects


    def get_shared_projects(self) -> list[Project]:
        """
        Returns all Projects shared with (but not originally created by) the current User
        """

        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/project/shared"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # Deserialize the response
        projects: list[Project] = JsonHelper.deserialize_list(content, Project)

        return projects