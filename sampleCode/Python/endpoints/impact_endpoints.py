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


class ImpactEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)


    def run_impact(self, project_id: uuid.UUID) -> int:
        """
        Runs the Impact Analysis for the given Project and returns the Analysis Run Id
        """

        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/{project_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.post(url)

        # The response is just the Impact's Run Id
        impact_run_id: int = int(content)
        return impact_run_id


    def get_impact_status(self, impact_run_id: int) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/status/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # The response is the status text
        status: str = str(content, 'utf-8')
        return status

    def cancel_impact(self, impact_run_id: int):
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/cancel/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.put(url)

        # The response contains information about the cancellation
        status: str = str(content, 'utf-8')
        return status