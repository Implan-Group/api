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
