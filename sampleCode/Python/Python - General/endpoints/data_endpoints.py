from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from models.enums import EventType
from models.specification import Specification
from utilities.json_helper import JsonHelper


class DataEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to retrieving identifiers, enumerations, and other data.
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def get_aggregation_schemes(self, industry_set_id: int | None = None) -> list[AggregationScheme]:
        """
        Returns a list of all valid Aggregation Schemes, optionally filtered by an Industry Set
        :param industry_set_id: An optional `int` that filters the Aggregation Schemes by Industry Set
        :returns: A list of Aggregation Schemes
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/aggregationSchemes"

        # If an Industry Set was specified, add it to the query parameters
        query_params = {}
        if industry_set_id:
            query_params["industrySetId"] = industry_set_id

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url, query_params=query_params)

        # Translate the content into the list of Aggregation Schemes
        agg_schemes: list[AggregationScheme] = JsonHelper.deserialize_list(content, AggregationScheme)
        return agg_schemes

    def get_datasets(self, aggregation_scheme_id: int) -> list[Dataset]:
        """
        Returns a list of all valid Datasets for a given Aggregation Scheme
        :param aggregation_scheme_id: The Aggregation Scheme Id used to filter the Datsets
        :returns: A list of valid Datasets
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/datasets/{aggregation_scheme_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Datasets
        datasets: list[Dataset] = JsonHelper.deserialize_list(content, Dataset)
        return datasets

    def get_specifications(self, project_id: UUID, event_type: EventType) -> list[Specification]:
        """
        Returns a list of valid Specification Codes that can be used with a given Event Type
        :param project_id: The uuid for the existing Implan Project the Event will be added to
        :param event_type: The EventType that the specifications will be used with
        :returns: A list of valid Specifications
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/eventtype/{event_type}/specification"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Specifications
        specifications: list[Specification] = JsonHelper.deserialize_list(content, Specification)
        return specifications
