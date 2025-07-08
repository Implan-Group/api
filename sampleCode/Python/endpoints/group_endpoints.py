from http import HTTPMethod

import requests
import logging
import uuid

from endpoints.api_endpoints import ApiEndpoint
from endpoints.endpoints_root import EndpointsHelper
from models.group_models import Group
from services.json_helper import JsonHelper
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class GroupEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def add_group_to_project(self,
                             project_guid: uuid.UUID,
                             group: Group) -> Group:
        # Hydrate the endpoint url
        url: str = f"{self.base_url}/api/v1/impact/project/{project_guid}/group"

        # Transform the group into our json payload
        payload: str = JsonHelper.serialize(group)
        
        # Send our POST request
        content: bytes = self.rest_helper.send_http_request(HTTPMethod.POST, url, data=payload)

        # The response will be the fully hydrated Group
        group: Group = JsonHelper.deserialize(content, Group)

        return group