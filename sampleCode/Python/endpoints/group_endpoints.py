import uuid

from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.group_models import Group
from utilities.json_helper import JsonHelper


class GroupEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def add_group_to_project(self,
                             project_guid: uuid.UUID,
                             group: Group) -> Group:
        # Hydrate the endpoint url
        url: str = f"{self.base_url}/api/v1/impact/project/{project_guid}/group"

        # Transform the group into our json payload
        payload: str = JsonHelper.serialize(group)
        
        # Send our POST request
        content: bytes = self.rest_helper.post(url, body=payload)

        # The response will be the fully hydrated Group
        group: Group = JsonHelper.deserialize(content, Group)

        return group