# Workflow 4: CombineRegions.
#
# Goal: combine two counties into one region and wait for its model to build.
#
# IMPLAN builds a model for every region it publishes, but a study area is often
# not one of them: two counties either side of a state line, the six counties a
# transit authority serves, a metro area plus its exurbs. Combining regions makes
# one economic region out of several, and the result behaves like any other
# region afterwards.
#
# The important part of this workflow is the waiting. The build is asynchronous:
# the POST returns immediately with the new region at status "New", and the model
# is not usable until that reads "Complete". Poll the single-region endpoint for
# that, and never poll a heavy data export to find out, because those answer with
# an error until the model is ready and the error looks like a different problem.
#
# Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
# Support: Combining Regions
# https://support.implan.com/hc/en-us/articles/1260805784110


# Two adjacent Oregon counties. They must come from the same dataset, must not
# overlap, and must not nest inside one another, so a state and a county within
# it would be rejected.
COUNTIES_TO_COMBINE <- c("Lane County, OR", "Douglas County, OR")


combine_regions_workflow <- function() {
  client <- create_client()

  # Step 1. Resolve the scheme and dataset the combined region will belong to.
  log_heading("Step 1: resolve the Aggregation Scheme and Dataset")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. Find the counties by name and collect their HashIds.
  log_heading("Step 2: find the regions to combine")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=County
  # (wiki: Regional Children)
  all_counties <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = "County"
  )
  log_info("  %d counties in this scheme and dataset", length(all_counties))

  chosen <- lapply(COUNTIES_TO_COMBINE, function(name) {
    find_region_by_description(all_counties, name)
  })
  for (county in chosen) {
    log_info("    %s", describe(county))
  }

  # Step 3. Ask for the combination. The description has to be unique for your
  # account, so it carries a timestamp.
  log_heading("Step 3: request the combined region")
  description <- unique_title("Combined Region")

  # Re-running this workflow should not fail on a name that already exists, and
  # should not build the same region twice.
  existing <- find_existing_user_region(
    client, ids$aggregation_scheme_id, ids$dataset_id, description
  )

  if (!is.null(existing)) {
    log_info("  a region named '%s' already exists; reusing it", description)
    combined <- existing
  } else {
    log_info("  combining %d regions as '%s'", length(chosen), description)

    # POST /api/v1/region/build/combined/{aggregationSchemeId}
    # (wiki: Combine Regions)
    combined <- build_combined_region(
      client,
      ids$aggregation_scheme_id,
      combine_region_request(
        description = description,
        hash_ids = vapply(chosen, function(county) county$hash_id, character(1))
      )
    )
    log_info("  accepted: %s", describe(combined))
    log_info(
      "  status is '%s'; the model builds in the background",
      combined$model_build_status
    )
  }

  # Step 4. Wait for the model. A combined region usually finishes inside a
  # minute; the helper gives up after ten and says so rather than looping.
  log_heading("Step 4: wait for the model to build")

  # GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
  built <- wait_for_region_build(client, combined$hash_id)
  log_info("  built")
  log_info("    %s", describe(built))
  log_info(
    "    employment %s    output %s",
    format(field_or(built, "employment", 0), big.mark = ",", scientific = FALSE),
    format(field_or(built, "output", 0), big.mark = ",", scientific = FALSE)
  )

  log_heading("Done")
  log_info("Created region: %s", built$description)
  log_info("  HashId:      %s", built$hash_id)
  log_info("  userModelId: %s", field_or(built, "user_model_id", "(none)"))
  log_info("")
  log_info("Use that HashId in a Group exactly as you would an IMPLAN region.")
  log_info("Delete the region from Regions in IMPLAN Cloud when you are done.")

  invisible(built$hash_id)
}
