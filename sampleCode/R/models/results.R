# Impact runs and their results.
#
# An Impact Run is one execution of a Project. It is started with a POST, it
# takes a few minutes, and its status is polled until it reaches a terminal
# state. The results are then read as CSV reports, filtered however you like.
#
# Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
# Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results


# The states an impact run moves through.
#
# "Complete" is the only one that means results can be read. "Error" and
# "UserCancelled" are terminal failures: polling past them waits forever. A 404
# from the status endpoint is also terminal, and means the run never attached to
# a project, most often because a group was saved without a dollar year.
IMPACT_STATUSES <- c(
  UNKNOWN = "Unknown",
  NEW = "New",
  IN_PROGRESS = "InProgress",
  READY_FOR_WAREHOUSE = "ReadyForWarehouse",
  COMPLETE = "Complete",
  ERROR = "Error",
  USER_CANCELLED = "UserCancelled"
)


# TRUE when the run has stopped and will not produce results.
is_terminal_failure <- function(status) {
  status %in% c(IMPACT_STATUSES[["ERROR"]], IMPACT_STATUSES[["USER_CANCELLED"]])
}


# The three effects an impact analysis separates.
#
# Direct is the activity itself, Indirect is its supply chain, and Induced is the
# household spending of everyone paid along the way.
#
# Support: Examining Results and Interpreting Direct, Indirect, and Induced Effects
# https://support.implan.com/hc/en-us/articles/360038799153
IMPACT_TYPES <- c(DIRECT = "Direct", INDIRECT = "Indirect", INDUCED = "Induced")


# Optional filters shared by the CSV report endpoints.
#
# These go on the query string rather than in a body. Leaving one empty means no
# filter on that dimension.
#
# `year` overrides the dollar year the results are expressed in. Left unset, the
# API uses your account's dollar-year preference, falling back to the current
# calendar year, so the samples set it explicitly to keep runs reproducible.
result_filters <- function(year = NULL,
                           regions = NULL,
                           impacts = NULL,
                           groups = NULL,
                           events = NULL,
                           event_tags = NULL) {
  structure(
    list(
      year = year,
      regions = regions,
      impacts = impacts,
      groups = groups,
      events = events,
      event_tags = event_tags
    ),
    class = "implan_result_filters"
  )
}


# Renders the filters as query parameters, omitting the empty ones.
#
# A parameter holding several values is left as a vector, and the REST layer
# turns it into a repeated parameter (`regions=Oregon&regions=Wisconsin`), which
# is the shape the API expects.
filters_to_query <- function(filters) {
  if (is.null(filters)) {
    return(list())
  }

  query <- list()
  if (!is.null(filters$year)) query$year <- filters$year
  if (length(filters$regions) > 0) query$regions <- filters$regions
  if (length(filters$impacts) > 0) query$impacts <- filters$impacts
  if (length(filters$groups) > 0) query$groups <- filters$groups
  if (length(filters$events) > 0) query$events <- filters$events
  if (length(filters$event_tags) > 0) query$eventTags <- filters$event_tags
  query
}


# Filters for the Estimated Growth Percentage report.
#
# Every list has to be present in the request, even when empty, so all five
# default to empty vectors here rather than to NULL. `dollar_year` is required.
#
# This is the body of a GET request, which is unusual but is what the endpoint
# requires; see `get_estimated_growth_percentage()` in
# endpoints/impact_results.R.
impact_results_export_request <- function(dollar_year,
                                          regions = character(),
                                          impacts = character(),
                                          group_names = character(),
                                          event_names = character(),
                                          event_tags = character()) {
  structure(
    list(
      dollar_year = dollar_year,
      regions = regions,
      impacts = impacts,
      group_names = group_names,
      event_names = event_names,
      event_tags = event_tags
    ),
    class = c("implan_growth_request", "implan_model", "list")
  )
}
