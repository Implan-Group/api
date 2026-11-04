"""Workflow 12: AdvancedEvents.

Goal: the two event types analysts reach for after Industry Output, plus tags and
tag-filtered results.

Industry Output answers "what if this new activity arrived?". Two other types
answer different questions:

  - Industry Contribution Analysis asks how much of the economy already rests on an
    industry that is there now. It constrains the industry from buying from itself,
    so its own output is not counted twice. Use it for "the hotel industry
    contributes X to this county", never for a new hotel.

  - Industry Spending Pattern models a buyer rather than a producer. It spends
    money through an industry's supply chain without adding any direct output, which
    is what you want for an organization whose own output is not the thing being
    measured. Its commodity list can be read, edited, and sent back, which this
    workflow demonstrates.

Tags tie it together. Both events are tagged, and the results are read once per
tag, so a single run answers two questions separately.

Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
Support: ICA: Introduction to Industry Contribution Analysis
https://support.implan.com/hc/en-us/articles/360025854654
Support: Industry Spending Pattern Events
https://support.implan.com/hc/en-us/articles/360052212933
Support: Event Tags
https://support.implan.com/hc/en-us/articles/4407853242139
"""

from endpoints import (
    events,
    groups,
    identifiers,
    impact_results,
    impacts,
    industries,
    projects,
    regions,
)
from models.event import (
    EventType,
    IndustryContributionAnalysisEvent,
    IndustrySpendingPatternEvent,
    SpendingPatternValueType,
)
from models.group import Group, GroupEvent
from models.project import Project
from models.reference import MapCode
from models.region import RegionType
from models.results import ImpactResultsExportRequest, ResultFilters
from models.spending_pattern import SpendingPatternType
from utilities import auth, config, logging_setup

REGION_NAME = "Oregon"
CONTRIBUTION_INDUSTRY = "Full-service restaurants"
SPENDING_INDUSTRY = "Oilseed farming"

# The tags each event carries. Results are filtered by these at the end.
CONTRIBUTION_TAG = "contribution"
SPENDING_TAG = "spending"

EVENT_VALUE = 1_000_000.00


