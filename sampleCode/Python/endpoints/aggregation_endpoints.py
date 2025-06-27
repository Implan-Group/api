from http import HTTPMethod

from endpoints.endpoints_root import EndpointsHelper
from endpoints.api_endpoints import ApiEndpoint
from models.aggregation_scheme import AggregationScheme
from services.json_helper import JsonHelper


class AggregationSchemeEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

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
        # Send our request, expecting json
        aggregation_schemes_json = self.rest_helper.send_http_request(HTTPMethod.GET, url, params=params)
        # Translate that back into a list of Aggregation Schemes
        agg_schemes: list[AggregationScheme] = JsonHelper.deserialize_list(aggregation_schemes_json, AggregationScheme)
        return agg_schemes
