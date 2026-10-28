# Workflow 12: AdvancedEvents.
#
# Goal: the two event types analysts reach for after Industry Output, plus tags
# and tag-filtered results.
#
# Industry Output answers "what if this new activity arrived?". Two other types
# answer different questions:
#
#   - Industry Contribution Analysis asks how much of the economy already rests
#     on an industry that is there now. It constrains the industry from buying
#     from itself, so its own output is not counted twice. Use it for "the hotel
#     industry contributes X to this county", never for a new hotel.
#
#   - Industry Spending Pattern models a buyer rather than a producer. It spends
#     money through an industry's supply chain without adding any direct output,
#     which is what you want for an organization whose own output is not the
#     thing being measured. Its commodity list can be read, edited, and sent
#     back, which this workflow demonstrates.
#
# Tags tie it together. Both events are tagged, and the results are read once per
# tag, so a single run answers two questions separately.
#
# Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
# Support: ICA: Introduction to Industry Contribution Analysis
# https://support.implan.com/hc/en-us/articles/360025854654
# Support: Industry Spending Pattern Events
# https://support.implan.com/hc/en-us/articles/360052212933
# Support: Event Tags
# https://support.implan.com/hc/en-us/articles/4407853242139


ADVANCED_REGION_NAME <- "Oregon"
CONTRIBUTION_INDUSTRY <- "Full-service restaurants"
SPENDING_INDUSTRY <- "Oilseed farming"

# The tags each event carries. Results are filtered by these at the end.
CONTRIBUTION_TAG <- "contribution"
SPENDING_TAG <- "spending"

ADVANCED_EVENT_VALUE <- 1000000


