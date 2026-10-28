# Dataset endpoints.
#
# A Dataset is one data year within one Aggregation Scheme. IMPLAN publishes data
# annually and flags the newest complete year as the default.
#
# Dataset ids are scheme-specific and are not ordered by year, so never carry an
# id from one scheme to another and never assume the newest is last in the list.
# Read the list for your scheme and take the entry flagged `is_default`.
#
# Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets


# Lists the data years available for one Aggregation Scheme.
#
# GET /api/v1/datasets/{aggregationSchemeId}
# (wiki: Dataset by Aggregation Scheme)
get_datasets_for_scheme <- function(client, aggregation_scheme_id) {
  payload <- get_json(client, sprintf("/api/v1/datasets/%s", aggregation_scheme_id))
  list_from_api(payload, dataset_from_api)
}


# Lists the data years for the current default Aggregation Scheme.
#
# GET /api/v1/datasets  (wiki: Datasets)
#
# The scheme-scoped call above is almost always the one you want, because it
# makes the scheme the ids belong to explicit.
get_datasets <- function(client) {
  list_from_api(get_json(client, "/api/v1/datasets"), dataset_from_api)
}


# Picks the default data year out of a list.
#
# The default is flagged rather than ordered: it is often the last entry, so
# taking the first would quietly select 2001. Exactly one entry carries the flag.
default_dataset <- function(datasets) {
  for (dataset in datasets) {
    if (isTRUE(dataset$is_default)) {
      return(dataset)
    }
  }

  stop(
    "No Dataset in this Aggregation Scheme is flagged as the default. ",
    "Choose one explicitly by description.",
    call. = FALSE
  )
}
