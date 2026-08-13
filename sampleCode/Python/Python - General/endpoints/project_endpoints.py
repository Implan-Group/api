from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.project_models import Project
from utilities.json_helper import JsonHelper


class ProjectEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to Projects
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def create_project(self, project: Project) -> Project:
        """
        Create a new Project and return it
        :param project: The initial Project definition
        :returns: The fully-hydrated, newly-created Project
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project"

        # Convert the Project to json
        project_json: str = JsonHelper.serialize(project)

        # Send the request and get the returned content
        content = self.rest_helper.post(url, body=project_json)

        # Translate the content into the hydrated Project
        hydrated_project: Project = JsonHelper.deserialize(content, Project)
        return hydrated_project

    def get_project(self, project_id: UUID) -> Project:
        """
        Get an existing Project's Information
        :param project_id: The Project's Identifier
        :returns: The Project with the given identifier
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the hydrated Project
        project: Project = JsonHelper.deserialize(content, Project)
        return project

    def get_all_projects(self) -> list[Project]:
        """
        Returns all Projects created by the current User
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the hydrated Project
        projects: list[Project] = JsonHelper.deserialize_list(content, Project)
        return projects

    def get_shared_projects(self) -> list[Project]:
        """
        Returns all Projects shared with (but not originally created by) the current User
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/shared"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the hydrated Project
        projects: list[Project] = JsonHelper.deserialize_list(content, Project)
        return projects
