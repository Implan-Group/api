# Resolving the identifiers every other call needs.
#
# This file composes the lookup endpoints into the one answer a workflow actually
# wants: which Aggregation Scheme, Dataset, and Household Set should I use right
# now?
#
# Resolving instead of hardcoding is the single most important habit when writing
# against this API. IMPLAN publishes new data every year and new industry
# vintages every few years, and a script with `aggregation_scheme_id <- 8` frozen
# into it quietly analyzes 2022 data in 2030. Nothing here is expensive: three
# GETs, held for the life of the run.
#
# Wiki: Getting Started
# https://github.com/Implan-Group/api/wiki/Getting-Started


# Picks the current United States Industry Set.
#
# Exactly one set carries `is_default`. That flag moves when IMPLAN publishes a
# new vintage, which is precisely why the samples read it instead of naming a
# set.
default_us_industry_set <- function(sets) {
  for (industry_set in sets) {
    if (isTRUE(industry_set$is_default)) {
      return(industry_set)
    }
  }

  stop(
    "No Industry Set is flagged as the default. Pick one by description from ",
    "GET /api/v1/industry-sets.",
    call. = FALSE
  )
}


# Picks the newest Industry Set for Canada or International.
#
# Only the United States set carries `is_default`, so for the other two the
# newest active set is found by looking at which sets the Aggregation Schemes for
# that map code are built on, and taking the highest.
latest_set_for_map_code <- function(client, sets, map_code) {
  schemes <- Filter(
    function(scheme) {
      identical(scheme$map_code, map_code) && grepl("Unaggregated", scheme$description, fixed = TRUE)
    },
    get_aggregation_schemes(client)
  )

  if (length(schemes) == 0L) {
    stop(
      sprintf("No Unaggregated Aggregation Scheme for map code %s.", map_code),
      call. = FALSE
    )
  }

  # Industry Set ids increase with each vintage, so the highest is the newest.
  set_ids <- vapply(schemes, function(scheme) as.integer(scheme$industry_set_id), integer(1))
  newest <- schemes[[which.max(set_ids)]]

  for (industry_set in sets) {
    if (identical(as.integer(industry_set$id), as.integer(newest$industry_set_id))) {
      return(industry_set)
    }
  }

  stop(
    sprintf(
      paste0(
        "Aggregation Scheme %s refers to Industry Set %s, which is not in the ",
        "Industry Set list."
      ),
      newest$id, newest$industry_set_id
    ),
    call. = FALSE
  )
}


# Works out the current Aggregation Scheme, Dataset, and Household Set.
#
# The chain is always the same:
#
#   1. Find the Industry Set. For the United States that is the one flagged
#      `isDefault`; for Canada and International it is the newest one in use.
#   2. Take its `defaultAggregationSchemeId`, which is the Unaggregated scheme
#      for that set. Falling back to a description search covers a set that does
#      not name one.
#   3. Read that scheme's Datasets and take the one flagged `isDefault`.
#   4. Take the first of the scheme's `householdSetIds`.
#
# Every workflow starts here, so the console prints what was chosen.
resolve_identifiers <- function(client, map_code = MAP_CODES[["US"]]) {
  # GET /api/v1/industry-sets  (wiki: Get Industry Sets)
  all_sets <- get_industry_sets(client)

  industry_set <- if (identical(map_code, MAP_CODES[["US"]])) {
    default_us_industry_set(all_sets)
  } else {
    latest_set_for_map_code(client, all_sets, map_code)
  }

  # GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)
  # Narrowing by Industry Set keeps custom schemes on the account out of the way.
  schemes <- get_aggregation_schemes(client, industry_set_id = industry_set$id)
  if (length(schemes) == 0L) {
    stop(
      sprintf(
        "Industry Set %s has no Aggregation Schemes available to this account.",
        industry_set$id
      ),
      call. = FALSE
    )
  }

  scheme <- NULL
  if (!is.null(industry_set$default_aggregation_scheme_id)) {
    for (candidate in schemes) {
      if (identical(
        as.integer(candidate$id),
        as.integer(industry_set$default_aggregation_scheme_id)
      )) {
        scheme <- candidate
        break
      }
    }
  }

  if (is.null(scheme)) {
    # No default named, so take the Unaggregated scheme, which keeps every
    # industry separate and is the right starting point for a sample.
    unaggregated <- Filter(
      function(candidate) grepl("Unaggregated", candidate$description, fixed = TRUE),
      schemes
    )
    scheme <- if (length(unaggregated) > 0L) unaggregated[[1]] else schemes[[1]]
  }

  # GET /api/v1/datasets/{aggregationSchemeId}
  # (wiki: Dataset by Aggregation Scheme)
  dataset <- default_dataset(get_datasets_for_scheme(client, scheme$id))

  if (length(scheme$household_set_ids) == 0L) {
    stop(
      sprintf(
        "Aggregation Scheme %s lists no Household Sets, so a Project cannot be created against it.",
        scheme$id
      ),
      call. = FALSE
    )
  }

  resolved <- identifiers(
    map_code = map_code,
    industry_set = industry_set,
    aggregation_scheme = scheme,
    dataset = dataset,
    household_set_id = scheme$household_set_ids[[1]]
  )

  log_info("Resolved identifiers from the API:")
  log_info(describe(resolved))
  resolved
}