advanced_events_workflow <- function() {
  client <- create_client()

  # Step 1. Resolve identifiers.
  log_heading("Step 1: resolve the identifiers")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. Create the project and confirm both event types are available in it.
  log_heading("Step 2: create the Project")

  # POST /api/v1/impact/project  (wiki: Create Project)
  project <- create_project(client, new_project(
    title = unique_title("Advanced Events"),
    aggregation_scheme_id = ids$aggregation_scheme_id,
    household_set_id = ids$household_set_id
  ))
  log_info("  %s", describe(project))

  # GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
  accepted <- get_event_types(client, project$id)
  required_types <- c(
    EVENT_TYPES[["INDUSTRY_CONTRIBUTION_ANALYSIS"]],
    EVENT_TYPES[["INDUSTRY_SPENDING_PATTERN"]]
  )
  for (required in required_types) {
    if (!required %in% accepted) {
      stop(
        sprintf(
          "%s is not available in this Project's Aggregation Scheme. Available types: %s",
          required, paste(accepted, collapse = ", ")
        ),
        call. = FALSE
      )
    }
  }
  log_info("  both event types are available here")

  # GET /api/v1/IndustryCodes/{aggregationSchemeId}
  # (wiki: Industry Codes by Aggregation Scheme)
  codes <- get_industry_codes_for_scheme(client, ids$aggregation_scheme_id)

  # Step 3. The contribution event. The value is a dollar figure, and it must not
  # exceed the industry's total output in the region; setting
  # `is_output_percentage` instead lets you give a share from 0 to 1, which
  # avoids having to know that total.
  log_heading("Step 3: an Industry Contribution Analysis event")
  contribution_industry <- find_industry_by_description(codes, CONTRIBUTION_INDUSTRY)
  log_info(
    "  %s is code %s here",
    contribution_industry$description, contribution_industry$code
  )

  # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
  contribution_event <- create_event(
    client, project$id,
    industry_contribution_analysis_event(
      title = unique_title("Restaurant contribution"),
      industry_code = contribution_industry$code,
      output = ADVANCED_EVENT_VALUE,
      is_output_percentage = FALSE,
      tags = CONTRIBUTION_TAG
    )
  )
  log_info("  %s", describe(contribution_event))
  log_info("  tagged '%s'", CONTRIBUTION_TAG)

  # Step 4. Read a default spending pattern, so it can be edited rather than
  # invented. The pattern is a list of commodities and the share of each dollar
  # that goes to them, summing to 1.
  log_heading("Step 4: read a default spending pattern")
  spending_industry <- find_industry_by_description(codes, SPENDING_INDUSTRY)

  # GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/Industry/{industryCode}
  # (wiki: Spending Pattern by Id)
  commodities <- get_spending_pattern(
    client,
    ids$aggregation_scheme_id,
    spending_industry$code,
    pattern_type = SPENDING_PATTERN_TYPES[["INDUSTRY"]],
    dataset_id = ids$dataset_id
  )
  log_info("  %s buys %d commodities", spending_industry$description, length(commodities))

  if (length(commodities) == 0L) {
    stop(
      sprintf(
        "No default spending pattern for industry %s in Dataset %s.",
        spending_industry$code, ids$dataset_id
      ),
      call. = FALSE
    )
  }

  coefficients <- vapply(
    commodities,
    function(commodity) as.numeric(field_or(commodity, "coefficient", 0)),
    numeric(1)
  )
  ranked <- order(coefficients, decreasing = TRUE)

  log_info("  the five largest:")
  for (index in utils::head(ranked, 5)) {
    log_info("    %s", describe(commodities[[index]]))
  }

  # Step 5. Edit one coefficient. Marking it `is_user_coefficient` tells IMPLAN
  # the number is yours and not its own, which is what makes the change visible
  # in the project and in the results.
  log_heading("Step 5: change one coefficient")
  target <- ranked[1]
  original <- coefficients[target]
  commodities[[target]]$coefficient <- round(original * 1.10, 6)
  commodities[[target]]$is_user_coefficient <- TRUE
  log_info(
    "  %s: %.6f -> %.6f",
    commodities[[target]]$commodity_description, original, commodities[[target]]$coefficient
  )
  log_info("  (the rest of the pattern is sent back unchanged)")

  # Step 6. The spending-pattern event, carrying the edited list.
  log_heading("Step 6: an Industry Spending Pattern event")

  # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
  spending_event <- create_event(
    client, project$id,
    industry_spending_pattern_event(
      title = unique_title("Supplier spending"),
      industry_code = spending_industry$code,
      output = ADVANCED_EVENT_VALUE,
      # Spend the whole value across the pattern rather than taking a share of it
      # as gross absorption first.
      spending_pattern_value_type =
        SPENDING_PATTERN_VALUE_TYPES[["INTERMEDIATE_EXPENDITURE"]],
      spending_pattern_dataset_id = ids$dataset_id,
      spending_pattern_commodities = commodities,
      tags = SPENDING_TAG
    )
  )
  log_info("  %s", describe(spending_event))
  log_info("  tagged '%s'", SPENDING_TAG)

  # Step 7. One group holding both events.
  log_heading("Step 7: one Group holding both events")

  # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
  # (wiki: Regional Children)
  states <- get_region_children(
    client, ids$aggregation_scheme_id, ids$dataset_id,
    region_type = "State"
  )
  region <- find_region_by_description(states, ADVANCED_REGION_NAME)

  # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
  group <- create_group(client, project$id, new_group(
    title = unique_title(ADVANCED_REGION_NAME),
    hash_id = region$hash_id,
    dataset_id = ids$dataset_id,
    dollar_year = current_dollar_year(),
    group_events = list(
      group_event(contribution_event$id),
      group_event(spending_event$id)
    )
  ))
  log_info("  %s", describe(group))

  # Step 8. Run it.
  log_heading("Step 8: run the impact")

  # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
  run_id <- run_impact(client, project$id)
  log_info("  run id %d", run_id)

  # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
  wait_for_impact(client, run_id)
  log_info("  complete")

  # Step 9. Read the results once per tag. This is what tags are for: two
  # questions answered from one run, each read separately.
  log_heading("Step 9: read the results, filtered by tag")
  destination <- file.path(reports_directory(), sprintf("Advanced Events-%d", run_id))
  dollar_year <- current_dollar_year()

  for (tag in c(CONTRIBUTION_TAG, SPENDING_TAG)) {
    filters <- result_filters(year = dollar_year, event_tags = tag)

    # GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?eventTags=...
    # (wiki: Results - Summary Economic Indicators)
    csv_text <- get_summary_economic_indicators(client, run_id, filters)
    save_csv(
      csv_text,
      file.path(destination, sprintf("Summary Economic Indicators - %s.csv", tag))
    )

    log_info("  tag '%s': %d data rows", tag, csv_data_row_count(csv_text))
  }

  # The same filter, in the shape the growth report wants: a JSON body on a GET,
  # with every list present.
  growth_request <- impact_results_export_request(
    dollar_year = dollar_year,
    event_tags = SPENDING_TAG
  )

  # GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
  # (wiki: Results - Estimated Growth Percentage)
  growth_csv <- get_estimated_growth_percentage(client, run_id, growth_request)
  save_csv(
    growth_csv,
    file.path(destination, sprintf("Estimated Growth Percentage - %s.csv", SPENDING_TAG))
  )

  log_heading("Done")
  log_info("Project id: %s", project$id)
  log_info("Run id:     %d", run_id)
  log_info("Reports:    %s", destination)
  log_info("")
  log_info("Each tagged report holds only its own event, from one run. Tag")
  log_info("events by what they represent, for example capital against")
  log_info("operations, and one project answers several questions.")

  invisible(run_id)
}
