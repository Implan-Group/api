# Industry Set and Industry Code endpoints.
#
# An Industry Set is a vintage of IMPLAN's industry list; an Industry Code names
# one industry inside a set. Codes are only meaningful with their set: 509 is
# Full-service restaurants in the 546 set and Federal electric utilities in the
# 528 set, so a code copied from an older example lands on the wrong industry
# rather than failing.
#
# Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries


# Lists every Industry Set, including retired ones.
#
# GET /api/v1/industry-sets  (wiki: Get Industry Sets)
#
# `active_status` marks a set as still supported and exactly one set carries
# `is_default`, which is the current United States list. There is no public
# endpoint for reading a single set, so filter this list when you want one.
get_industry_sets <- function(client) {
  list_from_api(get_json(client, "/api/v1/industry-sets"), industry_set_from_api)
}


# Lists the industries in an Aggregation Scheme, ordered by code.
#
# GET /api/v1/IndustryCodes/{aggregationSchemeId}
# (wiki: Industry Codes by Aggregation Scheme)
#
# This route takes no query string. An `industrySetId` parameter added here is
# ignored, because a scheme already implies its Industry Set; the route below is
# the one that accepts it. For a custom scheme these are the scheme's own
# aggregated sectors.
get_industry_codes_for_scheme <- function(client, aggregation_scheme_id) {
  payload <- get_json(client, sprintf("/api/v1/IndustryCodes/%s", aggregation_scheme_id))
  list_from_api(payload, industry_code_from_api)
}


# Lists the industries in an Industry Set, ordered by code.
#
# GET /api/v1/IndustryCodes  (wiki: Industry Codes by Industry Set)
#
# Omitting `industry_set_id` uses the current default United States set.
get_industry_codes_for_set <- function(client, industry_set_id = NULL) {
  query <- list()
  if (!is.null(industry_set_id)) {
    query$industrySetId <- industry_set_id
  }

  payload <- get_json(client, "/api/v1/IndustryCodes", query = query)
  list_from_api(payload, industry_code_from_api)
}


# Finds one industry by code, and confirms it is the industry you meant.
#
# Checking the description as well as the code is the guard against the trap this
# file's header describes. The comparison is loose on purpose: IMPLAN rewords
# descriptions between vintages, so a substring match either way is enough to
# catch a code that has moved to a different industry entirely.
find_industry <- function(industries, code, expected_description) {
  for (industry in industries) {
    if (!identical(as.integer(industry$code), as.integer(code))) {
      next
    }

    actual <- tolower(industry$description)
    expected <- tolower(expected_description)
    if (grepl(expected, actual, fixed = TRUE) || grepl(actual, expected, fixed = TRUE)) {
      return(industry)
    }

    stop(
      sprintf(
        paste0(
          "Industry code %s is '%s' in this Aggregation Scheme, not '%s'. ",
          "Industry codes differ between Industry Sets; look the industry up by ",
          "description instead."
        ),
        code, industry$description, expected_description
      ),
      call. = FALSE
    )
  }

  stop(
    sprintf("No industry with code %s in this Aggregation Scheme.", code),
    call. = FALSE
  )
}


# Finds one industry by description, matched case-insensitively.
#
# Use this when you know the industry by name and want whatever code it carries
# in the scheme you resolved, which is the portable way to write a sample.
find_industry_by_description <- function(industries, description) {
  wanted <- tolower(description)
  matches <- Filter(function(industry) identical(tolower(industry$description), wanted), industries)

  if (length(matches) == 1L) {
    return(matches[[1]])
  }

  if (length(matches) == 0L) {
    stop(
      sprintf(
        paste0(
          "No industry named '%s' in this Aggregation Scheme. Print the industry ",
          "list to see the available descriptions."
        ),
        description
      ),
      call. = FALSE
    )
  }

  stop(
    sprintf(
      "'%s' matches %d industries in this Aggregation Scheme; use the code instead.",
      description, length(matches)
    ),
    call. = FALSE
  )
}
