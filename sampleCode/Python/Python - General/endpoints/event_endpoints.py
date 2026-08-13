from uuid import UUID
from endpoints.endpoint import ApiEndpoint
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import EventType
from models.event_models import Event
from utilities.json_helper import JsonHelper


class EventEndpoints(ApiEndpoint):
    """
    A collection of API Endpoints related to Events.
    """

    def __init__(self, endpoints: EndpointsHelper):
        super().__init__(endpoints)

    def add_event[E:Event](self,
                           project_id: UUID,
                           event: E
                           ) -> E:
        """
        Adds a new Event to an existing Project
        :param project_id: The uuid for the Project to add the Event to
        :param event: The Event to add to the Project
        :returns: The fully-hydrated Event that has been added to the Project
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/event"

        # Convert the Event to json
        event_json: str = JsonHelper.serialize(event)

        # Send the request and get the returned content
        content: bytes = self.rest_helper.post(url, body=event_json)

        # Translate the content into the hydrated Event
        added_event: E = JsonHelper.deserialize(content, type(event))
        return added_event

    def get_event_types(self, project_id: UUID) -> list[EventType]:
        """
        Get a list of all valid Event Types that can be used in a given Project
        :param project_id: The uuid for the Project that the Event will be added to
        :returns: A list of all valid Event Types that can be used with the given Project
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/eventtype"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Event Types
        event_types: list[EventType] = JsonHelper.deserialize_list(content, EventType)
        return event_types

    def get_event[E](self, project_id: UUID, event_id: UUID, cls: type[E] | None = None) -> E:
        """
        Gets an existing Event's information
        :param project_id: The uuid for the Project that contains the Event
        :param event_id: The uuid for the Event to return
        :param cls: The Event's class name, used to map back to the correct Event type
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/event/{event_id}"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # If a specific Event class was not passed, we deserialize to the basic Event instance
        if cls is None:
            event: Event = JsonHelper.deserialize(content, Event)
            return event
        else:
            # Otherwise, deserialize to the specific Event instance type
            event: E = JsonHelper.deserialize(content, cls)
            return event

    def get_events(self, project_id: UUID) -> list[Event]:
        """
        Returns a list of all Events that have been added to a Project
        :param project_id: The uuid for the existing Project
        :returns: A list of all Events added to the Project
        """

        # Resolve the endpoint's full URL
        url: str = f"{self.base_url}/api/v1/impact/project/{project_id}/event"

        # Send the request and get the returned content
        content: bytes = self.rest_helper.get(url)

        # Translate the content into the list of Events
        events: list[Event] = JsonHelper.deserialize_list(content, Event)
        return events
