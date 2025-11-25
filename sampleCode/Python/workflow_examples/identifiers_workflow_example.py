from pprint import pprint
from uuid import UUID

from endpoints.endpoints_helper import EndpointsHelper
from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from models.enums import EventType
from models.industry_models import IndustrySet, IndustryCode
from utilities.prelude import uuid_empty, pretty_print
from workflow_examples.workflow_example import WorkflowExample


class IdentifiersWorkflowExample(WorkflowExample):

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def execute_example(self):
        # There are several different identifiers that are required by various endpoints in order to properly filter data
        # Here are some examples of different ways of finding that data

        # ----- Aggregation Schemes-----
        # Aggregation Schemes are used by many endpoints
        # Aggregation Schemes also contain the valid Household Set Ids that can be used in conjunction
        aggregation_schemes: list[AggregationScheme] = self.endpoints.data_endpoints.get_aggregation_schemes()
        print("Aggregation Schemes:\n")
        pretty_print(aggregation_schemes)
        print("-------------\n")
        # Examples:
        # ' 8 - 546 Unaggregated'
        # '14 - 528 Unaggregated'

        # ----- Datasets -----
        # A valid Aggregation Scheme Id is required to filter the datasets to only those that can be used
        # alongside the agg id
        agg_scheme_id = 14  # 528 Unaggregated
        datasets: list[Dataset] = self.endpoints.data_endpoints.get_datasets(aggregation_scheme_id=agg_scheme_id)
        print(f"Datasets in Agg Scheme #{agg_scheme_id}:\n")
        pretty_print(datasets)
        print("-------------\n")
        # Examples:
        # '98 - 2023 default'

        # ----- Industry Sets -----
        industry_sets: list[IndustrySet] = self.endpoints.industry_endpoints.get_industry_sets()
        print("Industry Sets:\n")
        pretty_print(industry_sets)
        print("-------------\n")
        # Examples:
        # ' 8 - 546 Industries'
        # '12 - 528 Industries'
        industry_set_id = 12

        # ----- Industry Codes -----
        # Valid industry set id and aggregation scheme ids are required to filter the data
        industry_codes: list[IndustryCode] = self.endpoints.industry_endpoints.get_industry_codes(industry_set_id=industry_set_id, aggregation_scheme_id=agg_scheme_id)
        print(f"Industry Codes in Set #{industry_set_id} + Agg #{agg_scheme_id}:\n")
        pretty_print(industry_codes)
        print("-------------\n")
        # ' 1 - Oilseed Farming'
        # ' 3 - Vegetable and melon farming'

        # ----- Event Types -----
        # Requires the Project's Id (uuid/guid) in order to determine valid Event Types for the Project's Aggregation
        # NOTE: The below line will not work unless you replace the `project_id` with a valid one that you have access to
        project_id: UUID = UUID("2c8ea5b4-ca29-11f0-ba58-0afff3912f9d")
        event_types: list[EventType] = self.endpoints.event_endpoints.get_event_types(project_id=project_id)
        print("US Project Event Types:\n")
        pretty_print(event_types)
        print("-------------\n")
