# Workflow 6: MultiEventToMultiGroup.
#
# Goal: apply the same set of events to several regions at once.
#
# This is the shape most real analyses take. A mixed-use development has
# restaurants on the ground floor and two bands of apartments above it, and the
# question is which of three states to build it in. That is three events and
# three groups, with every event in every group, and the answer falls out of the
# results filtered by region.
#
# The pattern is a nested loop: create each event once, then create one group per
# region holding all of them. Events are owned by the project, not by a group, so
# they are created once and referenced many times.
#
# Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
# Support: MRIO vs. Larger Study Area, on when separate groups are the right model
# https://support.implan.com/hc/en-us/articles/115002799373


# The states to compare. Change this vector to compare different ones.
COMPARISON_STATES <- c("Oregon", "Wisconsin", "North Carolina")

# The restaurants on the ground floor, by name rather than by code.
RESTAURANT_INDUSTRY <- "Full-service restaurants"

# The two household income brackets, by specification code. These are checked
# against the project's own specification list in step 4 rather than trusted.
HOUSEHOLD_BRACKETS <- list(
  list(code = 10002, label = "Households 15-30k", value = 25000),
  list(code = 10005, label = "Households 50-70k", value = 125000)
)


multi_event_to_multi_group_workflow <- function(project_id = NULL) {
  client <- create_client()

  # Step 1. Resolve the identifiers.
  log_heading("Step 1: resolve the identifiers")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. Get a project to work in. An existing empty one can be passed in;
  # otherwise one is created here.
  log_heading("Step 2: the Project")
  if (is.null(project_id)) {
    # POST /api/v1/impact/project  (wiki: Create Project)
    project <- create_project(client, new_project(
      title = unique_title("Multi Event Multi Group"),
      aggregation_scheme_id = ids$aggregation_scheme_id,
      household_set_id = ids$household_set_id
    ))
    log_info("  created %s", describe(project))
  } else {
    # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
    project <- get_project(client, project_id)
    log_info("  using existing %s", describe(project))
  }

  # Step 3. The restaurant event needs an industry code.
  log_heading("Step 3: find the restaurant industry")

  # GET /api/v1/IndustryCodes/{aggregationSchemeId}
  # (wiki: Industry Codes by Aggregation Scheme)
  codes <- get_industry_codes_for_scheme(client, ids$aggregation_scheme_id)
  restaurants <- find_industry_by_description(codes, RESTAURANT_INDUSTRY)
  log_info("  %s is code %s here", restaurants$description, restaurants$code)
  log_info("  (it is a different code in other Industry Sets, which is why this")
  log_info("   sample looks it up by name)")

  # Step 4. Household Income events take a specification code rather than an
  # industry code, so read the valid ones for this project first.
  log_heading("Step 4: read the Household Income specification codes")

  # GET /api/v1/impact/project/{projectId}/eventtype/HouseholdIncome/specification
  # (wiki: Get Event Specifications)
  specifications <- get_event_specifications(client, project$id, "HouseholdIncome")
  available <- vapply(specifications, function(spec) as.character(spec$code), character(1))
  log_info("  %d income brackets available:", length(specifications))
  for (spec in specifications) {
    log_info("    %s", spec$name)
  }

  for (bracket in HOUSEHOLD_BRACKETS) {
    if (!as.character(bracket$code) %in% available) {
      stop(
        sprintf(
          "Household income code %s (%s) is not valid for this Project. Available codes: %s.",
          bracket$code, bracket$label, paste(sort(available), collapse = ", ")
        ),
        call. = FALSE
      )
    }
  }

  # Step 5. Create the events. Each one is created once and will be referenced by
  # all three groups.
  log_heading("Step 5: add the Events")

  # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
  restaurant_event <- create_event(client, project$id, industry_output_event(
    title = unique_title("Restaurants"),
    industry_code = restaurants$code,
    output = 1000000
  ))
  created <- list(restaurant_event)
  log_info("  %s", describe(restaurant_event))

  for (bracket in HOUSEHOLD_BRACKETS) {
    household_event <- create_event(client, project$id, household_income_event(
      title = unique_title(bracket$label),
      household_income_code = bracket$code,
      value = bracket$value
    ))
    created <- c(created, list(household_event))
    log_info("  %s", describe(household_event))
  }

  # Step 6. Find the states.
  log_heading("Step 6: find the Regions")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
  # (wiki: Regional Children)
  states <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = "State"
  )
  chosen <- lapply(COMPARISON_STATES, function(name) {
    find_region_by_description(states, name)
  })
  for (state in chosen) {
    log_info("  %s", describe(state))
  }

  # Step 7. One group per region, each holding every event. This is the nested
  # loop the workflow exists to show: events on the inside, regions on the
  # outside, and the group titles distinct.
  log_heading("Step 7: one Group per Region, each holding every Event")
  dollar_year <- current_dollar_year()
  event_links <- lapply(created, function(event) group_event(event$id))

  for (state in chosen) {
    # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    group <- create_group(client, project$id, new_group(
      # Group titles have to be distinct within a project.
      title = unique_title(state$description),
      hash_id = state$hash_id,
      dataset_id = ids$dataset_id,
      dollar_year = dollar_year,
      group_events = event_links
    ))
    log_info("  %s", describe(group))
  }

  # Step 8. Read it back.
  log_heading("Step 8: read the Groups back")

  # GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
  all_groups <- get_groups(client, project$id)
  log_info("  %d groups, each with %d events", length(all_groups), length(created))

  log_heading("Done")
  log_info("Project id: %s", project$id)
  log_info("%d events across %d groups", length(created), length(all_groups))
  log_info("")
  log_info("Run it, then filter the results by region to compare the states:")
  log_info("  Rscript main.R run-impact-analysis --project-id %s", project$id)

  invisible(project)
}
