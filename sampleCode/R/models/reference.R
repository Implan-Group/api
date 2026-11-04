# Reference data: the identifiers everything else is built on.
#
# Nothing in the Impact API stands on its own. An Industry Code only means
# something inside an Industry Set, a Dataset only exists for an Aggregation
# Scheme, and a Region is unique to a scheme and dataset together. These models
# carry those identifiers, and `identifiers()` is the resolved bundle every
# workflow starts from.
#
# Wiki: Aggregation Schemes - https://github.com/Implan-Group/api/wiki/Aggregation-Schemes
# Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets
# Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries


# Which country's data an Aggregation Scheme covers.
MAP_CODES <- c(US = "US", CANADA = "CAN", INTERNATIONAL = "INTL")


# The full list of industries for a country, in one vintage.
#
# IMPLAN revises its industry list periodically, so several sets coexist: the US
# has had 536, 546, and 528 industries. Exactly one set is flagged `is_default`,
# and that is the current one. Descriptions carry a country in parentheses, for
# example "528 Industries (latest US)", so match on the id rather than on the
# text wherever you can.
industry_set_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(
      id = NA_integer_,
      description = "",
      default_aggregation_scheme_id = NULL,
      active_status = NA,
      is_default = FALSE,
      map_type_id = NULL,
      is_naics_compatible = FALSE
    ),
    class_name = "implan_industry_set"
  )
}

describe.implan_industry_set <- function(x, ...) {
  sprintf("%s - %s", x$id, x$description)
}


# How industries are grouped for a Project.
#
# An Unaggregated scheme keeps every industry separate; the NAICS schemes roll
# them up. A Project's scheme is fixed at creation and cannot be changed, and
# every region identifier and industry code you use has to come from the same
# scheme.
#
# `status` is "Complete" when the scheme is ready to run impacts against.
aggregation_scheme_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(
      id = NA_integer_,
      description = "",
      industry_set_id = NA_integer_,
      household_set_ids = list(),
      map_code = "",
      status = ""
    ),
    class_name = "implan_aggregation_scheme"
  )
}

describe.implan_aggregation_scheme <- function(x, ...) {
  sprintf("%s - %s", x$id, x$description)
}


# One data year, within one Aggregation Scheme.
#
# Dataset ids are specific to a scheme and are not ordered by year, so an id
# taken from another scheme is either rejected or, worse, silently resolves to a
# different year. Always read the list for the scheme you are using and take the
# entry flagged `is_default`.
dataset_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(id = NA_integer_, description = "", is_default = FALSE),
    class_name = "implan_dataset"
  )
}

describe.implan_dataset <- function(x, ...) {
  sprintf("%s - %s", x$id, x$description)
}


# One industry within an Industry Set.
#
# The same `code` means different industries in different sets: 509 is
# Full-service restaurants in the 546 set and Federal electric utilities in the
# 528 set. The workflows here check the description alongside the code for that
# reason.
industry_code_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(id = NA_integer_, code = NA_integer_, description = ""),
    class_name = "implan_industry_code"
  )
}

describe.implan_industry_code <- function(x, ...) {
  sprintf("%s - %s", x$code, x$description)
}


# A valid code for an event type that needs one.
#
# Household Income events, for instance, take an income bracket such as
# "10002 - Households 15-30k" rather than an industry.
specification_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(code = "", name = ""),
    class_name = "implan_specification"
  )
}

describe.implan_specification <- function(x, ...) x$name


# Everything a workflow needs to address data, resolved from the API.
#
# Built by `resolve_identifiers()` in endpoints/identifiers.R. Holding these
# together means a workflow asks for them once and then passes one object
# around, instead of threading four integers through every call.
identifiers <- function(map_code, industry_set, aggregation_scheme, dataset, household_set_id) {
  structure(
    list(
      map_code = map_code,
      industry_set = industry_set,
      aggregation_scheme = aggregation_scheme,
      dataset = dataset,
      household_set_id = household_set_id,
      aggregation_scheme_id = aggregation_scheme$id,
      dataset_id = dataset$id
    ),
    class = "implan_identifiers"
  )
}

# A short block naming everything that was resolved, for the console.
describe.implan_identifiers <- function(x, ...) {
  paste(
    sprintf("  Map code:          %s", x$map_code),
    sprintf("  Industry Set:      %s - %s", x$industry_set$id, x$industry_set$description),
    sprintf(
      "  Aggregation Scheme:%s - %s",
      x$aggregation_scheme$id, x$aggregation_scheme$description
    ),
    sprintf("  Dataset:           %s - %s", x$dataset$id, x$dataset$description),
    sprintf("  Household Set:     %s", x$household_set_id),
    sep = "\n"
  )
}
