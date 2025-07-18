from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.group_models import Group
from utilities.json_helper import JsonHelper


class GroupEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to Groups
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def add_group_to_project(self,
                             project_id: UUID,
                             group: Group) -> Group:
        """
        Adds a new Group to an Existing Project
        :param project_id: The uuid for the Project to add the Group to
        :param group: The defined Group to add
        :returns: The fully-hydrated Group that has been added to the Project
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/group"

        # Convert the Group to json
        group_json: str = JsonHelper.serialize(group)

        # Send the request and get the returned content
        content: bytes = self.rest_helper.post(url, body=group_json)

        # Translate the content into the hydrated Group
        group: Group = JsonHelper.deserialize(content, Group)
        return group
