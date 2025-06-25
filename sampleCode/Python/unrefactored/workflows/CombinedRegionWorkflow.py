import time

from datetime import datetime
from unrefactored.endpoints.aggregation_scheme_endpoints import AggregationSchemeEndpoints
from unrefactored.endpoints.dataset_endpoints import DataSetEndpoints
from unrefactored.endpoints.regions.region_endpoints import RegionEndpoints
from endpoints.regions.CombineRegionRequest import CombineRegionRequest

class CombinedRegionWorkflow:
    @staticmethod
    def examples(bearer_token):
        # Get a list of all valid Aggregation Schemes
        aggregation_schemes = AggregationSchemeEndpoints.get_aggregation_schemes(bearer_token)
        # Choose the one you would like to use
        aggregation_scheme_id = 8  # 8 = Implan 546 Unaggregated

        # Get a list of all valid Data Sets for the Aggregation Scheme
        datasets = DataSetEndpoints.get_datasets(aggregation_scheme_id, bearer_token)
        # Choose the one you would like to use -- must be compatible with your chosen HouseholdSetId
        data_set_id = 96  # 96 = 2022 Data

        # For this example, we're going to search through the Child regions of the US for a few particular counties.
        regions = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, data_set_id, region_type="County")
        # Convert to a dictionary so that we can quickly search by Description
        description_to_region_dict = {region.description: region for region in regions}

        # Find the HashId for the first county we want to combine
        hashid1 = description_to_region_dict["Lane County, OR"].hashid  # W1aQl9wzxj
        # Find the other HashId
        hashid2 = description_to_region_dict["Douglas County, OR"].hashid  # Rgxp4eA3xK

        # Create the request payload
        combine_region_payload = CombineRegionRequest(
            description=f"Combined Region - {datetime.now():%Y%m%d_%H%M%S}",
            hashids=[hashid1, hashid2]
        )

        # Send the combine region request
        combined_region = RegionEndpoints.combine_regions(aggregation_scheme_id, combine_region_payload, bearer_token)

        # Polling loop to wait for that completion
        while True:
            user_regions = RegionEndpoints.get_user_regions(bearer_token, combined_region.aggregation_scheme_id, combined_region.dataset_id)
            region = next((r for r in user_regions if r.hashid == combined_region.hashid), None)

            if region and region.model_build_status.lower() == "complete":
                break

            time.sleep(30)

        # Once the ModelBuildStatus is `complete`, the Region is ready to use
        print("Region build complete:", region)
