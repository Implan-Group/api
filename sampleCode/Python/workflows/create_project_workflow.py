"""Workflow 5: CreateProject.

Goal: the shortest path from nothing to a project that can be run.

Four things have to exist, in this order, and each depends on the one before:

  1. A Project, which fixes the Aggregation Scheme and Household Set.
  2. Events, which say what changed.
  3. A Region to apply them to.
  4. A Group, which pairs that region and a dollar year with those events.

Run the RunImpactAnalysis workflow afterwards to analyze what this creates.

The workflow takes a map code, so the same code builds a United States, Canadian,
or international project. Only the resolved ids and the industry differ.

Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
"""

from endpoints import events, groups, identifiers, industries, projects, regions
from models.event import (
    EventType,
    IndustryImpactAnalysisEvent,
    IndustryOutputEvent,
    SpendingPatternValueType,
)
from models.group import Group, GroupEvent
from models.project import Project
from models.reference import MapCode
from models.region import RegionType
from utilities import auth, config, logging_setup

# The industry the events use, by name rather than by code, because the code
# differs between Industry Sets.
INDUSTRY_NAME = "Oilseed farming"

# Which region to put the group in, per map code. International schemes have no
# state level, so a country is used there.
DEFAULT_REGION = {
    MapCode.US: ("Oregon", RegionType.STATE),
    MapCode.CANADA: ("Ontario", RegionType.STATE),
    MapCode.INTERNATIONAL: ("Canada", RegionType.COUNTRY),
}


def run(map_code: MapCode = MapCode.US) -> Project:
    """Create a project with two events and one group, and return it."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve the ids. The Household Set comes from the scheme rather than
    # being assumed to be 1, because it differs by country.
    logging_setup.heading("Step 1: resolve the identifiers")
    ids = identifiers.resolve(client, map_code)

    # Step 2. Create the project. The scheme and household set are fixed here and
    # cannot be changed afterwards.
    logging_setup.heading("Step 2: create the Project")
    definition = Project(
        title=config.unique_title("Create Project"),
        aggregation_scheme_id=ids.aggregation_scheme_id,
        household_set_id=ids.household_set_id,
    )

    # POST /api/v1/impact/project  (wiki: Create Project)
    project = projects.create_project(client, definition)
    logger.info("  %s", project.describe())

    # Step 3. Ask the project which event types it accepts. The answer depends on
    # the Aggregation Scheme, so asking beats assuming.
    logging_setup.heading("Step 3: which event types this Project accepts")

    # GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
    accepted = events.get_event_types(client, project.id)
    logger.info("  %s", ", ".join(accepted))

    # Step 4. Find the industry. By name, then confirm the code, which is the
    # habit that stops a sample from quietly analyzing the wrong industry.
    logging_setup.heading("Step 4: find the industry")

    # GET /api/v1/IndustryCodes/{aggregationSchemeId}
    # (wiki: Industry Codes by Aggregation Scheme)
    codes = industries.get_industry_codes_for_scheme(client, ids.aggregation_scheme_id)
    industry = industries.find_industry_by_description(codes, INDUSTRY_NAME)
    logger.info("  %s is code %d in this Industry Set", industry.description, industry.code)

    # Step 5. Add the events.
    logging_setup.heading("Step 5: add the Events")

    # The simple case: one number and the industry that earned it. IMPLAN estimates
    # employment, compensation, and the rest from the region's averages.
    output_event = IndustryOutputEvent(
        title=config.unique_title("Industry Output"),
        industry_code=industry.code,
        output=1_000_000.00,
    )

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    # Re-assign from the response: it comes back with the generated id and with
    # everything IMPLAN estimated.
    output_event = events.create_event(client, project.id, output_event)
    logger.info("  %s", output_event.describe())

    # The detailed case, when you have the operating statement rather than one
    # total. Only available in domestic schemes, so it is skipped elsewhere.
    detailed_event = None
    if EventType.INDUSTRY_IMPACT_ANALYSIS.value in accepted:
        detailed_event = IndustryImpactAnalysisEvent(
            title=config.unique_title("Industry Impact Analysis"),
            industry_code=industry.code,
            intermediate_inputs=500_000.00,
            employee_compensation=250_000.00,
            proprietor_income=50_000.00,
            wage_and_salary_employment=4,
            proprietor_employment=1,
            total_employment=5,
            total_labor_income=300_000.00,
            other_property_income=100_000.00,
            tax_on_production_and_imports=100_000.00,
            local_purchase_percentage=1.0,
            # Which data year's spending pattern the intermediate inputs flow
            # through. The resolved dataset keeps this consistent with the project.
            spending_pattern_dataset_id=ids.dataset_id,
            spending_pattern_value_type=SpendingPatternValueType.INTERMEDIATE_EXPENDITURE.value,
        )
        detailed_event = events.create_event(client, project.id, detailed_event)
        logger.info("  %s", detailed_event.describe())
    else:
        logger.info(
            "  Industry Impact Analysis is not available in a %s scheme; skipping it",
            map_code.value,
        )

    # Step 6. Find the region the group will use.
    logging_setup.heading("Step 6: find the Region")
    region_name, region_type = DEFAULT_REGION[map_code]

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
    # (wiki: Regional Children)
    # Passing no parent means "children of the top-level region". That works for
    # international schemes too, which have no top-level region of their own: ask
    # for Country there and the countries come back.
    candidates = regions.get_region_children(
        client, ids.aggregation_scheme_id, ids.dataset_id, region_type=region_type
    )
    region = regions.find_region_by_description(candidates, region_name)
    logger.info("  %s", region.describe())

    # Step 7. Create the group. This is where the events, the region, and the
    # dollar year come together.
    logging_setup.heading("Step 7: add the Group")
    event_links = [GroupEvent(event_id=output_event.id)]
    if detailed_event is not None:
        event_links.append(GroupEvent(event_id=detailed_event.id))

    group = Group(
        title=config.unique_title("Group"),
        # Exactly one region identifier. HashId is the one to use.
        hash_id=region.hash_id,
        dataset_id=ids.dataset_id,
        # Always set this. There is no server-side default, and a group without one
        # produces a run that never attaches.
        dollar_year=config.current_dollar_year(),
        group_events=event_links,
    )

    # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    group = groups.create_group(client, project.id, group)
    logger.info("  %s", group.describe())

    # Step 8. Read the project back, to confirm what was built.
    logging_setup.heading("Step 8: read the Project back")

    # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
    project = projects.get_project(client, project.id)
    logger.info("  %s", project.describe())
    logger.info("  Aggregation Scheme %d, Household Set %d", project.aggregation_scheme_id, project.household_set_id)

    logging_setup.heading("Done")
    logger.info("Project id:  %s", project.id)
    logger.info("Event ids:   %s", ", ".join(str(e.id) for e in [output_event, detailed_event] if e))
    logger.info("Group id:    %s", group.id)
    logger.info("")
    logger.info("Run it with the RunImpactAnalysis workflow:")
    logger.info("  python main.py run-impact-analysis --project-id %s", project.id)
    logger.info("")
    logger.info("Delete it from Projects in IMPLAN Cloud when you are done.")
    return project
