# Group endpoints.
#
# A Group pairs one region and one dollar year with the Events that happen there.
# An analysis comparing three states is three Groups holding the same Events.
#
# Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups


# Adds a Group to a Project and returns it with its generated id.
#
# POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
#
# Supply exactly one region identifier, and always supply `dollar_year`: there is
# no server-side default, and a Group stored without one produces an impact run
# that never attaches, which surfaces later as a 404 from the status endpoint
# rather than as an error here.
#
# Every event id in `group_events` has to belong to this Project; one that does
# not earns a 422 naming the problem.
create_group <- function(client, project_id, group) {
  payload <- post_json(
    client,
    sprintf("/api/v1/impact/project/%s/group", project_id),
    body = to_api(group)
  )
  group_from_api(payload)
}


# Lists every Group in a Project.
#
# GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
get_groups <- function(client, project_id) {
  payload <- get_json(client, sprintf("/api/v1/impact/project/%s/group", project_id))
  list_from_api(payload, group_from_api)
}


# Reads one Group.
#
# GET /api/v1/impact/project/{projectId}/group/{groupId}  (wiki: Get Group)
#
# Read a single Group rather than scanning the list when you care about a Group's
# scaling factors; the single-Group read is the authoritative one.
get_group <- function(client, project_id, group_id) {
  payload <- get_json(
    client,
    sprintf("/api/v1/impact/project/%s/group/%s", project_id, group_id)
  )
  group_from_api(payload)
}


# Removes a Group from a Project.
#
# DELETE /api/v1/impact/project/{projectId}/group/{groupId}  (wiki: Delete Group)
delete_group <- function(client, project_id, group_id) {
  delete_resource(client, sprintf("/api/v1/impact/project/%s/group/%s", project_id, group_id))
}
