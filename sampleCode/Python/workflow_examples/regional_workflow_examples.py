import time

from endpoints.endpoints_helper import EndpointsHelper
from models.enums import RegionType
from models.region import Region
from models.request_models import CombineRegionRequest
from workflow_examples.workflow_example import WorkflowExample


class RegionalWorkflowExamples(WorkflowExample):
    """
    Workflow Examples around Regionality: Searching, filtering, and using Regions
    """

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def combine_regions(self) -> Region:
        """
        An example workflow for combining multiple Regions together
        Any number of non-overlapping Regions can be combined this way
        """

        # Required Identifiers: (see `identifiers_workflow_example` and `data_endpoints` for more information)
        aggregation_scheme_id: int = 14  # 538 Unaggregated
        dataset_id: int = 98  # 2023 Default

        # For this example, we're going to start with a list of all the Counties in the US
        regions: list[Region] = self.endpoints.regional_endpoints.get_region_children(
            aggregation_scheme_id,
            dataset_id,
            region_type=RegionType.COUNTY)

        # Filter to the counties we're going to combine
        douglas_county_or: Region = next((r for r in regions if r.description == "Douglas County, OR"))
        eau_claire_county_wi: Region = next((r for r in regions if r.description == "Eau Claire County, WI"))

        # We require their hashids for the request
        region_hash_ids: list[str] = [
            douglas_county_or.hash_id,
            eau_claire_county_wi.hash_id
        ]

        # Create the Combine Region Request payload
        payload: CombineRegionRequest = CombineRegionRequest(
            description="Example Combined Region",
            hash_ids=region_hash_ids,
        )

        # Send the request to have the regions combined
        combined_region: Region = self.endpoints.regional_endpoints.combine_regions(aggregation_scheme_id, payload)

        # We have to wait for the combined region to fully build before it can be used
        # Use a short polling loop for this
        while True:
            # Pull down a list of User-defined Regions (which includes combined + customized)
            user_regions: list[Region] = self.endpoints.regional_endpoints.get_user_regions(aggregation_scheme_id, dataset_id)
            # Find the region that has the same HashId as our response
            region = next((r for r in user_regions if r.hash_id == combined_region.hash_id), None)
            # If the region does not exist or has a non-complete status, we must wait a bit longer
            if region is None or region.model_build_status != "Complete":
                # Wait 30 seconds and try again
                time.sleep(30.0)
            else:
                # Our region exists and has finished building
                break

        # Now this combined region can be used for any other workflow, using its ids:
        # Please see the simple + complex workflow examples for more examples
        hash_id: str = region.hash_id
        urid: int = region.urid

        return region

    def explore_implan_regions(self):
        """
        Examples around exploring Regional data through connections
        """

        # ----- United States -----
        # If we specify a US aggregation scheme, the returned top-level-region will be the entire United States
        us_aggregation_scheme_id: int = 14  # 528 Unaggregated US
        us_dataset_id: int = 98  # 2023
        us_region: Region = self.endpoints.regional_endpoints.get_top_level_region(us_aggregation_scheme_id, us_dataset_id)
        print(us_region)

        # Using the US's HashId lets us explore sub-regions,
        # Like all 50 States + DC
        us_states: list[Region] = self.endpoints.regional_endpoints.get_region_children(us_aggregation_scheme_id, us_dataset_id, hash_id=us_region.hash_id, region_type=RegionType.STATE)
        # Or every single Zip Code
        us_zips: list[Region] = self.endpoints.regional_endpoints.get_region_children(us_aggregation_scheme_id, us_dataset_id, hash_id=us_region.hash_id, region_type=RegionType.ZIPCODE)

        # ----- Canada -----
        # If we use a Canadian aggregation scheme, the returned region will be Canada
        can_aggregation_scheme_id: int = 12  # 235 Unaggregated Canada
        can_dataset_id: int = 100  # 2021 CAN
        can_region: Region = self.endpoints.regional_endpoints.get_top_level_region(can_aggregation_scheme_id, can_dataset_id)
        print(can_region)
        # We can access its Territories, but no other sub-regional information
        can_territories: list[Region] = self.endpoints.regional_endpoints.get_region_children(can_aggregation_scheme_id, can_dataset_id, hash_id=can_region.hash_id, region_type=RegionType.STATE)
        print(can_territories)

        # ----- International -----
        # To access international regions, you must use an International Aggregation Scheme Id and Dataset
        # However, there is no top-level International Region, nor International Sub-Regions
        # You can access a full list of every Country
        intl_aggregation_scheme_id: int = 13  # 46 Unaggregated International
        intl_dataset_id: int = 95  # 2020 International
        intl_countries: list[Region] = self.endpoints.regional_endpoints.get_region_children(intl_aggregation_scheme_id, intl_dataset_id, region_type=RegionType.COUNTRY)
        print(intl_countries)

    def explore_user_regions(self):
        """
        Examples around exploring a User's Regional Data
        """

        # Get all Regions defined by the current User (Combined and/or Customized)
        # This must be filtered down by an Aggregation Scheme and Dataset
        us_aggregation_scheme_id: int = 14  # 528 Unaggregated US
        us_dataset_id: int = 98  # 2023

        user_regions: list[Region] = self.endpoints.regional_endpoints.get_user_regions(us_aggregation_scheme_id, us_dataset_id)
        print(user_regions)
