from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.industry_models import IndustrySet, IndustryCode
from utilities.json_helper import JsonHelper


class IndustryEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to Industry Sets and Industry Codes
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def get_industry_sets(self) -> list[IndustrySet]:
        """
        Gets a list of all valid Industry Sets
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/industry-sets"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into a list of Industry Sets
        industry_sets: list[IndustrySet] = JsonHelper.deserialize_list(content, IndustrySet)
        return industry_sets

    def get_industry_set(self, industry_set_id: int) -> IndustrySet | None:
        """
        Gets the Industry Set with a given identifier
        :param industry_set_id: The id for the Industry Set to return
        :returns: The found Industry Set or None
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/industry-sets/{industry_set_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the Industry Set
        industry_set: IndustrySet = JsonHelper.deserialize(content, IndustrySet)
        return industry_set

    def get_industry_codes(self,
                           industry_set_id: int | None = None,
                           aggregation_scheme_id: int | None = None) -> list[IndustryCode]:
        """
        Gets a list of valid Industry Codes that can optionally filtered for use with a particular Industry Set and/or Aggregation Scheme.
        :param industry_set_id: An optional Industry Set Id used for filtering
        :param aggregation_scheme_id: An optional Aggregation Scheme Id used for filtering
        """

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
        content: bytes = self.rest_helper.get(url, query_params=query_params)
        # Deserialize to the list of Industry Codes
        industry_codes: list[IndustryCode] = JsonHelper.deserialize_list(content, IndustryCode)

        return industry_codes
