# Workflow 11: MrioProject.
#
# Goal: multi-regional input-output analysis, where activity in one region shows
# up as effects in another.
#
# An ordinary project treats each of its regions in isolation. Build a factory in
# Oregon and the results show Oregon's supply chain; anything the factory buys
# from Wisconsin leaks out of the model and is never counted. That is usually the
# wrong answer when the regions are economically linked.
#
# MRIO keeps the link. With `isMrio` set on the project, IMPLAN traces demand
# from one region into the others in the same project, so Wisconsin shows
# indirect and induced effects from an event that only happened in Oregon.
#
# The shape is:
#
#   - One project, with `is_mrio` set to TRUE.
#   - One event, in one region.
#   - A group per region, including the region with no activity of its own. That
#     group exists so there is somewhere for the spillover to be reported.
#
# Reading the results filtered by region is what makes the point: Wisconsin's
# numbers are non-zero although nothing was built there.
#
# Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
# Support: MRIO: Introduction to Multi-Regional Input-Output Analysis
# https://support.implan.com/hc/en-us/articles/115009713448


# The region the event happens in, and the region that should show spillover.
MRIO_SOURCE_REGION <- "Oregon"
MRIO_LINKED_REGION <- "Wisconsin"

# An industry with a wide supply chain, so the cross-region effect is visible.
MRIO_INDUSTRY_NAME <- "Full-service restaurants"
MRIO_EVENT_OUTPUT <- 10000000


mrio_project_workflow <- function() {
  client <- create_client()

  # Step 1. Resolve identifiers.
  log_heading("Step 1: resolve the identifiers")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. Find both regions, and check each allows MRIO. Not every region does,
  # and finding out here is better than after a run produces nothing.
  log_heading("Step 2: find the regions and check they allow MRIO")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
  # (wiki: Regional Children)
  states <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = "State"
  )

  source_region <- find_region_by_description(states, MRIO_SOURCE_REGION)
  linked_region <- find_region_by_description(states, MRIO_LINKED_REGION)

  for (region in list(source_region, linked_region)) {
    log_info("  %s  MRIO allowed: %s", describe(region), region$is_mrio_allowed)
    if (!isTRUE(region$is_mrio_allowed)) {
      stop(
        sprintf(
          "%s cannot take part in an MRIO analysis. Pick a different region.",
          region$description
        ),
        call. = FALSE
      )
    }
  }

  # Step 3. Create the project with MRIO switched on. This is the one flag that
  # separates this workflow from CreateProject, and it cannot be changed later.
  log_heading("Step 3: create the Project with MRIO enabled")

  # POST /api/v1/impact/project  (wiki: Create Project)
  project <- create_project(client, new_project(
    title = unique_title("MRIO"),
    aggregation_scheme_id = ids$aggregation_scheme_id,
    household_set_id = ids$household_set_id,
    is_mrio = TRUE
  ))
  log_info("  %s", describe(project))
  log_info("  isMrio: %s", project$is_mrio)

  # Step 4. One event, in the source region only.
  log_heading("Step 4: add one Event")

  # GET /api/v1/IndustryCodes/{aggregationSchemeId}
  # (wiki: Industry Codes by Aggregation Scheme)
  codes <- get_industry_codes_for_scheme(client, ids$aggregation_scheme_id)
  industry <- find_industry_by_description(codes, MRIO_INDUSTRY_NAME)

  # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
  event <- create_event(client, project$id, industry_output_event(
    title = unique_title(paste("Restaurants in", MRIO_SOURCE_REGION)),
    industry_code = industry$code,
    output = MRIO_EVENT_OUTPUT
  ))
  log_info("  %s", describe(event))
  log_info(
    "  $%s output in %s",
    format(MRIO_EVENT_OUTPUT, big.mark = ",", scientific = FALSE),
    MRIO_SOURCE_REGION
  )

  # Step 5. Two groups. The source group holds the event. The linked group holds
  # the same event too, scaled to almost nothing.
  #
  # On that scaling: a group with no events at all is the cleaner illustration,
  # but the API requires a group to carry at least one event, so the linked
  # region gets the event at a negligible scaling factor. Its own direct effect
  # is therefore near zero, and essentially everything reported for it is
  # spillover from the source region, which is the effect this workflow exists to
  # show.
  log_heading("Step 5: a Group for each region")
  dollar_year <- current_dollar_year()

  # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
  source_group <- create_group(client, project$id, new_group(
    title = unique_title(MRIO_SOURCE_REGION),
    hash_id = source_region$hash_id,
    dataset_id = ids$dataset_id,
    dollar_year = dollar_year,
    group_events = list(group_event(event$id))
  ))
  log_info("  %s", describe(source_group))

  linked_group <- create_group(client, project$id, new_group(
    title = unique_title(MRIO_LINKED_REGION),
    hash_id = linked_region$hash_id,
    dataset_id = ids$dataset_id,
    dollar_year = dollar_year,
    group_events = list(group_event(event$id, scaling_factor = 0.01))
  ))
  log_info("  %s  (event scaled to 0.01)", describe(linked_group))

  # Step 6. Run it.
  log_heading("Step 6: run the impact")

  # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
  run_id <- run_impact(client, project$id)
  log_info("  run id %d", run_id)

  # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
  wait_for_impact(client, run_id)
  log_info("  complete")

  # Step 7. Read the results once per region. The filter is what separates the
  # two, and comparing them is the point of the workflow.
  log_heading("Step 7: read the results region by region")
  destination <- file.path(reports_directory(), sprintf("MRIO-%d", run_id))

  for (region in list(source_region, linked_region)) {
    filters <- result_filters(year = dollar_year, regions = region$description)

    # GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?regions=...
    # (wiki: Results - Summary Economic Indicators)
    csv_text <- get_summary_economic_indicators(client, run_id, filters)
    path <- save_csv(
      csv_text,
      file.path(
        destination,
        sprintf("Summary Economic Indicators - %s.csv", safe_file_name(region$description))
      )
    )

    log_info(
      "  %s: %d rows in %s",
      region$description, csv_data_row_count(csv_text), basename(path)
    )
  }

  log_heading("Done")
  log_info("Project id: %s", project$id)
  log_info("Run id:     %d", run_id)
  log_info("Reports:    %s", destination)
  log_info("")
  log_info("Compare the two files. %s carries indirect and induced", MRIO_LINKED_REGION)
  log_info("effects from activity that only happened in %s. In a project", MRIO_SOURCE_REGION)
  log_info("without MRIO those effects leak out of the model and are lost.")

  invisible(run_id)
}
