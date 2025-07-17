from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import RegionType
from models.region import Region
from models.request_models import CombineRegionRequest
from utilities.json_helper import JsonHelper


class RegionalEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)


    def get_region_types(self) -> list[RegionType]:

        # Hydrate the full url
        url: str = f"{self.base_url}/api/v1/region/RegionTypes"

        # No extra information needed for headers/body

        # Send a GET Request and get the Response
        content: bytes = self.rest_helper.get(url)

        # Convert into a list of RegionTypes
        region_types: list[RegionType] = JsonHelper.deserialize_list(content, RegionType)

        return region_types


    def get_top_level_region(self, aggregation_scheme_id: int, dataset_id: int) -> Region:

        # Hydrate the full url
        url: str = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}"

        # No extra information needed for headers/body

        # Send a GET Request and get the Response
        content: bytes = self.rest_helper.get(url)

        # Convert into a single Region
        region: Region = JsonHelper.deserialize(content, Region)

        return region


    def get_region_children(self,
                            aggregation_scheme_id: int,
                            dataset_id: int,
                            urid: int | None = None,
                            hash_id: str | None = None,
                            region_type: RegionType | None = None) -> list[Region]:

        # Hydrate the full url
        url: str
        if hash_id is not None:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hash_id}/children"
        elif urid is not None:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{urid}/children"
        else:
            url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children"

        # If we have a region_type, we need to add it as a query param
        query_params = {}
        if region_type:
            query_params["regionTypeFilter"] = region_type

        # Send a GET Request and get the Response
        content: bytes = self.rest_helper.get(url, query_params=query_params)

        # Convert into Regions
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)

        return regions


    def get_user_regions(self, aggregation_scheme_id: int, dataset_id: int) -> list[Region]:
        # Hydrate the full url
        url: str = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/user"

        # No extra information needed for headers/body

        # Send a GET Request and get the Response
        content: bytes = self.rest_helper.get(url)

        # Convert into Regions
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)

        return regions


    def combine_regions(self,
                        aggregation_scheme_id: int,
                        payload: CombineRegionRequest) -> Region:
        # Hydrate the full url
        url: str = f"{self.base_url}/api/v1/region/build/combined/{aggregation_scheme_id}"

        # Add the CombineRegionRequest as a json payload
        payload: str = JsonHelper.serialize(payload)

        # POST the request and get the response
        content: bytes = self.rest_helper.post(url, body=payload)

        # The response is a list that contains a single region
        regions: list[Region] = JsonHelper.deserialize_list(content, Region)

        if len(regions) != 1:
            raise "Invalid number of regions returned"

        region: Region = regions[0]
        return region
