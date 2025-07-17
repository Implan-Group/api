from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from models.enums import EventType
from models.specification import Specification
from utilities.json_helper import JsonHelper


class DataEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def get_aggregation_schemes(self, industry_set_id: int | None = None) -> list[AggregationScheme]:
        """
        :param industry_set_id:
        :returns:
        """
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/aggregationSchemes"
        # If we have an industry set id, filter with it
        params = {}
        if industry_set_id:
            params["industrySetId"] = industry_set_id
        # Send our request
        content: bytes = self.rest_helper.get(url, query_params=params)
        # Translate that back into a list of Aggregation Schemes
        agg_schemes: list[AggregationScheme] = JsonHelper.deserialize_list(content, AggregationScheme)
        return agg_schemes

    def get_datasets(self, aggregation_scheme_id: int):
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/datasets/{aggregation_scheme_id}"
        # Send our request, expecting json
        content: bytes = self.rest_helper.get(url)
        # Map to Datasets
        datasets: list[Dataset] = JsonHelper.deserialize_list(content, Dataset)
        return datasets

    def get_specifications(self, project_id: UUID, event_type: EventType) -> list[Specification]:
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/eventtype/{event_type}/specification"
        content: bytes = self.rest_helper.get(url)
        specifications: list[Specification] = JsonHelper.deserialize_list(content, Specification)
        return specifications
