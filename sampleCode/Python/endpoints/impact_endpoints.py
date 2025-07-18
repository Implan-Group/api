from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper


class ImpactEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to running, cancelling, and interrogating Impacts.
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def run_impact(self, project_id: UUID) -> int:
        """
        Starts the Impact Analysis for a given Project
        :param project_id: The uuid for the existing Project to Analyze
        :returns: The `Impact Run Id` that identifies this Impact
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/{project_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.post(url)

        # Translate the content into the Impact Run Id
        impact_run_id: int = int(content)
        return impact_run_id

    def get_impact_status(self, impact_run_id: int) -> str:
        """
        Returns the status of an Impact Run
        :param impact_run_id: The Impact Run Id from `run_impact`
        :returns: A string status for the Impact
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/status/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into status text
        status: str = str(content, 'utf-8')
        return status

    def cancel_impact(self, impact_run_id: int) -> str:
        """
        Cancel a running Impact analysis
        :param impact_run_id: The Impact Run Id from `run_impact`
        :returns: A string describing the cancellation status
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/cancel/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.put(url)

        # Translate the content into status text
        status: str = str(content, 'utf-8')
        return status
