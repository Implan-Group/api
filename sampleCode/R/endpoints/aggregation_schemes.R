# Aggregation Scheme endpoints.
#
# An Aggregation Scheme decides how industries are grouped for a Project. It is
# the first identifier you resolve and the one everything else hangs off:
# datasets, regions, industry codes, and events are all scoped to it.
#
# Wiki: Aggregation Schemes
# https://github.com/Implan-Group/api/wiki/Aggregation-Schemes


# Lists the Aggregation Schemes the signed-in user can use.
#
# GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)
#
# Returns both IMPLAN's standard schemes and any custom ones on the account.
# Supplying `industry_set_id` narrows the list to the schemes built on that set,
# which is how you get from "the current industry set" to "the scheme to use".
#
# Only schemes that have finished building are returned, so an entry here is
# ready to use.
get_aggregation_schemes <- function(client, industry_set_id = NULL) {
  query <- list()
  if (!is.null(industry_set_id)) {
    # The API spells this parameter with a lowercase `s`: `industrysetId`.
    query$industrysetId <- industry_set_id
  }

  payload <- get_json(client, "/api/v1/aggregationSchemes", query = query)
  list_from_api(payload, aggregation_scheme_from_api)
}


# Reads one Aggregation Scheme by its id.
#
# GET /api/v1/aggregationSchemes/{aggregationSchemeId}
# (wiki: Aggregation Scheme by Id)
#
# Useful for checking `status` after creating a custom scheme: it is only usable
# once that reads "Complete".
get_aggregation_scheme <- function(client, aggregation_scheme_id) {
  payload <- get_json(client, sprintf("/api/v1/aggregationSchemes/%s", aggregation_scheme_id))
  aggregation_scheme_from_api(payload)
}