def run() -> int:
    """Create both event types, tag them, run, and read results per tag."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve identifiers.
    logging_setup.heading("Step 1: resolve the identifiers")
    ids = identifiers.resolve(client, MapCode.US)

    # Step 2. Create the project and confirm both event types are available in it.
    logging_setup.heading("Step 2: create the Project")

    # POST /api/v1/impact/project  (wiki: Create Project)
    project = projects.create_project(
        client,
        Project(
            title=config.unique_title("Advanced Events"),
            aggregation_scheme_id=ids.aggregation_scheme_id,
            household_set_id=ids.household_set_id,
        ),
    )
    logger.info("  %s", project.describe())

    # GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
    accepted = events.get_event_types(client, project.id)
    for required in (
        EventType.INDUSTRY_CONTRIBUTION_ANALYSIS.value,
        EventType.INDUSTRY_SPENDING_PATTERN.value,
    ):
        if required not in accepted:
            raise RuntimeError(
                f"{required} is not available in this Project's Aggregation Scheme. "
                f"Available types: {', '.join(accepted)}"
            )
    logger.info("  both event types are available here")

    # GET /api/v1/IndustryCodes/{aggregationSchemeId}
    # (wiki: Industry Codes by Aggregation Scheme)
    codes = industries.get_industry_codes_for_scheme(client, ids.aggregation_scheme_id)

    # Step 3. The contribution event. The value is a dollar figure, and it must not
    # exceed the industry's total output in the region; setting
    # `is_output_percentage` instead lets you give a share from 0 to 1, which avoids
    # having to know that total.
    logging_setup.heading("Step 3: an Industry Contribution Analysis event")
    contribution_industry = industries.find_industry_by_description(
        codes, CONTRIBUTION_INDUSTRY
    )
    logger.info(
        "  %s is code %d here",
        contribution_industry.description,
        contribution_industry.code,
    )

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    contribution_event = events.create_event(
        client,
        project.id,
        IndustryContributionAnalysisEvent(
            title=config.unique_title("Restaurant contribution"),
            industry_code=contribution_industry.code,
            output=EVENT_VALUE,
            is_output_percentage=False,
            tags=[CONTRIBUTION_TAG],
        ),
    )
    logger.info("  %s", contribution_event.describe())
    logger.info("  tagged '%s'", CONTRIBUTION_TAG)

    # Step 4. Read a default spending pattern, so it can be edited rather than
    # invented. The pattern is a list of commodities and the share of each dollar
    # that goes to them, summing to 1.
    logging_setup.heading("Step 4: read a default spending pattern")
    spending_industry = industries.find_industry_by_description(codes, SPENDING_INDUSTRY)

    # GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/Industry/{industryCode}
    # (wiki: Spending Pattern by Id)
    pattern = events.get_spending_pattern(
        client,
        ids.aggregation_scheme_id,
        spending_industry.code,
        pattern_type=SpendingPatternType.INDUSTRY,
        dataset_id=ids.dataset_id,
    )
    logger.info(
        "  %s buys %d commodities",
        spending_industry.description,
        len(pattern.commodities),
    )

    if not pattern.commodities:
        raise RuntimeError(
            f"No default spending pattern for industry {spending_industry.code} in "
            f"Dataset {ids.dataset_id}."
        )

    ranked = sorted(
        pattern.commodities, key=lambda c: c.coefficient or 0, reverse=True
    )
    logger.info("  the five largest:")
    for commodity in ranked[:5]:
        logger.info("    %s", commodity.describe())

    # Step 5. Edit one coefficient. Marking it `is_user_coefficient` tells IMPLAN
    # the number is yours and not its own, which is what makes the change visible
    # in the project and in the results.
    logging_setup.heading("Step 5: change one coefficient")
    edited = list(pattern.commodities)
    target = ranked[0]
    original = target.coefficient or 0.0

    for commodity in edited:
        if commodity.commodity_code == target.commodity_code:
            commodity.coefficient = round(original * 1.10, 6)
            commodity.is_user_coefficient = True
            logger.info(
                "  %s: %.6f -> %.6f",
                commodity.commodity_description,
                original,
                commodity.coefficient,
            )
            break

    logger.info("  (the rest of the pattern is sent back unchanged)")

    # Step 6. The spending-pattern event, carrying the edited list.
    logging_setup.heading("Step 6: an Industry Spending Pattern event")

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    spending_event = events.create_event(
        client,
        project.id,
        IndustrySpendingPatternEvent(
            title=config.unique_title("Supplier spending"),
            industry_code=spending_industry.code,
            output=EVENT_VALUE,
            # Spend the whole value across the pattern rather than taking a share
            # of it as gross absorption first.
            spending_pattern_value_type=SpendingPatternValueType.INTERMEDIATE_EXPENDITURE.value,
            spending_pattern_dataset_id=ids.dataset_id,
            spending_pattern_commodities=edited,
            tags=[SPENDING_TAG],
        ),
    )
    logger.info("  %s", spending_event.describe())
    logger.info("  tagged '%s'", SPENDING_TAG)

    # Step 7. One group holding both events.
    logging_setup.heading("Step 7: one Group holding both events")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
    # (wiki: Regional Children)
    states = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        region_type=RegionType.STATE,
    )
    region = regions.find_region_by_description(states, REGION_NAME)

    # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    group = groups.create_group(
        client,
        project.id,
        Group(
            title=config.unique_title(REGION_NAME),
            hash_id=region.hash_id,
            dataset_id=ids.dataset_id,
            dollar_year=config.current_dollar_year(),
            group_events=[
                GroupEvent(event_id=contribution_event.id),
                GroupEvent(event_id=spending_event.id),
            ],
        ),
    )
    logger.info("  %s", group.describe())

    # Step 8. Run it.
    logging_setup.heading("Step 8: run the impact")

    # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
    run_id = impacts.run_impact(client, project.id)
    logger.info("  run id %d", run_id)

    # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
    impacts.wait_for_impact(client, run_id)
    logger.info("  complete")

    # Step 9. Read the results once per tag. This is what tags are for: two
    # questions answered from one run, each read separately.
    logging_setup.heading("Step 9: read the results, filtered by tag")
    destination = config.REPORTS_DIRECTORY / f"Advanced Events-{run_id}"
    dollar_year = config.current_dollar_year()

    for tag in (CONTRIBUTION_TAG, SPENDING_TAG):
        filters = ResultFilters(year=dollar_year, event_tags=[tag])

        # GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?eventTags=...
        # (wiki: Results - Summary Economic Indicators)
        csv_text = impact_results.get_summary_economic_indicators(
            client, run_id, filters
        )
        impact_results.save_csv(
            csv_text, destination / f"Summary Economic Indicators - {tag}.csv"
        )

        rows = [line for line in csv_text.splitlines() if line.strip()]
        logger.info("  tag '%s': %d data rows", tag, max(len(rows) - 1, 0))

    # The same filter, in the shape the growth report wants: a JSON body on a GET,
    # with every list present.
    growth_request = ImpactResultsExportRequest(
        dollar_year=dollar_year, event_tags=[SPENDING_TAG]
    )

    # GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
    # (wiki: Results - Estimated Growth Percentage)
    growth_csv = impact_results.get_estimated_growth_percentage(
        client, run_id, growth_request
    )
    impact_results.save_csv(
        growth_csv, destination / f"Estimated Growth Percentage - {SPENDING_TAG}.csv"
    )

    logging_setup.heading("Done")
    logger.info("Project id: %s", project.id)
    logger.info("Run id:     %d", run_id)
    logger.info("Reports:    %s", destination)
    logger.info("")
    logger.info("Each tagged report holds only its own event, from one run. Tag")
    logger.info("events by what they represent, for example capital against")
    logger.info("operations, and one project answers several questions.")
    return run_id
