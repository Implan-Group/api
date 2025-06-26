from http import HTTPMethod
from uuid import UUID

from models.aggregation_scheme import AggregationScheme
from models.dataset_models import Dataset
from models.enums import EventType
from models.industryset_models import IndustrySet
from models.project_models import Project
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
        self._industry_sets: IndustrySetEndpoints | None = None

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

    @property
    def industry_sets(self):
        if self._industry_sets is None:
            self._industry_sets = IndustrySetEndpoints(self)
        return self._industry_sets


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


class ProjectEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def create(self, project: Project) -> Project:
        # Resolve the url to the endpoint
        url = f"{self.base_url}/api/v1/impact/project"
        # Turn our Project into json
        project_json = JsonHelper.serialize(project)
        # Send the request
        content = self.rest_helper.send_http_request(HTTPMethod.POST, url, data=project_json)
        # Deserialize
        output = JsonHelper.deserialize(content, Project)
        return output


class IndustrySetEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints.rest_helper, endpoints.logging_helper, endpoints.base_url)

    def get_all(self) -> list[IndustrySet]:
        # The endpoint's url
        url: str = f"{self.base_url}/api/v1/industry-sets"

        # GET that url's content -- a json array of IndustrySets
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url)

        # Deserialize the content
        industry_sets: list[IndustrySet] = JsonHelper.deserialize_list(content, IndustrySet)

        return industry_sets

    def get(self, industry_set_id: int) -> IndustrySet | None:
        # The endpoint's url
        url: str = f"{self.base_url}/api/v1/industry-sets/{industry_set_id}"

        # GET that url's content -- a json IndustrySet
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url)

        # Deserialize the content
        industry_set: IndustrySet = JsonHelper.deserialize(content, IndustrySet)

        return industry_set

class EventEndpoints(ApiEndpoint):

    def get_events_types(self, project_guid: UUID) -> list[EventType]
        # The endpoint's url
        url = f"{self.base_url}/api/v1/impact/project/{project_guid}/eventtype"

        # GET that url's content -- a json IndustrySet
        content: str = self.rest_helper.send_http_request(HTTPMethod.GET, url)

        if response.status_code == 200:
            event_types = response.json()
            return event_types
        else:
            print(f"Failed to get event types: {response.status_code} - {response.text}")
            response.raise_for_status()


    @staticmethod
    def add_industry_output_event(project_id, event_data, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_id}/event"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        response = None
        try:
            payload = event_data.to_dict()
            print("Request Payload for IndustryOutputEvent:", json.dumps(payload, indent=4))
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return IndustryOutputEvent.from_dict(response.json())
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    @staticmethod
    def add_industry_impact_analysis_event(project_id, event_data, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_id}/event"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        response = None
        try:
            payload = event_data.to_dict()
            print("Request Payload for IndustryImpactAnalysisEvent:", json.dumps(payload, indent=4))
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return IndustryImpactAnalysisEvent.from_dict(response.json())
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.content}")
        except Exception as err:
            print(f"Other error occurred: {err}")



    @staticmethod
    def get_event(project_guid, event_guid, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event/{event_guid}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            event_data = response.json()
            return event_data
        else:
            print(f"Failed to get event: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def get_events(project_guid, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            events_data = response.json()
            print(f"Events Data: {events_data}")  # Debugging line
            return events_data
        else:
            print(f"Failed to get events: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def add_household_income_event(project_guid, household_income_event, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.post(url, json=household_income_event.to_dict(), headers=headers)
        response.raise_for_status()
        return response.json()