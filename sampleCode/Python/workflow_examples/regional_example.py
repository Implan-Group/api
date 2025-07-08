from endpoints.endpoints_root import EndpointsHelper
from models.enums import RegionType
from models.region import Region
from models.request_models import CombineRegionRequest
from services.json_helper import JsonHelper
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class RegionalWorkflowExample:
    """

    """

    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.endpoints:EndpointsHelper = EndpointsHelper(rest_helper, logging_helper)


    def combine_regions(self):
        """
        An example workflow for combining multiple Regions together
        """

        # Required Information:
        aggregation_scheme_id: int = 14     # 538 Unaggregated
        dataset_id: int = 98                # 2023 Default


        # For this example, we're going to start with a list of all the Counties in the US
        # Any non-overlapping Regions can be combined
        regions: list[Region] = self.endpoints.regional_endpoints.get_region_children(aggregation_scheme_id, dataset_id, region_type=RegionType.COUNTY)

        # Select some regions to combine
        douglas_county_or: Region = next((r for r in regions if r.description == "Douglas County, OR"))
        eau_claire_county_wi: Region = next((r for r in regions if r.description == "Eau Claire County, WI"))

        # We require their HashIds for the request
        region_hash_ids: list[str] = [
            douglas_county_or.hash_id,
            eau_claire_county_wi.hash_id
            ]

        # Create the Combine Region Request payload
        payload: CombineRegionRequest = CombineRegionRequest(
            description="Example Combined Region",
            hash_ids=region_hash_ids,
        )

        # Send the request
        content: bytes = self.endpoints.regional_endpoints.combine_regions(aggregation_scheme_id, payload)
        combined_region: Region = JsonHelper.deserialize(content, Region)

        # We have to wait for the combined region to fully build before it can be used
        # We'll use a short polling loop for this
        while True:


