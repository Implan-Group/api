# Region endpoints: finding, combining, and building regions.
#
# Regions form a hierarchy. The top-level region for a United States scheme is
# the country; its children are the states; a state's children are its counties,
# MSAs, and congressional districts; a county's children are its ZIP codes.
# International schemes have no top-level region, so start from the country
# children instead.
#
# Alongside IMPLAN's regions sit your own: combined regions you built from
# several others, and customized regions where you edited the underlying economic
# data. Those are the "user" regions.
#
# Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
# Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions


# Lists the values accepted by the `regionTypeFilter` parameter.
#
# GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
#
# This is also the cheapest authenticated call in the API, which is why the auth
# helper uses it to test a cached token.
get_region_types <- function(client) {
  unlist(get_json(client, "/api/v1/region/RegionTypes"), use.names = FALSE)
}


# Reads the region at the top of the hierarchy, usually a country.
#
# GET /api/v1/region/{aggregationSchemeId}/{datasetId}
# (wiki: Regions - Top Level)
#
# International schemes have no top-level region and answer 422 here; use
# `get_region_children()` with "Country" for those.
get_top_level_region <- function(client, aggregation_scheme_id, dataset_id) {
  payload <- get_json(
    client,
    sprintf("/api/v1/region/%s/%s", aggregation_scheme_id, dataset_id)
  )
  region_from_api(payload)
}


# Reads one region by HashId or URID.
#
# GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}
# (wiki: Get Region by Id)
get_region <- function(client, aggregation_scheme_id, dataset_id, hash_id_or_urid) {
  payload <- get_json(
    client,
    sprintf("/api/v1/region/%s/%s/%s", aggregation_scheme_id, dataset_id, hash_id_or_urid)
  )
  region_from_api(payload)
}


# Lists the regions inside a region, optionally filtered to one type.
#
# GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children
# GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}/children
# (wiki: Regional Children)
#
# Omitting the parent starts from the top-level region, so asking for "State"
# with no parent gives every state in the country.
#
# The filter reaches through the hierarchy: asking a state for "Zipcode" returns
# the ZIP codes of its counties, not nothing.
#
# Worth knowing for bulk work: every region in this response carries its own
# `modelBuildStatus`, so one call tells you both which regions exist and which of
# them are already built. There is no separate endpoint for that, and asking
# region by region is what makes a bulk script trip the rate limit.
get_region_children <- function(client,
                                aggregation_scheme_id,
                                dataset_id,
                                parent_hash_id_or_urid = NULL,
                                region_type = NULL) {
  path <- if (is.null(parent_hash_id_or_urid)) {
    sprintf("/api/v1/region/%s/%s/children", aggregation_scheme_id, dataset_id)
  } else {
    sprintf(
      "/api/v1/region/%s/%s/%s/children",
      aggregation_scheme_id, dataset_id, parent_hash_id_or_urid
    )
  }

  query <- list()
  if (!is.null(region_type)) {
    query$regionTypeFilter <- region_type
  }

  list_from_api(get_json(client, path, query = query), region_from_api)
}


# Lists your combined and customized regions for one scheme and dataset.
#
# GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
# (wiki: Get User Regions by Aggregation Scheme)
get_user_regions_for_scheme <- function(client, aggregation_scheme_id, dataset_id) {
  payload <- get_json(
    client,
    sprintf("/api/v1/region/%s/%s/user", aggregation_scheme_id, dataset_id)
  )
  list_from_api(payload, region_from_api)
}


# Lists all of your combined and customized regions.
#
# GET /api/v1/region/user  (wiki: Get User Regions)
#
# On an account with many custom schemes this call can answer 503 while IMPLAN
# rebuilds its region cache, and the first request can exceed the gateway's
# 30-second limit. Narrowing it with a scheme and dataset, or using the
# scheme-scoped call above, is more reliable.
get_user_regions <- function(client, aggregation_scheme_id = NULL, dataset_id = NULL) {
  query <- list()
  if (!is.null(aggregation_scheme_id)) {
    query$aggregationSchemeId <- aggregation_scheme_id
  }
  if (!is.null(dataset_id)) {
    query$datasetId <- dataset_id
  }

  list_from_api(get_json(client, "/api/v1/region/user", query = query), region_from_api)
}


# Reads one of your regions by HashId.
#
# GET /api/v1/region/user/{hashId}  (wiki: Get User Region)
#
# This is the endpoint to poll while a combined region builds. It reads one
# region rather than the whole list, so it stays fast and avoids the 503 the list
# can return.
#
# An unknown HashId comes back as an empty body rather than a 404, so NULL here
# means "no such region of yours".
get_user_region <- function(client, hash_id) {
  payload <- get_json(client, sprintf("/api/v1/region/user/%s", hash_id))
  if (is.null(payload) || length(payload) == 0L) {
    return(NULL)
  }
  region_from_api(payload)
}


