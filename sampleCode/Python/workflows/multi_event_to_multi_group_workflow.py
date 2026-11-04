"""Workflow 6: MultiEventToMultiGroup.

Goal: apply the same set of events to several regions at once.

This is the shape most real analyses take. A mixed-use development has restaurants
on the ground floor and two bands of apartments above it, and the question is which
of three states to build it in. That is three events and three groups, with every
event in every group, and the answer falls out of the results filtered by region.

The pattern is a nested loop: create each event once, then create one group per
region holding all of them. Events are owned by the project, not by a group, so
they are created once and referenced many times.

Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
Support: MRIO vs. Larger Study Area, on when separate groups are the right model
https://support.implan.com/hc/en-us/articles/115002799373
"""

from endpoints import events, groups, identifiers, industries, projects, regions
from models.event import HouseholdIncomeEvent, IndustryOutputEvent
from models.group import Group, GroupEvent
from models.project import Project
from models.reference import MapCode
from models.region import RegionType
from utilities import auth, config, logging_setup

# The states to compare. Change this list to compare different ones.
TARGET_STATES = ["Oregon", "Wisconsin", "North Carolina"]

# The restaurants on the ground floor, by name rather than by code.
RESTAURANT_INDUSTRY = "Full-service restaurants"

# The two household income brackets, by specification code. These are checked
# against the project's own specification list in step 3 rather than trusted.
HOUSEHOLD_BRACKETS = [
    (10002, "Households 15-30k", 25_000.00),
    (10005, "Households 50-70k", 125_000.00),
]


def run(project_id: str | None = None) -> Project:
    """Add three events and one group per state, and return the project."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Get a project to work in, and the identifiers that go with it. An
    # existing empty project can be passed in; otherwise one is created here.
    #
    # An existing project keeps the Aggregation Scheme and Household Set it was
    # created with, so its identifiers are resolved from the project rather than
    # from today's defaults. The industry codes, Dataset, and states below then
    # all belong to the project's own scheme.
    logging_setup.heading("Step 1: the Project and its identifiers")
    if project_id is None:
        ids = identifiers.resolve(client, MapCode.US)

        # POST /api/v1/impact/project  (wiki: Create Project)
        project = projects.create_project(
            client,
            Project(
                title=config.unique_title("Multi Event Multi Group"),
                aggregation_scheme_id=ids.aggregation_scheme_id,
                household_set_id=ids.household_set_id,
            ),
        )
        logger.info("  created %s", project.describe())
    else:
        # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
        project = projects.get_project(client, project_id)
        logger.info("  using existing %s", project.describe())
        ids = identifiers.resolve_for_project(client, project)

        # The three states only exist in a United States scheme.
        if ids.map_code is not MapCode.US:
            raise ValueError(
                f"Project {project.id} uses a {ids.map_code.value} Aggregation Scheme. "
                f"This workflow adds groups for three US states, so it needs a "
                f"Project on a US scheme."
            )

    # Step 2. The restaurant event needs an industry code.
    logging_setup.heading("Step 2: find the restaurant industry")

    # GET /api/v1/IndustryCodes/{aggregationSchemeId}
    # (wiki: Industry Codes by Aggregation Scheme)
    codes = industries.get_industry_codes_for_scheme(client, ids.aggregation_scheme_id)
    restaurants = industries.find_industry_by_description(codes, RESTAURANT_INDUSTRY)
    logger.info("  %s is code %d here", restaurants.description, restaurants.code)
    logger.info("  (it is a different code in other Industry Sets, which is why this")
    logger.info("   sample looks it up by name)")

    # Step 3. Household Income events take a specification code rather than an
    # industry code, so read the valid ones for this project first.
    logging_setup.heading("Step 3: read the Household Income specification codes")

    # GET /api/v1/impact/project/{projectId}/eventtype/HouseholdIncome/specification
    # (wiki: Get Event Specifications)
    specifications = events.get_event_specifications(
        client, project.id, "HouseholdIncome"
    )
    available = {spec.code: spec.name for spec in specifications}
    logger.info("  %d income brackets available:", len(specifications))
    for spec in specifications:
        logger.info("    %s", spec.name)

    for code, label, _ in HOUSEHOLD_BRACKETS:
        if str(code) not in available:
            raise LookupError(
                f"Household income code {code} ({label}) is not valid for this "
                f"Project. Available codes: {', '.join(sorted(available))}."
            )

    # Step 4. Create the events. Each one is created once and will be referenced
    # by all three groups.
    logging_setup.heading("Step 4: add the Events")
    created = []

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    restaurant_event = events.create_event(
        client,
        project.id,
        IndustryOutputEvent(
            title=config.unique_title("Restaurants"),
            industry_code=restaurants.code,
            output=1_000_000.00,
        ),
    )
    created.append(restaurant_event)
    logger.info("  %s", restaurant_event.describe())

    for code, label, value in HOUSEHOLD_BRACKETS:
        household_event = events.create_event(
            client,
            project.id,
            HouseholdIncomeEvent(
                title=config.unique_title(label),
                household_income_code=code,
                value=value,
            ),
        )
        created.append(household_event)
        logger.info("  %s", household_event.describe())

    # Step 5. Find the states.
    logging_setup.heading("Step 5: find the Regions")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
    # (wiki: Regional Children)
    states = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        region_type=RegionType.STATE,
    )
    chosen = [regions.find_region_by_description(states, name) for name in TARGET_STATES]
    for state in chosen:
        logger.info("  %s", state.describe())

    # Step 6. One group per region, each holding every event. This is the nested
    # loop the workflow exists to show: events on the inside, regions on the
    # outside, and the group titles distinct.
    logging_setup.heading("Step 6: one Group per Region, each holding every Event")
    dollar_year = config.current_dollar_year()
    event_links = [GroupEvent(event_id=event.id) for event in created]

    for state in chosen:
        group = Group(
            # Group titles have to be distinct within a project.
            title=config.unique_title(state.description),
            hash_id=state.hash_id,
            dataset_id=ids.dataset_id,
            dollar_year=dollar_year,
            group_events=event_links,
        )

        # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
        group = groups.create_group(client, project.id, group)
        logger.info("  %s", group.describe())

    # Step 7. Read it back.
    logging_setup.heading("Step 7: read the Groups back")

    # GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
    all_groups = groups.get_groups(client, project.id)
    logger.info("  %d groups in the Project", len(all_groups))
    for group in all_groups:
        logger.info("    %s", group.describe())

    logging_setup.heading("Done")
    logger.info("Project id: %s", project.id)
    logger.info("Added %d events, in each of %d new groups", len(created), len(chosen))
    logger.info("")
    logger.info("Run it, then filter the results by region to compare the states:")
    logger.info("  python main.py run-impact-analysis --project-id %s", project.id)
    return project
