# Workflow 8: BulkFromCsv.
#
# Goal: drive many regions, projects, and runs from input files.
#
# This is what batch work looks like in practice. An analyst keeps the study
# areas and the events in spreadsheets, and the script turns them into combined
# regions, one project per region, and a final project holding all of them.
#
# Three habits make the difference between a script that finishes and one that
# trips the rate limit or falls over halfway:
#
#   - Look up regions once and cache the lookup. The FIPS-to-region map is built
#     from two calls per state, not one call per county.
#   - Reuse what already exists. Re-running finds the regions, the folder, and
#     the projects it made last time instead of failing on duplicate names.
#   - Throttle. httr2's rate limiter is switched on for this workflow, because a
#     loop over hundreds of regions will otherwise earn a 429 and then a ban.
#
# Input files, all in `data/`:
#
#   state_based.csv   fips, region_description, model_name
#   county_based.csv  fips, region_description, model_name
#   demo_events.csv   Name, Code, Type, Value
#
# Rows sharing a `model_name` are combined into one region.
#
# Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
# Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects


# The folder in IMPLAN Cloud these projects are filed under.
BULK_FOLDER_NAME <- paste(TITLE_PREFIX, "- Bulk From CSV")

# Reads one input file, keeping FIPS codes as text.
#
# FIPS codes have leading zeros that matter: Alabama is 01000, and reading that
# as a number turns it into 1000, which is not a place. `colClasses` is what
# keeps them as strings.
read_input_csv <- function(path) {
  if (!file.exists(path)) {
    stop(
      sprintf("Missing input file %s. The samples ship with these in data/.", path),
      call. = FALSE
    )
  }

  read.csv(
    path,
    colClasses = "character",
    stringsAsFactors = FALSE,
    strip.white = TRUE,
    fileEncoding = "UTF-8-BOM"
  )
}


# Finds regions by FIPS code, with as few API calls as possible.
#
# All the states are fetched once. Counties are fetched per state, and only for
# the states actually referenced, then kept. A file naming forty counties across
# three states costs four calls, not forty.
#
# An environment rather than a list, because the caches have to survive being
# read from inside the loops below; R would otherwise copy the lookup on every
# change and throw the cached regions away.
region_lookup <- function(client, ids) {
  lookup <- new.env(parent = emptyenv())
  lookup$client <- client
  lookup$ids <- ids
  lookup$states <- NULL
  lookup$counties_by_state <- list()
  lookup
}


lookup_load_states <- function(lookup) {
  if (!is.null(lookup$states)) {
    return(invisible(NULL))
  }

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
  # (wiki: Regional Children)
  found <- get_region_children(
    lookup$client, lookup$ids$aggregation_scheme_id, lookup$ids$dataset_id,
    region_type = "State"
  )

  states <- list()
  for (region in found) {
    if (!is.null(region$fips_code) && nzchar(region$fips_code)) {
      states[[region$fips_code]] <- region
    }
  }

  lookup$states <- states
  log_info("  cached %d states", length(states))
  invisible(NULL)
}


lookup_load_counties <- function(lookup, state_fips) {
  cached <- lookup$counties_by_state[[state_fips]]
  if (!is.null(cached)) {
    return(cached)
  }

  lookup_load_states(lookup)
  state <- lookup$states[[state_fips]]
  if (is.null(state)) {
    stop(sprintf("No state with FIPS code %s.", state_fips), call. = FALSE)
  }

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children
  # (wiki: Regional Children)
  found <- get_region_children(
    lookup$client, lookup$ids$aggregation_scheme_id, lookup$ids$dataset_id,
    parent_hash_id_or_urid = state$hash_id,
    region_type = "County"
  )

  counties <- list()
  for (region in found) {
    if (!is.null(region$fips_code) && nzchar(region$fips_code)) {
      counties[[region$fips_code]] <- region
    }
  }

  lookup$counties_by_state[[state_fips]] <- counties
  log_info("  cached %d counties in %s", length(counties), state$description)
  counties
}


