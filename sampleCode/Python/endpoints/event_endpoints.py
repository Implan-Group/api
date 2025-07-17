from http import HTTPMethod
from uuid import UUID

from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import EventType
from models.event_models import Event
from utilities.json_helper import JsonHelper


class EventEndpoints(ApiEndpoint):
    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def add_event[E:Event](self,
                           project_id: UUID,
                           event: E
                           ) -> E:
        # Hydrate the Endpoint URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/event"

        # Convert our Event to json
        event_json: str = JsonHelper.serialize(event)

        # POST the request
        content: bytes = self.rest_helper.post(url, body=event_json)

        # Transform the response back into our Event Type
        added_event: E = JsonHelper.deserialize(content, type(event))

        return added_event

    def get_event_types(self, project_id: UUID) -> list[EventType]:
        # The endpoint's url
        url = f"{self.base_url}/api/v1/impact/project/{project_id}/eventtype"

        # GET that url's content
        content: bytes = self.rest_helper.get(url)

        # Transform the json bytes into a list of EventType
        event_types: list[EventType] = JsonHelper.deserialize_list(content, EventType)

        return event_types

    def get_event[E](self, project_id: UUID, event_id: UUID, cls: type[E] | None = None) -> E:
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/event/{event_id}"
        content: bytes = self.rest_helper.get(url)

        if cls is None:
            event: Event = JsonHelper.deserialize(content, Event)
            return event
        else:
            event: E = JsonHelper.deserialize(content, cls)
            return event


    #
    #
    # @staticmethod
    # def get_event(project_guid, event_guid, bearer_token):
    #     url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event/{event_guid}"
    #     headers = {"Authorization": f"Bearer {bearer_token}"}
    #     response = requests.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         event_data = response.json()
    #         return event_data
    #     else:
    #         print(f"Failed to get event: {response.status_code} - {response.text}")
    #         response.raise_for_status()
    #
    # @staticmethod
    # def get_events(project_guid, bearer_token):
    #     url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event"
    #     headers = {"Authorization": f"Bearer {bearer_token}"}
    #     response = requests.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         events_data = response.json()
    #         print(f"Events Data: {events_data}")  # Debugging line
    #         return events_data
    #     else:
    #         print(f"Failed to get events: {response.status_code} - {response.text}")
    #         response.raise_for_status()
    #
    # @staticmethod
    # def add_household_income_event(project_guid, household_income_event, bearer_token):
    #     url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/event"
    #     headers = {"Authorization": f"Bearer {bearer_token}"}
    #     response = requests.post(url, json=household_income_event.to_dict(), headers=headers)
    #     response.raise_for_status()
    #     return response.json()
