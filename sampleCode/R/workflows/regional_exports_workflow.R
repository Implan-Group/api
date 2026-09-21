# Workflow 9: RegionalExports.
#
# Goal: download a regional data export for many regions, without tripping the
# rate limit.
#
# Regional data exports describe a region's economy as it already is, so they
# need no project and no impact run, only a built region. Wanting one for every
# MSA, or every county in a state, is common.
#
# The naive version of this asks each region for its status, then downloads. That
# is one extra call per region, which for three thousand counties is hours of
# waiting under the published five-region-model-requests-per-minute limit. It is
# also unnecessary: the children listing already carries `modelBuildStatus` for
# every region it returns, so one call gives both the list and which of them are
# ready.
#
# So the shape here is:
#
#   1. One children call: every region, with its build status.
#   2. One build-and-return call for whichever are not built, then wait.
#   3. Download, skipping any file already on disk so a re-run resumes.
#
# The export is a parameter. RegionOverviewIndustries and the single-file GAMS
# export are named for convenience, but any report from the wiki's Regional Data
# Exports section can be passed by name.
#
# Wiki: Regional Data Exports
# https://github.com/Implan-Group/api/wiki/Regional-Data-Exports


# How many regions to ask for in one build-and-return call.
BUILD_BATCH_SIZE <- 25


# Builds the regions whose models are not ready, in batches.
ensure_built <- function(client, aggregation_scheme_id, unbuilt) {
  starts <- seq(1L, length(unbuilt), by = BUILD_BATCH_SIZE)

  for (start in starts) {
    finish <- min(start + BUILD_BATCH_SIZE - 1L, length(unbuilt))
    batch <- unbuilt[start:finish]
    log_info(
      "  requesting %d models (%d to %d of %d)",
      length(batch), start, finish, length(unbuilt)
    )

    # POST /api/v1/region/build-and-return/{aggregationSchemeId}
    # (wiki: Build and Return Regions)
    build_and_return_regions(
      client, aggregation_scheme_id,
      vapply(batch, function(region) region$hash_id, character(1))
    )

    # These are IMPLAN regions rather than user regions, so the user-region
    # endpoint does not see them. Give the queue time to work and let the
    # download step below treat a 400 as "still building".
    Sys.sleep(30)
  }

  invisible(NULL)
}


# Downloads one export for every region of a type.
#
# `limit` caps how many regions are processed, which keeps a first run short.
# Pass NULL to process all of them, and expect it to take a while: the rate
# limit, not the API's speed, sets the pace.
regional_exports_workflow <- function(region_type = "Msa",
                                      export_name = REGION_OVERVIEW_INDUSTRIES,
                                      limit = 10) {
  client <- create_client()
  set_rate_limit(client, REGION_REQUESTS_PER_MINUTE)

  # Step 1. Resolve identifiers.
  log_heading("Step 1: resolve the identifiers")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. One call for the list and the build status together. This is the step
  # that keeps the workflow inside the rate limit.
  log_heading("Step 2: list the regions, with their build status")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
  # (wiki: Regional Children)
  found <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = region_type
  )
  log_info("  %d regions of type %s", length(found), region_type)

  if (!is.null(limit) && length(found) > limit) {
    found <- found[seq_len(limit)]
    log_info("  limited to the first %d for this run", limit)
  }

  built_flags <- vapply(found, is_built, logical(1))
  unbuilt <- found[!built_flags]
  log_info("  %d already built, %d not yet", sum(built_flags), length(unbuilt))
  log_info("  (that status came from the same call as the list, so this cost")
  log_info("   one request rather than one per region)")

  # Step 3. Build whatever is missing.
  if (length(unbuilt) > 0L) {
    log_heading("Step 3: build the models that are missing")
    ensure_built(client, ids$aggregation_scheme_id, unbuilt)
  } else {
    log_heading("Step 3: nothing to build")
    log_info("  every region already has a model")
  }

  # Step 4. Download. Skipping files already on disk makes a re-run resume rather
  # than start over, which matters when the whole job takes an hour.
  log_heading("Step 4: download the export for each region")
  extension <- file_extension_for(export_name)
  destination <- file.path(
    reports_directory(),
    sprintf("%s-agg%s-ds%s", export_name, ids$aggregation_scheme_id, ids$dataset_id)
  )
  if (!dir.exists(destination)) {
    dir.create(destination, recursive = TRUE)
  }
  log_info("  into %s", destination)

  downloaded <- 0L
  skipped <- 0L
  failed <- 0L

  for (region in found) {
    path <- file.path(destination, paste0(safe_file_name(region$description), extension))

    if (file.exists(path)) {
      skipped <- skipped + 1L
      next
    }

    content <- tryCatch(
      # GET /api/v1/regions/export/{aggregationSchemeId}/{exportName}?hashId=...
      # (wiki: Regional Data Exports)
      get_export(client, ids$aggregation_scheme_id, export_name, region = region),
      implan_api_error = function(condition) {
        if (condition$status == 400L) {
          # From these endpoints a 400 nearly always means the model is still
          # building rather than that the request was wrong.
          log_info("  %s: not ready yet (400); run again later", region$description)
        } else {
          log_info("  %s: %s", region$description, describe(condition$problem))
        }
        NULL
      }
    )

    if (is.null(content)) {
      failed <- failed + 1L
      next
    }

    connection <- file(path, open = "wb")
    writeChar(content, connection, eos = NULL, useBytes = TRUE)
    close(connection)

    downloaded <- downloaded + 1L
    log_info("  %s", basename(path))
  }

  log_heading("Done")
  log_info("Downloaded: %d", downloaded)
  log_info("Skipped (already on disk): %d", skipped)
  log_info("Not ready or failed: %d", failed)
  log_info("Folder: %s", destination)
  if (failed > 0L) {
    log_info("")
    log_info("Run this again to pick up the ones that were still building.")
  }

  invisible(NULL)
}
