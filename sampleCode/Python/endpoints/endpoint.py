from http import HTTPMethod

from models.aggregation_scheme import AggregationScheme
from services.json_helper import JsonHelper
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class Endpoints:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url = base_url or "https://api.implan.com"

        self.aggregation_schemes = AggregationSchemeEndpoints(self)


class AggregationSchemeEndpoints(Endpoints):
    def __init__(self, endpoints: Endpoints):
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
        aggregation_schemes: list[AggregationScheme] = JsonHelper.deserialize(aggregation_schemes_json, AggregationScheme)