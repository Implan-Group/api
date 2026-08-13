from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import RegionType
from models.region import Region
from models.request_models import CombineRegionRequest
from utilities.json_helper import JsonHelper


class RegionalEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to Regions
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def get_region_types(self) -> list[RegionType]:
        """
        Returns a list of all valid Region Types
        :returns: A list of RegionTypes
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/region/RegionTypes"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Region Types
        region_types: list[RegionType] = JsonHelper.deserialize_list(content, RegionType)
        return region_types

    def get_top_level_region(self, aggregation_scheme_id: int, dataset_id: int) -> Region:
        """
        Returns the Top-Level Region for a given Aggregation Scheme and Dataset
        :param aggregation_scheme_id: The Aggregation Scheme the Region must belong to
        :param dataset_id: The Dataset the Region must belong to
        :returns: The top-level Region that matches the Aggregation and Dataset
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the Region
        region: Region = JsonHelper.deserialize(content, Region)
        return region

    def get_region_children(self,
                            aggregation_scheme_id: int,
                            dataset_id: int,
                            urid: int | None = None,
                            hash_id: str | None = None,
                            region_type: RegionType | None = None) -> list[Region]:
        """
        Returns a list of all the Child Regions for a particular Region
        :param aggregation_scheme_id: The Aggregation Scheme the children must belong to
        :param dataset_id: The Dataset the children must belong to
        :param urid: One of `urid` or `hash_id` may be specified as the Parent Region,
        :param hash_id: whose children are to be returned
        :param region_type: Optional filter for the Types of Regions to return
        """

        # Resolve the endpoint's full URL
        url: str
        if hash_id is not None:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hash_id}/children"
        elif urid is not None:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{urid}/children"
        else:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children"

        # If we have an optional RegionType, we add it as a Query Parameter
        query_params = {}
        if region_type:
            query_params["regionTypeFilter"] = region_type

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url, query_params=query_params)

        # Translate the content into the list of Regions
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)
        return regions

    def get_user_regions(self, aggregation_scheme_id: int, dataset_id: int) -> list[Region]:
        """
        Returns a list of all User-Created Regions
        :param aggregation_scheme_id: The Aggregation Scheme the Regions must belong to
        :param dataset_id: The Dataset the Regions must belong to
        :returns: A list of user-created Regions matching the filter criteria
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/user"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Regions
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)
        return regions

    def combine_regions(self,
                        aggregation_scheme_id: int,
                        payload: CombineRegionRequest) -> Region:
        """
        Combines two or more Regions together into a Combined Region
        :param aggregation_scheme_id: The Aggregation Scheme the combined Region will belong to
        :param payload: The CombineRegionRequest model that defines which Regions to Combine
        :returns: The newly Combined Region
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/region/build/combined/{aggregation_scheme_id}"

        # Convert the CombineRegionRequest into a json body
        payload: str = JsonHelper.serialize(payload)

        # Send the request and get the returned content
        content: bytes = self.rest_helper.post(url, body=payload)

        # For this endpoint, the response is a list of Regions, but it only contains a single entry
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)

        if len(regions) != 1:
            raise "Invalid number of regions returned"

        region: Region = regions[0]
        return region