# Returns the region for a FIPS code, state or county.
#
# A state code is two digits, or five ending in three zeros.
lookup_find <- function(lookup, fips) {
  fips <- trimws(fips)
  is_state <- nchar(fips) == 2L || (nchar(fips) == 5L && endsWith(fips, "000"))
  state_fips <- substr(fips, 1, 2)

  if (is_state) {
    lookup_load_states(lookup)
    state <- lookup$states[[state_fips]]
    if (is.null(state)) {
      stop(sprintf("No state with FIPS code %s.", fips), call. = FALSE)
    }
    return(state)
  }

  counties <- lookup_load_counties(lookup, state_fips)
  county <- counties[[fips]]
  if (is.null(county)) {
    stop(
      sprintf(
        "No county with FIPS code %s in state %s. Check the code against the current data year.",
        fips, state_fips
      ),
      call. = FALSE
    )
  }
  county
}


# Turns the rows of one input file into built regions, one per model name.
build_models <- function(client, ids, rows, lookup) {
  built <- list()

  for (model_name in unique(rows$model_name)) {
    fips_codes <- rows$fips[rows$model_name == model_name]

    # Naming the region for the scheme and dataset means the same input file can
    # be run against several data years without a name collision.
    description <- sprintf(
      "%s %s %s-%s",
      TITLE_PREFIX, model_name, ids$aggregation_scheme_id, ids$dataset_id
    )

    existing <- find_existing_user_region(
      client, ids$aggregation_scheme_id, ids$dataset_id, description
    )
    if (!is.null(existing) && is_built(existing)) {
      log_info("  %s already built, reusing it", model_name)
      built <- c(built, list(existing))
      next
    }

    members <- lapply(fips_codes, function(fips) lookup_find(lookup, fips))

    if (length(members) == 1L) {
      # One region needs no combining; use IMPLAN's own region directly.
      log_info(
        "  %s is a single region (%s), using it as is",
        model_name, members[[1]]$description
      )
      built <- c(built, list(members[[1]]))
      next
    }

    log_info("  %s: combining %d regions", model_name, length(members))

    # POST /api/v1/region/build/combined/{aggregationSchemeId}
    # (wiki: Combine Regions)
    combined <- build_combined_region(
      client, ids$aggregation_scheme_id,
      combine_region_request(
        description = description,
        hash_ids = vapply(members, function(region) region$hash_id, character(1))
      )
    )

    # GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
    built <- c(built, list(wait_for_region_build(client, combined$hash_id)))
    log_info("    built as %s", combined$hash_id)
  }

  built
}


# Creates one event per row of the events file.
#
# Two event types are covered: an Industry Output event, where the code names an
# industry, and a Commodity Output event, where it names a commodity. Add another
# branch here to support more.
add_events_from_csv <- function(client, project_id, rows) {
  created <- list()

  for (index in seq_len(nrow(rows))) {
    row <- rows[index, ]
    title <- unique_title(row$Name)
    code <- as.integer(row$Code)
    value <- as.numeric(row$Value)
    kind <- tolower(trimws(row$Type))

    event <- if (identical(kind, "industry output")) {
      industry_output_event(title = title, industry_code = code, output = value)
    } else if (identical(kind, "commodity output")) {
      commodity_output_event(title = title, commodity_code = code, output = value)
    } else {
      stop(
        sprintf(
          paste0(
            "Event type '%s' in demo_events.csv is not one this workflow builds. Add a ",
            "branch for it in add_events_from_csv()."
          ),
          row$Type
        ),
        call. = FALSE
      )
    }

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    created <- c(created, list(create_event(client, project_id, event)))
  }

  log_info("    added %d events", length(created))
  created
}


# Runs one project, waits for it, and saves its reports. Returns the run id, or
# NULL when the run did not complete.
run_and_download <- function(client, project, label) {
  # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
  run_id <- run_impact(client, project$id)
  log_info("    run %d started", run_id)

  completed <- tryCatch(
    {
      # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
      wait_for_impact(client, run_id)
      TRUE
    },
    error = function(condition) {
      # One failed run should not stop a batch of fifty. Report it and carry on.
      log_info("    run %d did not complete: %s", run_id, conditionMessage(condition))
      FALSE
    }
  )

  if (!isTRUE(completed)) {
    return(NULL)
  }

  destination <- file.path(
    reports_directory(), BULK_FOLDER_NAME, sprintf("%s-%d", label, run_id)
  )
  filters <- result_filters(year = current_dollar_year())

  for (report in STANDARD_REPORTS) {
    csv_text <- report$fetch(client, run_id, filters)
    save_csv(csv_text, file.path(destination, paste0(report$label, ".csv")))
  }

  run_id
}


