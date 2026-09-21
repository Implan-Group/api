"""Event endpoints, including event types, specifications, and spending patterns.

An Event is a change to an economy: an industry producing more, a household earning
more, a government spending. What an event needs depends on its type, so the flow
is usually: ask the Project which types it accepts, read any specification codes
that type needs, then create the event.

Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
"""

from models.event import Event, event_from_api, events_from_api
from models.reference import Specification
from models.spending_pattern import SpendingPattern, SpendingPatternType
from utilities.rest import ApiClient


def get_event_types(client: ApiClient, project_id: str) -> list[str]:
    """List the event types this Project accepts.

    GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)

    The list depends on the Project's Aggregation Scheme. An international scheme
    accepts the international impact-analysis types and refuses the domestic ones,
    and the reverse. Reading this list is cheaper than discovering the rule from a
    422.
    """
    return client.get_json(f"/api/v1/impact/project/{project_id}/eventtype")


def get_event_specifications(
    client: ApiClient, project_id: str, event_type: str
) -> list[Specification]:
    """List the specification codes valid for one event type in this Project.

    GET /api/v1/impact/project/{projectId}/eventtype/{eventType}/specification
    (wiki: Get Event Specifications)

    Some event types take an industry code; others take a code from a fixed list.
    Household Income is the clearest example, where the codes are income brackets
    such as `10002 - Households 15-30k`.
    """
    payload = client.get_json(
        f"/api/v1/impact/project/{project_id}/eventtype/{event_type}/specification"
    )
    return Specification.list_from_api(payload)


def get_spending_pattern(
    client: ApiClient,
    aggregation_scheme_id: int,
    specification_code: int,
    pattern_type: SpendingPatternType = SpendingPatternType.INDUSTRY,
    dataset_id: int | None = None,
    region_hash_id: str | None = None,
) -> SpendingPattern:
    """Read a default spending pattern and the commodities in it.

    GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/{spendingPatternType}/{specificationCode}
    (wiki: Spending Pattern by Id)

    This is what you read, edit, and send back when you want an event to spend
    money through a supply chain you have adjusted. `INSTITUTION` patterns need a
    `region_hash_id`, because government and household spending varies by place.
    Omitting `dataset_id` uses the newest data year.
    """
    params: dict[str, object] = {}
    if dataset_id is not None:
        params["datasetId"] = dataset_id
    if region_hash_id is not None:
        params["regionHashId"] = region_hash_id

    payload = client.get_json(
        f"/api/v1/impact/spending-patterns/{aggregation_scheme_id}"
        f"/{pattern_type.value}/{specification_code}",
        params=params,
    )
    return SpendingPattern.from_api(payload)


def create_event(client: ApiClient, project_id: str, event: Event) -> Event:
    """Add an Event to a Project and return it fully populated.

    POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)

    Leave `event.id` unset; it is generated and returned, and it is the id you
    reference from a Group. The response comes back with everything IMPLAN
    estimated from what you supplied, so re-assign rather than keeping the object
    you sent.

    A 400 means the event failed validation, usually a duplicate title or a field
    that does not belong to the type. A 422 means the type is not valid in this
    Project's Aggregation Scheme.
    """
    payload = client.post_json(
        f"/api/v1/impact/project/{project_id}/event", json_body=event.to_api()
    )
    return event_from_api(payload)


def get_events(client: ApiClient, project_id: str) -> list[Event]:
    """List every Event in a Project.

    GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)

    The list mixes types, so each item is deserialized according to its own
    `impactEventType`.
    """
    payload = client.get_json(f"/api/v1/impact/project/{project_id}/event")
    return events_from_api(payload)


def get_event(client: ApiClient, project_id: str, event_id: str) -> Event:
    """Read one Event.

    GET /api/v1/impact/project/{projectId}/event/{eventId}  (wiki: Get Event)
    """
    payload = client.get_json(
        f"/api/v1/impact/project/{project_id}/event/{event_id}"
    )
    return event_from_api(payload)


def delete_event(client: ApiClient, project_id: str, event_id: str) -> None:
    """Remove an Event from a Project.

    DELETE /api/v1/impact/project/{projectId}/event/{eventId}  (wiki: Delete Event)
    """
    client.delete(f"/api/v1/impact/project/{project_id}/event/{event_id}")
