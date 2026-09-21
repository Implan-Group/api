# Event endpoints, including event types, specifications, and spending patterns.
#
# An Event is a change to an economy: an industry producing more, a household
# earning more, a government spending. What an event needs depends on its type,
# so the flow is usually: ask the Project which types it accepts, read any
# specification codes that type needs, then create the event.
#
# Wiki: Events - https://github.com/Implan-Group/api/wiki/Events


# Lists the event types this Project accepts.
#
# GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
#
# The list depends on the Project's Aggregation Scheme. An international scheme
# accepts the international impact-analysis types and refuses the domestic ones,
# and the reverse. Reading this list is cheaper than discovering the rule from a
# 422.
get_event_types <- function(client, project_id) {
  payload <- get_json(client, sprintf("/api/v1/impact/project/%s/eventtype", project_id))
  unlist(payload, use.names = FALSE)
}


# Lists the specification codes valid for one event type in this Project.
#
# GET /api/v1/impact/project/{projectId}/eventtype/{eventType}/specification
# (wiki: Get Event Specifications)
#
# Some event types take an industry code; others take a code from a fixed list.
# Household Income is the clearest example, where the codes are income brackets
# such as "10002 - Households 15-30k".
get_event_specifications <- function(client, project_id, event_type) {
  payload <- get_json(
    client,
    sprintf("/api/v1/impact/project/%s/eventtype/%s/specification", project_id, event_type)
  )
  list_from_api(payload, specification_from_api)
}


# Reads a default spending pattern and the commodities in it.
#
# GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/{spendingPatternType}/{specificationCode}
# (wiki: Spending Pattern by Id)
#
# This is what you read, edit, and send back when you want an event to spend
# money through a supply chain you have adjusted. "Institution" patterns need a
# `region_hash_id`, because government and household spending varies by place.
# Omitting `dataset_id` uses the newest data year.
get_spending_pattern <- function(client,
                                 aggregation_scheme_id,
                                 specification_code,
                                 pattern_type = SPENDING_PATTERN_TYPES[["INDUSTRY"]],
                                 dataset_id = NULL,
                                 region_hash_id = NULL) {
  query <- list()
  if (!is.null(dataset_id)) {
    query$datasetId <- dataset_id
  }
  if (!is.null(region_hash_id)) {
    query$regionHashId <- region_hash_id
  }

  payload <- get_json(
    client,
    sprintf(
      "/api/v1/impact/spending-patterns/%s/%s/%s",
      aggregation_scheme_id, pattern_type, specification_code
    ),
    query = query
  )
  spending_pattern_commodities_from_api(payload)
}


# Adds an Event to a Project and returns it fully populated.
#
# POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
#
# Leave the event's `id` unset; it is generated and returned, and it is the id
# you reference from a Group. The response comes back with everything IMPLAN
# estimated from what you supplied, so use the returned event rather than keeping
# the one you sent.
#
# A 400 means the event failed validation, usually a duplicate title or a field
# that does not belong to the type. A 422 means the type is not valid in this
# Project's Aggregation Scheme.
create_event <- function(client, project_id, event) {
  payload <- post_json(
    client,
    sprintf("/api/v1/impact/project/%s/event", project_id),
    body = to_api(event)
  )
  event_from_api(payload)
}


# Lists every Event in a Project.
#
# GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)
#
# The list mixes types, so each item is read according to its own
# `impactEventType`.
get_events <- function(client, project_id) {
  events_from_api(get_json(client, sprintf("/api/v1/impact/project/%s/event", project_id)))
}


# Reads one Event.
#
# GET /api/v1/impact/project/{projectId}/event/{eventId}  (wiki: Get Event)
get_event <- function(client, project_id, event_id) {
  payload <- get_json(
    client,
    sprintf("/api/v1/impact/project/%s/event/%s", project_id, event_id)
  )
  event_from_api(payload)
}


# Removes an Event from a Project.
#
# DELETE /api/v1/impact/project/{projectId}/event/{eventId}  (wiki: Delete Event)
delete_event <- function(client, project_id, event_id) {
  delete_resource(client, sprintf("/api/v1/impact/project/%s/event/%s", project_id, event_id))
}
