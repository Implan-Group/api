# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
from datetime import datetime
from endpoints.AggregationSchemeEndpoints import AggregationSchemeEndpoints
from endpoints.DataSetEndpoints import DataSetEndpoints
from endpoints.Regions.RegionEndpoints import RegionEndpoints
from workflows.authentication_workflow import AuthenticationWorkflow
from workflows.iworkflow import IWorkflow
from endpoints.Regions.CombineRegionRequest import CombineRegionRequest

class CombinedRegionWorkflow(IWorkflow):
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

        # For this example, we're going to search through the Child Regions of the US for a few particular counties.
        regions = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, data_set_id, regionType="County")
        # Convert to a dictionary so that we can quickly search by Description
        description_to_region_dict = {region.description: region for region in regions}

        # Find the HashId for the first county we want to combine
        hash_id1 = description_to_region_dict["Lane County, OR"].hash_id  # W1aQl9wzxj
        # Find the other HashId
        hash_id2 = description_to_region_dict["Douglas County, OR"].hash_id  # Rgxp4eA3xK

        # Create the request payload
        combine_region_payload = CombineRegionRequest(
            description=f"Combined Region - {datetime.now():%Y%m%d_%H%M%S}",
            hashIds=[hash_id1, hash_id2]
        )

        # Send the combine region request
        combined_region = RegionEndpoints.combine_regions(aggregation_scheme_id, combine_region_payload, bearer_token)

        # Polling loop to wait for that completion
        while True:
            user_regions = RegionEndpoints.get_user_regions(bearer_token, combined_region.aggregation_scheme_id, combined_region.dataset_id)
            region = next((r for r in user_regions if r.hash_id == combined_region.hash_id), None)

            if region and region.model_build_status.lower() == "complete":
                break

            time.sleep(30)

        # Once the ModelBuildStatus is `complete`, the Region is ready to use
        print("Region build complete:", region)