bulk_from_csv_workflow <- function() {
  client <- create_client()

  # Bulk work needs the throttle. Without it, a few hundred region calls earn a
  # 429 and then a temporary ban.
  set_rate_limit(client, REGION_REQUESTS_PER_MINUTE)

  # Step 1. Resolve identifiers and read the input files.
  log_heading("Step 1: resolve identifiers and read the input files")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  state_rows <- read_input_csv(file.path(data_directory(), "state_based.csv"))
  county_rows <- read_input_csv(file.path(data_directory(), "county_based.csv"))
  event_rows <- read_input_csv(file.path(data_directory(), "demo_events.csv"))
  log_info(
    "  %d state rows, %d county rows, %d event rows",
    nrow(state_rows), nrow(county_rows), nrow(event_rows)
  )

  # Step 2. Build the combined regions. The lookup is shared so the state list is
  # fetched once for both files.
  log_heading("Step 2: build the combined regions")
  lookup <- region_lookup(client, ids)
  models <- c(
    build_models(client, ids, state_rows, lookup),
    build_models(client, ids, county_rows, lookup)
  )
  log_info("  %d regions ready", length(models))

  # Step 3. A folder to keep the projects together.
  log_heading("Step 3: find or create the folder")

  # GET /api/v1/impact/folder, then POST if needed  (wiki: Projects, folders)
  folder <- find_or_create_folder(client, BULK_FOLDER_NAME)
  log_info("  folder '%s' id %s", folder$title, folder$id)

  # Step 4. One project per region.
  log_heading("Step 4: one Project per region")
  dollar_year <- current_dollar_year()

  for (model in models) {
    log_info("  %s", model$description)

    # POST /api/v1/impact/project  (wiki: Create Project)
    project <- create_project(client, new_project(
      title = unique_title(model$description),
      aggregation_scheme_id = ids$aggregation_scheme_id,
      household_set_id = ids$household_set_id,
      folder_id = folder_id_for_project(folder)
    ))

    created <- add_events_from_csv(client, project$id, event_rows)

    # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    create_group(client, project$id, new_group(
      title = unique_title(model$description),
      hash_id = model$hash_id,
      dataset_id = ids$dataset_id,
      dollar_year = dollar_year,
      group_events = lapply(created, function(event) group_event(event$id))
    ))

    run_and_download(client, project, substr(model$description, 1, 40))
  }

  # Step 5. One project holding every region, so the whole set can be read as a
  # single analysis.
  log_heading("Step 5: one Project holding every region")

  combined_project <- create_project(client, new_project(
    title = unique_title("All Models"),
    aggregation_scheme_id = ids$aggregation_scheme_id,
    household_set_id = ids$household_set_id,
    folder_id = folder_id_for_project(folder)
  ))
  log_info("  %s", describe(combined_project))

  # The events are created once and shared by every group, exactly as in the
  # MultiEventToMultiGroup workflow.
  all_events <- add_events_from_csv(client, combined_project$id, event_rows)
  event_links <- lapply(all_events, function(event) group_event(event$id))

  for (model in models) {
    create_group(client, combined_project$id, new_group(
      title = unique_title(model$description),
      hash_id = model$hash_id,
      dataset_id = ids$dataset_id,
      dollar_year = dollar_year,
      group_events = event_links
    ))
  }
  log_info("  %d groups added", length(models))

  run_and_download(client, combined_project, "all-models")

  log_heading("Done")
  log_info("Folder:  %s", BULK_FOLDER_NAME)
  log_info("Regions: %d", length(models))
  log_info("Reports: %s", file.path(reports_directory(), BULK_FOLDER_NAME))
  log_info("")
  log_info("Delete the folder and its projects from IMPLAN Cloud when you are done.")

  invisible(NULL)
}
