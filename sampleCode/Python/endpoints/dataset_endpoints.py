from http import HTTPMethod

from endpoints.api_endpoints import ApiEndpoint
from endpoints.endpoints_root import EndpointsHelper
from models.dataset_models import Dataset
from services.json_helper import JsonHelper


class DatasetEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def get_datasets(self, aggregation_scheme_id: int):
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/datasets/{aggregation_scheme_id}"
        # Send our request, expecting json
        dataset_json = self.rest_helper.send_http_request(HTTPMethod.GET, url)
        # Map to Datasets
        datasets: list[Dataset] = JsonHelper.deserialize_list(dataset_json, Dataset)
        return datasets