# Regions: the geographies an impact is measured in.
#
# A Region in IMPLAN is not just a place, it is a place within one Aggregation
# Scheme and one Dataset. The same county has a different `hash_id` in the 528
# and 546 schemes, and in the 2023 and 2024 datasets, because the underlying
# economic model differs.
#
# Prefer `hash_id` when you have a choice. `urid` still works and appears in
# older examples, but HashId is the identifier IMPLAN is standardizing on.
#
# Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions


# The values accepted by the `regionTypeFilter` parameter.
#
# Read them from GET /api/v1/region/RegionTypes rather than hardcoding, which is
# what the Regions workflow demonstrates. They are listed here so a typo fails
# against this vector rather than as an empty result.
#
# For Canadian data, "State" filters to Provinces and "County" to Economic
# Regions.
REGION_TYPES <- c(
  "Country", "State", "Msa", "County", "CongressionalDistrict", "Zipcode"
)


# Where a region's economic model is in the build process.
#
# A newly combined region starts at "New" and is only usable at "Complete".
# Anything else means waiting, and "Error" means it will never finish.
MODEL_BUILD_STATUS <- c(
  NEW = "New", IN_PROGRESS = "InProgress", COMPLETE = "Complete", ERROR = "Error"
)


# One region, as the API returns it.
#
# The identifier fields are populated selectively: an IMPLAN-defined region has a
# `urid`, a region you combined yourself has a `user_model_id` and no
# `fips_code`, and both have a `hash_id`.
region_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(
      hash_id = "",
      urid = NULL,
      user_model_id = NULL,
      description = "",
      model_id = NULL,
      model_build_status = "",

      # Totals for the region, useful as a sanity check that you picked the
      # right one.
      employment = NULL,
      output = NULL,
      value_added = NULL,

      aggregation_scheme_id = NULL,
      dataset_id = NULL,
      dataset_description = "",

      # Geographic codes, whichever applies: FIPS in the US, province in Canada,
      # M49 internationally.
      fips_code = NULL,
      province_code = NULL,
      m49_code = NULL,
      geo_id = NULL,
      sgc_fuller_code = NULL,

      region_type = "",
      region_type_description = "",
      has_accessible_children = FALSE,

      # Whether this region can take part in a multi-regional (MRIO) analysis.
      # The MrioProject workflow checks this before building a project.
      is_mrio_allowed = FALSE
    ),
    class_name = "implan_region"
  )
}


# TRUE when the economic model is ready to run impacts against.
is_built <- function(region) {
  identical(region$model_build_status, MODEL_BUILD_STATUS[["COMPLETE"]])
}


# TRUE for a region you combined or customized, rather than an IMPLAN one.
is_user_defined <- function(region) !is.null(region$user_model_id)


# One line naming the region and its identifiers, for the console.
describe.implan_region <- function(x, ...) {
  parts <- if (nzchar(x$description)) x$description else "(unnamed)"
  parts <- c(parts, paste0("hashId=", x$hash_id))
  if (!is.null(x$urid)) {
    parts <- c(parts, paste0("urid=", x$urid))
  }
  if (nzchar(x$model_build_status)) {
    parts <- c(parts, x$model_build_status)
  }
  paste(parts, collapse = "  ")
}


# The body for combining two or more regions into one.
#
# Supply the regions through `hash_ids`, `urids`, or both; two or more regions
# are required between them. HashId is the identifier IMPLAN is standardizing on,
# so these samples use it. The description becomes the new region's name and has
# to be unique for your account, which is why the samples put a timestamp in it.
#
# Regions being combined must come from the same dataset, must not overlap, and
# must not nest inside one another: a state and a county within it cannot be
# combined.
combine_region_request <- function(description, hash_ids = NULL, urids = NULL) {
  request_body <- list(description = description)
  if (!is.null(hash_ids)) {
    request_body$hash_ids <- as.character(hash_ids)
  }
  if (!is.null(urids)) {
    request_body$urids <- as.integer(urids)
  }
  request_body
}
