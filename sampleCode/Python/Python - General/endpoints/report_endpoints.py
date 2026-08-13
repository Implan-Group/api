from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.report_models import ImpactResultsExportRequest
from utilities.json_helper import JsonHelper


class ReportEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to retrieving Impact Results
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def detailed_economic_indicators(self, impact_run_id: int) -> str:
        """
        Get the Detailed Economic Indicators CSV Report
        :param impact_run_id: The Impact Run Id from the Project's Analysis
        :returns: A string containing the Detailed Economic Indicators CSV Report
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/results/ExportDetailEconomicIndicators/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def summary_economic_indicators(self, impact_run_id: int) -> str:
        """
        Get the Summary Economic Indicators CSV Report
        :param impact_run_id: The Impact Run Id from the Project's Analysis
        :returns: A string containing the Summary Economic Indicators CSV Report
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/results/SummaryEconomicIndicators/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def detailed_taxes(self, impact_run_id: int) -> str:
        """
        Get the Detailed Taxes CSV Report
        :param impact_run_id: The Impact Run Id from the Project's Analysis
        :returns: A string containing the Detailed Taxes CSV Report
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/results/DetailedTaxes/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def summary_taxes(self, impact_run_id: int) -> str:
        """
        Get the Summary Taxes CSV Report
        :param impact_run_id: The Impact Run Id from the Project's Analysis
        :returns: A string containing the Summary Taxes CSV Report
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/results/SummaryTaxes/{impact_run_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def estimated_growth_percentage(self, impact_run_id: int, export_request: ImpactResultsExportRequest) -> str:
        """
        Get the Estimated Growth Percentage CSV Report
        :param impact_run_id: The Impact Run Id from the Project's Analysis
        :param export_request: Additional filters that will be applied to generate the Report
        :returns: A string containing the Estimated Growth Percentage CSV Report
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/results/EstimatedGrowthPercentage/{impact_run_id}"

        # Convert the ImpactResultsExportRequest filters into a json body
        filter_json: str = JsonHelper.serialize(export_request)

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url, body=filter_json)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv
