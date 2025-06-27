from uuid import UUID

from endpoints.endpoints_root import EndpointsHelper
from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset

from models.enums import EventType
from models.industry_models import IndustrySet, IndustryCode
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class IdentifiersExample:
    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper = rest_helper
        self.logging_helper = logging_helper

    def execute_example(self):
        # There are several different identifiers that are required by various endpoints in order to properly filter data
        # Here are some examples of different ways of finding that data

        endpoints = EndpointsHelper(rest_helper=self.rest_helper, logging_helper=self.logging_helper)

        # Aggregation Schemes
        # These also contain valid Household Set Ids
        aggregation_schemes: list[AggregationScheme] = endpoints.aggregation_endpoints.get_aggregation_schemes()
        # Examples:
        # ' 8 - 546 Unaggregated'
        # '14 - 528 Unaggregated'


        # Datasets
        # These require an Aggregation Scheme Id
        datasets: list[Dataset] = endpoints.dataset_endpoints.get_datasets(14)

        # Industry Sets
        industry_sets: list[IndustrySet] = endpoints.industry_endpoints.get_industry_sets()
        # Examples:
        # ' 8 - 546 Industries'
        # '12 - 528 Industries'

        # Industry Codes
        industry_codes: list[IndustryCode] = endpoints.industry_endpoints.get_industry_codes(industry_set_id=12, aggregation_scheme_id=14)
        # ' 1 - Oilseed Farming'
        # ' 3 - Vegetable and melon farming'

        # Event Types
        # Required the Project Id (UUID) in order to determine valid Event Types for the Project's Aggregation
        # EXAMPLE DOES NOT WORK
        #event_types: list[EventType] = endpoints.event_endpoints.get_event_types()


        print('break')
