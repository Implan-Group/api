import json
from http import HTTPMethod

import humps

from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from services.json_helper import JsonHelper
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper

class EndpointsHelper:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url = base_url or "https://api.implan.com"
        self._aggregation_schemes: AggregationSchemeEndpoints | None = None
        self._datasets: DatasetEndpoints | None = None
        self._projects: ProjectEndpoints | None = None

    @property
    def aggregation_schemes(self):
        if self._aggregation_schemes is None:
            self._aggregation_schemes = AggregationSchemeEndpoints(self)
        return self._aggregation_schemes

    @property
    def datasets(self):
        if self._datasets is None:
            self._datasets = DatasetEndpoints(self)
        return self._datasets

    @property
    def projects(self):
        if self._projects is None:
            self._projects = ProjectEndpoints(self)
        return self._projects


class ApiEndpoint:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url = base_url or "https://api.implan.com"


class AggregationSchemeEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def get_aggregation_schemes(self, industry_set_id: int | None = None) -> list[AggregationScheme]:
        """
        :param industry_set_id:
        :returns:
        """
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/aggregationSchemes"
        # If we have an industry set id, filter with it
        params = {}
        if industry_set_id:
            params["industrySetId"] = industry_set_id
        # Send our request, expecting json
        aggregation_schemes_json = self.rest_helper.send_http_request(HTTPMethod.GET, url, params=params)
        # Translate that back into a list of Aggregation Schemes
        agg_schemes: list[AggregationScheme] = JsonHelper.deserialize_list(aggregation_schemes_json, AggregationScheme)
        return agg_schemes

class DatasetEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def get_datasets(self, aggregation_scheme_id: int):
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/datasets/{aggregation_scheme_id}"
        # Send our request, expecting json
        dataset_json = self.rest_helper.send_http_request(HTTPMethod.GET, url)
        # Map to Datasets
        datasets: list[Dataset] = JsonHelper.deserialize_list(dataset_json, Dataset)
        return datasets


class Project:
    pass


class ProjectEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def create(self, project: Project) -> Project:
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/impact/project"
        # Turn our Project into json
        project_json = JsonHelper.serialize(project)
        # Send the request
        content = self.rest_helper.send_http_request(HTTPMethod.POST, url, json_data=project_json)
        # Deserialize
        output = JsonHelper.deserialize(content, Project)
        return output
