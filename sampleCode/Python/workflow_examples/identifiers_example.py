from endpoints.api_endpoints import EndpointsHelper
from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from models.industryset_models import IndustrySet
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class IdentifiersExample:
    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper = rest_helper
        self.logging_helper = logging_helper

    def workflow(self):
        # There are several different identifiers that are required by various endpoints in order to properly filter data
        # Here are some examples of different ways of finding that data

        endpoints = EndpointsHelper(rest_helper=self.rest_helper, logging_helper=self.logging_helper)

        # Aggregation Schemes
        # These also contain valid Household Set Ids
        aggregation_schemes: list[AggregationScheme] = endpoints.aggregation_schemes.get_aggregation_schemes()

        # Datasets
        # These require an Aggregation Scheme Id
        datasets: list[Dataset] = endpoints.datasets.get_datasets(14)

        # Industry Sets
        industry_sets: list[IndustrySet] = endpoints.industry_sets.get_all()

