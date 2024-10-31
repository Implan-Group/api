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

import logging
from endpoints.AggregationSchemeEndpoints import AggregationSchemeEndpoints,AggregationScheme
from endpoints.DataSetEndpoints import DataSetEndpoints,DataSet
from endpoints.Regions import CombineRegionRequest,Region
from endpoints.Regions.RegionEndpoints import RegionEndpoints

from workflows.authentication_workflow import AuthenticationWorkflow  # Import the AuthenticationWorkflow
from workflows.iworkflow import IWorkflow

class RegionalWorkflow(IWorkflow):
    @staticmethod
    def examples(bearer_token):
        # Define aggregation scheme and dataset IDs
        aggregation_scheme_id = 8  # Implan 546 Unaggregated
        data_set_id = 96  # 2022

        # Get a list of region types
        region_types = RegionEndpoints.get_region_types(bearer_token)
        print(f"Common Region Types: {region_types}")

        # Get the top-level region for the given aggregation scheme and dataset
        top_level_region = RegionEndpoints.get_top_level_region(bearer_token, aggregation_scheme_id, data_set_id)
        print(f"Top-Level Region: {top_level_region}")

        # Get all child regions
        child_regions = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, data_set_id)
        print(f"Child Regions: {child_regions}")

        # Access combined and customized regions
        user_regions = RegionEndpoints.get_user_regions(bearer_token, aggregation_scheme_id, data_set_id)
        print(f"User Regions: {user_regions}")

        # Search for regions by type and store them in a dictionary
        regions = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, data_set_id, regionType="State")
        description_to_region_dict = {region.description: region for region in regions}

        # Look up a few states by their names
        ohio = description_to_region_dict.get("Ohio")
        north_carolina = description_to_region_dict.get("North Carolina")
        
        print(f"Ohio Region: {ohio}")
        print(f"North Carolina Region: {north_carolina}")

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
