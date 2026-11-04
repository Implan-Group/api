# Workflow 3: Regions.
#
# Goal: navigate the region hierarchy and find the regions an analysis will use.
#
# Regions nest. For a United States scheme the top-level region is the country,
# its children are the states, and a state's children are its counties, MSAs, and
# congressional districts. The filter reaches down through that hierarchy, so
# asking a state for ZIP codes works even though ZIP codes are children of
# counties.
#
# A region is identified by `hashId`, and that identifier is specific to one
# Aggregation Scheme and one Dataset. The same county has a different HashId in a
# different scheme or data year, so never carry one between them.
#
# Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions


# The states the later workflows use. Looked up by description so the sample does
# not depend on a HashId that changes with the data year.
TARGET_STATES <- c("Oregon", "Wisconsin", "North Carolina")


regions_workflow <- function() {
  client <- create_client()

  # Step 1. Resolve the scheme and dataset. Region identifiers only mean
  # something inside these two, so they come first.
  log_heading("Step 1: resolve the Aggregation Scheme and Dataset")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. The top of the hierarchy. For a US scheme this is the country.
  log_heading("Step 2: the top-level region")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}
  # (wiki: Regions - Top Level)
  country <- get_top_level_region(client, ids$aggregation_scheme_id, ids$dataset_id)
  log_info("  %s", describe(country))
  log_info(
    "  employment %s    output %s",
    format(field_or(country, "employment", 0), big.mark = ",", scientific = FALSE),
    format(field_or(country, "output", 0), big.mark = ",", scientific = FALSE)
  )
  log_info("  International schemes have no top-level region and answer 422 here;")
  log_info("  start from the country children instead.")

  # Step 3. The states. No parent region means "children of the top-level
  # region", so this is every state in the country.
  log_heading("Step 3: the states")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
  # (wiki: Regional Children)
  states <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = "State"
  )
  log_info("  %d states and equivalents", length(states))

  # Find the three the other workflows use. Matching on description rather than
  # on a HashId is what keeps these samples working across data years.
  for (name in TARGET_STATES) {
    log_info("    %s", describe(find_region_by_description(states, name)))
  }

  # Step 4. One level further down. Counties are children of a state.
  log_heading("Step 4: the counties inside one state")
  oregon <- find_region_by_description(states, "Oregon")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children?regionTypeFilter=County
  # (wiki: Regional Children)
  counties <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    parent_hash_id_or_urid = oregon$hash_id,
    region_type = "County"
  )
  log_info("  %d counties in %s", length(counties), oregon$description)

  for (county in utils::head(counties, 5)) {
    log_info("    %s", describe(county))
  }
  if (length(counties) > 5) {
    log_info("    ... and %d more", length(counties) - 5)
  }

  log_info("")
  log_info("  Every region above carries its own model build status, so this one")
  log_info("  call tells you both which regions exist and which are ready to use.")
  built <- sum(vapply(counties, is_built, logical(1)))
  log_info("  %d of %d counties are built", built, length(counties))

  # Step 5. Read one region on its own, by HashId.
  log_heading("Step 5: read one region by HashId")
  lane <- find_region_by_description(counties, "Lane County, OR")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}
  # (wiki: Get Region by Id)
  lane_again <- get_region(client, ids$aggregation_scheme_id, ids$dataset_id, lane$hash_id)
  log_info("  %s", describe(lane_again))
  log_info("  MRIO allowed: %s", lane_again$is_mrio_allowed)

  # Step 6. Your own regions: the ones you combined or customized. A fresh
  # account has none, and that is a normal result rather than an error.
  log_heading("Step 6: your combined and customized regions")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
  # (wiki: Get User Regions by Aggregation Scheme)
  user_regions <- get_user_regions_for_scheme(
    client, ids$aggregation_scheme_id, ids$dataset_id
  )

  if (length(user_regions) > 0) {
    log_info("  %d of your own regions in this scheme and dataset:", length(user_regions))
    for (region in utils::head(user_regions, 10)) {
      log_info("    %s", describe(region))
    }
    if (length(user_regions) > 10) {
      log_info("    ... and %d more", length(user_regions) - 10)
    }

    # GET /api/v1/region/user/{hashId}  (wiki: Get User Region)
    # Reading one is faster than the list and is what to poll while a region
    # builds.
    one <- get_user_region(client, user_regions[[1]]$hash_id)
    if (!is.null(one)) {
      log_info("  read back one by HashId: %s", describe(one))
    }
  } else {
    log_info("  none yet. The CombineRegions workflow creates one.")
  }

  log_heading("Done")
  log_info(
    "HashIds from this run are good for Aggregation Scheme %s and",
    ids$aggregation_scheme_id
  )
  log_info("Dataset %s only. Look them up again for any other combination.", ids$dataset_id)

  invisible(NULL)
}
