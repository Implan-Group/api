# Workflow 5: CreateProject.
#
# Goal: the shortest path from nothing to a project that can be run.
#
# Four things have to exist, in this order, and each depends on the one before:
#
#   1. A Project, which fixes the Aggregation Scheme and Household Set.
#   2. Events, which say what changed.
#   3. A Region to apply them to.
#   4. A Group, which pairs that region and a dollar year with those events.
#
# Run the RunImpactAnalysis workflow afterwards to analyze what this creates.
#
# The workflow takes a map code, so the same code builds a United States,
# Canadian, or international project. Only the resolved ids and the industry
# differ.
#
# Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
# Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
# Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups


# The industry the events use, by name rather than by code, because the code
# differs between Industry Sets.
INDUSTRY_NAME <- "Oilseed farming"

# Which region to put the group in, per map code. International schemes have no
# state level, so a country is used there.
DEFAULT_REGION <- list(
  US = list(name = "Oregon", type = "State"),
  CAN = list(name = "Ontario", type = "State"),
  INTL = list(name = "Canada", type = "Country")
)


create_project_workflow <- function(map_code = MAP_CODES[["US"]]) {
  client <- create_client()

  # Step 1. Resolve the ids. The Household Set comes from the scheme rather than
  # being assumed to be 1, because it differs by country.
  log_heading("Step 1: resolve the identifiers")
  ids <- resolve_identifiers(client, map_code)

  # Step 2. Create the project. The scheme and household set are fixed here and
  # cannot be changed afterwards.
  log_heading("Step 2: create the Project")

  # POST /api/v1/impact/project  (wiki: Create Project)
  project <- create_project(client, new_project(
    title = unique_title("Create Project"),
    aggregation_scheme_id = ids$aggregation_scheme_id,
    household_set_id = ids$household_set_id
  ))
  log_info("  %s", describe(project))

  # Step 3. Ask the project which event types it accepts. The answer depends on
  # the Aggregation Scheme, so asking beats assuming.
  log_heading("Step 3: which event types this Project accepts")

  # GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
  accepted <- get_event_types(client, project$id)
  log_info("  %s", paste(accepted, collapse = ", "))

  # Step 4. Find the industry. By name, then confirm the code, which is the habit
  # that stops a sample from quietly analyzing the wrong industry.
  log_heading("Step 4: find the industry")

  # GET /api/v1/IndustryCodes/{aggregationSchemeId}
  # (wiki: Industry Codes by Aggregation Scheme)
  codes <- get_industry_codes_for_scheme(client, ids$aggregation_scheme_id)
  industry <- find_industry_by_description(codes, INDUSTRY_NAME)
  log_info("  %s is code %s in this Industry Set", industry$description, industry$code)

  # Step 5. Add the events.
  log_heading("Step 5: add the Events")

  # The simple case: one number and the industry that earned it. IMPLAN estimates
  # employment, compensation, and the rest from the region's averages.
  #
  # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
  # Use the returned event: it comes back with the generated id and with
  # everything IMPLAN estimated.
  output_event <- create_event(client, project$id, industry_output_event(
    title = unique_title("Industry Output"),
    industry_code = industry$code,
    output = 1000000
  ))
  log_info("  %s", describe(output_event))

  # The detailed case, when you have the operating statement rather than one
  # total. Only available in domestic schemes, so it is skipped elsewhere.
  detailed_event <- NULL
  if (EVENT_TYPES[["INDUSTRY_IMPACT_ANALYSIS"]] %in% accepted) {
    detailed_event <- create_event(client, project$id, industry_impact_analysis_event(
      title = unique_title("Industry Impact Analysis"),
      industry_code = industry$code,
      intermediate_inputs = 500000,
      employee_compensation = 250000,
      proprietor_income = 50000,
      wage_and_salary_employment = 4,
      proprietor_employment = 1,
      total_employment = 5,
      total_labor_income = 300000,
      other_property_income = 100000,
      tax_on_production_and_imports = 100000,
      local_purchase_percentage = 1.0,
      # Which data year's spending pattern the intermediate inputs flow through.
      # The resolved dataset keeps this consistent with the project.
      spending_pattern_dataset_id = ids$dataset_id,
      spending_pattern_value_type =
        SPENDING_PATTERN_VALUE_TYPES[["INTERMEDIATE_EXPENDITURE"]]
    ))
    log_info("  %s", describe(detailed_event))
  } else {
    log_info(
      "  Industry Impact Analysis is not available in a %s scheme; skipping it",
      map_code
    )
  }

  # Step 6. Find the region the group will use.
  log_heading("Step 6: find the Region")
  target <- DEFAULT_REGION[[map_code]]

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
  # (wiki: Regional Children)
  # Passing no parent means "children of the top-level region". That works for
  # international schemes too, which have no top-level region of their own: ask
  # for Country there and the countries come back.
  candidates <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = target$type
  )
  region <- find_region_by_description(candidates, target$name)
  log_info("  %s", describe(region))

  # Step 7. Create the group. This is where the events, the region, and the
  # dollar year come together.
  log_heading("Step 7: add the Group")
  event_links <- list(group_event(output_event$id))
  if (!is.null(detailed_event)) {
    event_links <- c(event_links, list(group_event(detailed_event$id)))
  }

  # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
  group <- create_group(client, project$id, new_group(
    title = unique_title("Group"),
    # Exactly one region identifier. HashId is the one to use.
    hash_id = region$hash_id,
    dataset_id = ids$dataset_id,
    # Always set this. There is no server-side default, and a group without one
    # produces a run that never attaches.
    dollar_year = current_dollar_year(),
    group_events = event_links
  ))
  log_info("  %s", describe(group))

  # Step 8. Read the project back, to confirm what was built.
  log_heading("Step 8: read the Project back")

  # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
  project <- get_project(client, project$id)
  log_info("  %s", describe(project))
  log_info(
    "  Aggregation Scheme %s, Household Set %s",
    project$aggregation_scheme_id, project$household_set_id
  )

  created_ids <- c(output_event$id, if (is.null(detailed_event)) NULL else detailed_event$id)

  log_heading("Done")
  log_info("Project id:  %s", project$id)
  log_info("Event ids:   %s", paste(created_ids, collapse = ", "))
  log_info("Group id:    %s", group$id)
  log_info("")
  log_info("Run it with the RunImpactAnalysis workflow:")
  log_info("  Rscript main.R run-impact-analysis --project-id %s", project$id)
  log_info("")
  log_info("Delete it from Projects in IMPLAN Cloud when you are done.")

  invisible(project)
}
