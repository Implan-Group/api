"""Group endpoints.

A Group pairs one region and one dollar year with the Events that happen there. An
analysis comparing three states is three Groups holding the same Events.

Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
"""

from models.group import Group
from utilities.rest import ApiClient


def create_group(client: ApiClient, project_id: str, group: Group) -> Group:
    """Add a Group to a Project and return it with its generated id.

    POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)

    Supply exactly one region identifier, and always supply `dollar_year`: there is
    no server-side default, and a Group stored without one produces an impact run
    that never attaches, which surfaces later as a 404 from the status endpoint
    rather than as an error here.

    Every event id in `group_events` has to belong to this Project; one that does
    not earns a 422 naming the problem.
    """
    payload = client.post_json(
        f"/api/v1/impact/project/{project_id}/group", json_body=group.to_api()
    )
    return Group.from_api(payload)


def get_groups(client: ApiClient, project_id: str) -> list[Group]:
    """List every Group in a Project.

    GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
    """
    payload = client.get_json(f"/api/v1/impact/project/{project_id}/group")
    return Group.list_from_api(payload)


def get_group(client: ApiClient, project_id: str, group_id: str) -> Group:
    """Read one Group.

    GET /api/v1/impact/project/{projectId}/group/{groupId}  (wiki: Get Group)

    Read a single Group rather than scanning the list when you care about a
    Group's scaling factors; the single-Group read is the authoritative one.
    """
    payload = client.get_json(
        f"/api/v1/impact/project/{project_id}/group/{group_id}"
    )
    return Group.from_api(payload)


def delete_group(client: ApiClient, project_id: str, group_id: str) -> None:
    """Remove a Group from a Project.

    DELETE /api/v1/impact/project/{projectId}/group/{groupId}
    (wiki: Delete Group)
    """
    client.delete(f"/api/v1/impact/project/{project_id}/group/{group_id}")