# Combines two or more regions into one and starts building its model.
#
# POST /api/v1/region/build/combined/{aggregationSchemeId}
# (wiki: Combine Regions)
#
# Returns immediately with the new region at `modelBuildStatus` of "New". The
# model is not usable until that reads "Complete", which is what
# `wait_for_region_build()` waits for.
#
# The regions being combined must come from the same dataset, must not overlap,
# and must not nest: a state and a county inside it cannot be combined. The
# description has to be unique for your account.
#
# The endpoint answers with an array holding the single new region.
build_combined_region <- function(client, aggregation_scheme_id, request_body) {
  payload <- post_json(
    client,
    sprintf("/api/v1/region/build/combined/%s", aggregation_scheme_id),
    body = to_api(request_body)
  )

  built <- list_from_api(payload, region_from_api)
  if (length(built) != 1L) {
    stop(
      sprintf("Expected one combined region back, got %d.", length(built)),
      call. = FALSE
    )
  }
  built[[1]]
}


# Builds several IMPLAN regions at once, without combining them.
#
# POST /api/v1/region/build-and-return/{aggregationSchemeId}
# (wiki: Build and Return Regions)
#
# The body is a plain array of HashIds. Use this when a bulk job needs regions
# whose models have not been built yet: one call queues all of them instead of
# one call each.
#
# Like the combined build, this returns before the models are ready.
build_and_return_regions <- function(client, aggregation_scheme_id, hash_ids) {
  payload <- post_json(
    client,
    sprintf("/api/v1/region/build-and-return/%s", aggregation_scheme_id),
    # An unnamed list so jsonlite renders a JSON array, even for one HashId.
    body = unname(as.list(hash_ids))
  )
  list_from_api(payload, region_from_api)
}


# Polls until a combined or customized region has finished building.
#
# Polls GET /api/v1/region/user/{hashId} rather than the user-regions list: it is
# one region instead of all of them, and it does not hit the 503 the list can
# return on a busy account.
#
# Stops on a build that reports "Error", and on a build that has not finished
# inside `timeout_seconds`. Never poll a heavy data endpoint to find out whether
# a model is ready; those answer with an error until it is, which is slow and
# reads like a different problem.
wait_for_region_build <- function(client,
                                  hash_id,
                                  timeout_seconds = REGION_BUILD_TIMEOUT_SECONDS,
                                  poll_seconds = REGION_BUILD_POLL_SECONDS) {
  deadline <- Sys.time() + timeout_seconds
  last_status <- ""

  repeat {
    region <- get_user_region(client, hash_id)

    if (!is.null(region)) {
      if (!identical(region$model_build_status, last_status)) {
        last_status <- region$model_build_status
        log_info(
          "  region %s: %s",
          hash_id,
          if (nzchar(last_status)) last_status else "(no status)"
        )
      }

      if (is_built(region)) {
        return(region)
      }

      if (identical(region$model_build_status, MODEL_BUILD_STATUS[["ERROR"]])) {
        stop(
          sprintf(
            paste0(
              "The model for region %s failed to build. Try the request again, or ",
              "contact support@implan.com if it repeats."
            ),
            hash_id
          ),
          call. = FALSE
        )
      }
    }

    if (Sys.time() >= deadline) {
      stop(
        sprintf(
          paste0(
            "Region %s was still building after %d seconds, last status '%s'. It may ",
            "still finish; check your regions in IMPLAN Cloud."
          ),
          hash_id, timeout_seconds, if (nzchar(last_status)) last_status else "unknown"
        ),
        call. = FALSE
      )
    }

    Sys.sleep(poll_seconds)
  }
}


# Finds one region by its exact description, matched case-insensitively.
#
# Region descriptions carry their state, as in "Lane County, OR", so they are
# unique within a region type.
find_region_by_description <- function(regions, description) {
  wanted <- tolower(description)
  for (region in regions) {
    if (identical(tolower(region$description), wanted)) {
      return(region)
    }
  }

  stop(
    sprintf(
      paste0(
        "No region named '%s' in this list of %d regions. Check the spelling, ",
        "including the state abbreviation."
      ),
      description, length(regions)
    ),
    call. = FALSE
  )
}


# Returns one of your regions by name, or NULL if you have not built it.
#
# Bulk workflows call this first so that re-running them reuses the regions they
# built last time instead of failing on a duplicate name.
find_existing_user_region <- function(client, aggregation_scheme_id, dataset_id, description) {
  existing <- tryCatch(
    get_user_regions_for_scheme(client, aggregation_scheme_id, dataset_id),
    implan_api_error = function(condition) {
      if (condition$status == 503L) {
        # The region cache is rebuilding. Treat it as "cannot tell", and let the
        # caller try the build, which reports a duplicate name clearly.
        log_info(
          paste0(
            "  the user-regions list is temporarily unavailable (503); continuing ",
            "without checking for an existing region"
          )
        )
        return(NULL)
      }
      stop(condition)
    }
  )

  if (is.null(existing)) {
    return(NULL)
  }

  wanted <- tolower(description)
  for (region in existing) {
    if (identical(tolower(region$description), wanted)) {
      return(region)
    }
  }
  NULL
}
