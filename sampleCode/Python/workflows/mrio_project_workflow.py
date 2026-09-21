"""Workflow 11: MrioProject.

Goal: multi-regional input-output analysis, where activity in one region shows up
as effects in another.

An ordinary project treats each of its regions in isolation. Build a factory in
Oregon and the results show Oregon's supply chain; anything the factory buys from
Wisconsin leaks out of the model and is never counted. That is usually the wrong
answer when the regions are economically linked.

MRIO keeps the link. With `isMrio` set on the project, IMPLAN traces demand from
one region into the others in the same project, so Wisconsin shows indirect and
induced effects from an event that only happened in Oregon.

The shape is:

  - One project, with `is_mrio` set to true.
  - One event, in one region.
  - A group per region, including regions with no events of their own. Those exist
    so there is somewhere for the spillover to be reported.

Reading the results filtered by region is what makes the point: Wisconsin's numbers
are non-zero although nothing was built there.

Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
Support: MRIO: Introduction to Multi-Regional Input-Output Analysis
https://support.implan.com/hc/en-us/articles/115009713448
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
from models.event import IndustryOutputEvent
from models.group import Group, GroupEvent
from models.project import Project
from models.reference import MapCode
from models.region import RegionType
from models.results import ResultFilters
from utilities import auth, config, logging_setup

# The region the event happens in, and the region that should show spillover.
SOURCE_REGION = "Oregon"
LINKED_REGION = "Wisconsin"

# An industry with a wide supply chain, so the cross-region effect is visible.
INDUSTRY_NAME = "Full-service restaurants"
EVENT_OUTPUT = 10_000_000.00


def run() -> int:
    """Build and run an MRIO project, and report each region separately."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve identifiers.
    logging_setup.heading("Step 1: resolve the identifiers")
    ids = identifiers.resolve(client, MapCode.US)

    # Step 2. Find both regions, and check each allows MRIO. Not every region does,
    # and finding out here is better than after a run produces nothing.
    logging_setup.heading("Step 2: find the regions and check they allow MRIO")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
    # (wiki: Regional Children)
    states = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        region_type=RegionType.STATE,
    )

    source = regions.find_region_by_description(states, SOURCE_REGION)
    linked = regions.find_region_by_description(states, LINKED_REGION)

    for region in (source, linked):
        logger.info("  %s  MRIO allowed: %s", region.describe(), region.is_mrio_allowed)
        if not region.is_mrio_allowed:
            raise RuntimeError(
                f"{region.description} cannot take part in an MRIO analysis. Pick a "
                f"different region."
            )

    # Step 3. Create the project with MRIO switched on. This is the one flag that
    # separates this workflow from CreateProject, and it cannot be changed later.
    logging_setup.heading("Step 3: create the Project with MRIO enabled")

    # POST /api/v1/impact/project  (wiki: Create Project)
    project = projects.create_project(
        client,
        Project(
            title=config.unique_title("MRIO"),
            aggregation_scheme_id=ids.aggregation_scheme_id,
            household_set_id=ids.household_set_id,
            is_mrio=True,
        ),
    )
    logger.info("  %s", project.describe())
    logger.info("  isMrio: %s", project.is_mrio)

    # Step 4. One event, in the source region only.
    logging_setup.heading("Step 4: add one Event")

    # GET /api/v1/IndustryCodes/{aggregationSchemeId}
    # (wiki: Industry Codes by Aggregation Scheme)
    codes = industries.get_industry_codes_for_scheme(client, ids.aggregation_scheme_id)
    industry = industries.find_industry_by_description(codes, INDUSTRY_NAME)

    # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    event = events.create_event(
        client,
        project.id,
        IndustryOutputEvent(
            title=config.unique_title("Restaurants in " + SOURCE_REGION),
            industry_code=industry.code,
            output=EVENT_OUTPUT,
        ),
    )
    logger.info("  %s", event.describe())
    logger.info("  %s output in %s", f"${EVENT_OUTPUT:,.0f}", SOURCE_REGION)

    # Step 5. Two groups. The source group holds the event. The linked group holds
    # the same event too, scaled to almost nothing.
    #
    # On that scaling: a group with no events at all is the cleaner illustration,
    # but the API requires a group to carry at least one event, so the linked
    # region gets the event at a negligible scaling factor. Its own direct effect
    # is therefore near zero, and essentially everything reported for it is
    # spillover from the source region, which is the effect this workflow exists to
    # show.
    logging_setup.heading("Step 5: a Group for each region")
    dollar_year = config.current_dollar_year()

    # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    source_group = groups.create_group(
        client,
        project.id,
        Group(
            title=config.unique_title(SOURCE_REGION),
            hash_id=source.hash_id,
            dataset_id=ids.dataset_id,
            dollar_year=dollar_year,
            group_events=[GroupEvent(event_id=event.id)],
        ),
    )
    logger.info("  %s", source_group.describe())

    linked_group = groups.create_group(
        client,
        project.id,
        Group(
            title=config.unique_title(LINKED_REGION),
            hash_id=linked.hash_id,
            dataset_id=ids.dataset_id,
            dollar_year=dollar_year,
            group_events=[GroupEvent(event_id=event.id, scaling_factor=0.01)],
        ),
    )
    logger.info("  %s  (event scaled to 0.01)", linked_group.describe())

    # Step 6. Run it.
    logging_setup.heading("Step 6: run the impact")

    # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
    run_id = impacts.run_impact(client, project.id)
    logger.info("  run id %d", run_id)

    # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
    impacts.wait_for_impact(client, run_id)
    logger.info("  complete")

    # Step 7. Read the results once per region. The filter is what separates the
    # two, and comparing them is the point of the workflow.
    logging_setup.heading("Step 7: read the results region by region")
    destination = config.REPORTS_DIRECTORY / f"MRIO-{run_id}"

    for region in (source, linked):
        filters = ResultFilters(
            year=dollar_year,
            regions=[region.description],
        )

        # GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?regions=...
        # (wiki: Results - Summary Economic Indicators)
        csv_text = impact_results.get_summary_economic_indicators(
            client, run_id, filters
        )
        path = impact_results.save_csv(
            csv_text, destination / f"Summary Economic Indicators - {region.description}.csv"
        )

        # Count the data rows so the console says something useful without trying
        # to parse a report whose columns vary by account.
        rows = [line for line in csv_text.splitlines() if line.strip()]
        logger.info("  %s: %d rows in %s", region.description, max(len(rows) - 1, 0), path.name)

    logging_setup.heading("Done")
    logger.info("Project id: %s", project.id)
    logger.info("Run id:     %d", run_id)
    logger.info("Reports:    %s", destination)
    logger.info("")
    logger.info("Compare the two files. %s carries indirect and induced", LINKED_REGION)
    logger.info("effects from activity that only happened in %s. In a project", SOURCE_REGION)
    logger.info("without MRIO those effects leak out of the model and are lost.")
    return run_id
