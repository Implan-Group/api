from http import HTTPMethod

from endpoints.api_endpoints import ApiEndpoint
from endpoints.endpoints_root import EndpointsHelper
from models.industry_models import IndustrySet, IndustryCode
from services.json_helper import JsonHelper


class IndustryEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def get_industry_sets(self) -> list[IndustrySet]:
        # The endpoint's url
        url: str = f"{self.base_url}/api/v1/industry-sets"

        # GET that url's content -- a json array of IndustrySets
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url)

        # Deserialize the content
        industry_sets: list[IndustrySet] = JsonHelper.deserialize_list(content, IndustrySet)

        return industry_sets

    def get_industry_set(self, industry_set_id: int) -> IndustrySet | None:
        # The endpoint's url
        url: str = f"{self.base_url}/api/v1/industry-sets/{industry_set_id}"

        # GET that url's content -- a json IndustrySet
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url)

        # Deserialize the content
        industry_set: IndustrySet = JsonHelper.deserialize(content, IndustrySet)

        return industry_set

    def get_industry_codes(self,
                           industry_set_id: int | None = None,
                           aggregation_scheme_id: int | None = None):

        # The endpoint's url
        url: str = f"{self.base_url}/api/v1/IndustryCodes"

        # If we have an optional Aggregation Scheme Id, we add that to the url path
        if aggregation_scheme_id is not None:
            url = f"{url}/{aggregation_scheme_id}"

        # The Industry Set Id is passed as an additional query param
        query_params = {}
        if industry_set_id is not None:
            query_params["industrySetId"] = industry_set_id

        # Send a GET request expecting json content
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url, params=query_params)
        # Deserialize to the list of Industry Codes
        industry_codes: list[IndustryCode] = JsonHelper.deserialize_list(content, IndustryCode)

        return industry_codes
