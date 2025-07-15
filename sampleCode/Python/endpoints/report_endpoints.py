from endpoints.api_endpoints import ApiEndpoint
from endpoints.endpoints_root import EndpointsHelper
from models.report_models import ImpactResultsExportRequest
from utilities.json_helper import JsonHelper


class ReportEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)


    def detailed_economic_indicators(self, impact_run_id: int) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/results/ExportDetailEconomicIndicators/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def summary_economic_indicators(self, impact_run_id: int) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/results/SummaryEconomicIndicators/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def detailed_taxes(self, impact_run_id: int) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/results/DetailedTaxes/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv

    def summary_taxes(self, impact_run_id: int) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/results/SummaryTaxes/{impact_run_id}"

        # No Payload

        # Send the request
        content: bytes = self.rest_helper.get(url)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv


    def estimated_growth_percentage(self, impact_run_id: int, export_request: ImpactResultsExportRequest) -> str:
        # Resolve the endpoint's URL
        url: str = f"{self.base_url}/api/v1/impact/results/EstimatedGrowthPercentage/{impact_run_id}"

        # Attach the payload
        filter_json: str = JsonHelper.serialize(export_request)

        # Send the request
        content: bytes = self.rest_helper.get(url, body=filter_json)

        # The response is a CSV of the report
        report_csv = str(content)
        return report_csv