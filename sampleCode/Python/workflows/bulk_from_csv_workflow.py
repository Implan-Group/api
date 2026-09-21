"""Workflow 8: BulkFromCsv.

Goal: drive many regions, projects, and runs from input files.

This is what batch work looks like in practice. An analyst keeps the study areas
and the events in spreadsheets, and the script turns them into combined regions,
one project per region, and a final project holding all of them.

Three habits make the difference between a script that finishes and one that trips
the rate limit or falls over halfway:

  - Look up regions once and cache the lookup. The FIPS-to-region map is built from
    two calls per state, not one call per county.
  - Reuse what already exists. Re-running finds the regions, the folder, and the
    projects it made last time instead of failing on duplicate names.
  - Throttle. The client's rate limiter is switched on for this workflow, because
    a loop over hundreds of regions will otherwise earn a 429 and then a ban.

Input files, all in `data/`:

  state_based.csv   fips, region_description, model_name
  county_based.csv  fips, region_description, model_name
  demo_events.csv   Name, Code, Type, Value

Rows sharing a `model_name` are combined into one region.

Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
"""

import csv
from pathlib import Path

from endpoints import (
    events,
    groups,
    identifiers,
    impact_results,
    impacts,
    projects,
    regions,
)
from models.event import CommodityOutputEvent, IndustryOutputEvent
from models.group import Group, GroupEvent
from models.project import Project
from models.reference import Identifiers, MapCode
from models.region import CombineRegionRequest, Region, RegionType
from models.results import ResultFilters
from utilities import auth, config, logging_setup
from utilities.rest import ApiClient, RateLimiter

# The folder in IMPLAN Cloud these projects are filed under.
FOLDER_NAME = f"{config.TITLE_PREFIX} - Bulk From CSV"

# Region model requests are the most tightly limited family, so this workflow
# stays under the published five per minute. See the wiki home page for the table.
REGION_REQUESTS_PER_MINUTE = 5

# The four reports downloaded for each run.
REPORTS = [
    ("Summary Economic Indicators", impact_results.get_summary_economic_indicators),
    ("Detailed Economic Indicators", impact_results.get_detailed_economic_indicators),
    ("Summary Taxes", impact_results.get_summary_taxes),
    ("Detailed Taxes", impact_results.get_detailed_taxes),
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read one input file, keeping FIPS codes as text.

    FIPS codes have leading zeros that matter: Alabama is `01000`, and reading that
    as a number turns it into 1000, which is not a place.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input file {path}. The samples ship with these in data/."
        )
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


class RegionLookup:
    """Finds regions by FIPS code, with as few API calls as possible.

    All the states are fetched once. Counties are fetched per state, and only for
    the states actually referenced, then kept. A file naming forty counties across
    three states costs four calls, not forty.
    """

    def __init__(self, client: ApiClient, ids: Identifiers) -> None:
        self._client = client
        self._ids = ids
        self._states: dict[str, Region] = {}
        self._counties_by_state: dict[str, dict[str, Region]] = {}

    def _load_states(self) -> None:
        if self._states:
            return

        # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
        # (wiki: Regional Children)
        found = regions.get_region_children(
            self._client,
            self._ids.aggregation_scheme_id,
            self._ids.dataset_id,
            region_type=RegionType.STATE,
        )
        self._states = {
            region.fips_code: region for region in found if region.fips_code
        }
        logging_setup.get_logger().info("  cached %d states", len(self._states))

    def _load_counties(self, state_fips: str) -> dict[str, Region]:
        if state_fips in self._counties_by_state:
            return self._counties_by_state[state_fips]

        self._load_states()
        state = self._states.get(state_fips)
        if state is None:
            raise LookupError(f"No state with FIPS code {state_fips}.")

        # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children
        # (wiki: Regional Children)
        found = regions.get_region_children(
            self._client,
            self._ids.aggregation_scheme_id,
            self._ids.dataset_id,
            parent_hash_id_or_urid=state.hash_id,
            region_type=RegionType.COUNTY,
        )
        counties = {region.fips_code: region for region in found if region.fips_code}
        self._counties_by_state[state_fips] = counties
        logging_setup.get_logger().info(
            "  cached %d counties in %s", len(counties), state.description
        )
        return counties

    def find(self, fips: str) -> Region:
        """Return the region for a FIPS code, state or county.

        A state code is two digits, or five ending in three zeros.
        """
        fips = fips.strip()
        is_state = len(fips) == 2 or (len(fips) == 5 and fips.endswith("000"))
        state_fips = fips[:2]

        if is_state:
            self._load_states()
            state = self._states.get(state_fips)
            if state is None:
                raise LookupError(f"No state with FIPS code {fips}.")
            return state

        counties = self._load_counties(state_fips)
        county = counties.get(fips)
        if county is None:
            raise LookupError(
                f"No county with FIPS code {fips} in state {state_fips}. Check the "
                f"code against the current data year."
            )
        return county


def _build_models(
    client: ApiClient, ids: Identifiers, rows: list[dict[str, str]], lookup: RegionLookup
) -> list[Region]:
    """Turn the rows of one input file into built regions, one per model name."""
    logger = logging_setup.get_logger()
    built: list[Region] = []

    by_model: dict[str, list[str]] = {}
    for row in rows:
        by_model.setdefault(row["model_name"], []).append(row["fips"])

    for model_name, fips_codes in by_model.items():
        # Naming the region for the scheme and dataset means the same input file
        # can be run against several data years without a name collision.
        description = (
            f"{config.TITLE_PREFIX} {model_name} "
            f"{ids.aggregation_scheme_id}-{ids.dataset_id}"
        )

        existing = regions.find_existing_user_region(
            client, ids.aggregation_scheme_id, ids.dataset_id, description
        )
        if existing is not None and existing.is_built:
            logger.info("  %s already built, reusing it", model_name)
            built.append(existing)
            continue

        members = [lookup.find(fips) for fips in fips_codes]

        if len(members) == 1:
            # One region needs no combining; use IMPLAN's own region directly.
            logger.info(
                "  %s is a single region (%s), using it as is",
                model_name,
                members[0].description,
            )
            built.append(members[0])
            continue

        logger.info("  %s: combining %d regions", model_name, len(members))

        # POST /api/v1/region/build/combined/{aggregationSchemeId}
        # (wiki: Combine Regions)
        combined = regions.build_combined_region(
            client,
            ids.aggregation_scheme_id,
            CombineRegionRequest(
                description=description,
                hash_ids=[region.hash_id for region in members],
            ),
        )

        # GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
        built.append(regions.wait_for_region_build(client, combined.hash_id))
        logger.info("    built as %s", combined.hash_id)

    return built


def _add_events_from_csv(
    client: ApiClient, project: Project, rows: list[dict[str, str]]
) -> list:
    """Create one event per row of the events file.

    Two event types are covered: an Industry Output event, where the code names an
    industry, and a Commodity Output event, where it names a commodity. Add another
    branch here to support more.
    """
    logger = logging_setup.get_logger()
    created = []

    for row in rows:
        title = config.unique_title(row["Name"])
        code = int(row["Code"])
        value = float(row["Value"])
        kind = row["Type"].strip().casefold()

        if kind == "industry output":
            event = IndustryOutputEvent(title=title, industry_code=code, output=value)
        elif kind == "commodity output":
            event = CommodityOutputEvent(title=title, commodity_code=code, output=value)
        else:
            raise ValueError(
                f"Event type '{row['Type']}' in demo_events.csv is not one this "
                f"workflow builds. Add a branch for it in _add_events_from_csv."
            )

        # POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        created.append(events.create_event(client, project.id, event))

    logger.info("    added %d events", len(created))
    return created


def _run_and_download(
    client: ApiClient, project: Project, label: str
) -> int | None:
    """Run one project, wait for it, and save its reports. Returns the run id."""
    logger = logging_setup.get_logger()

    # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
    run_id = impacts.run_impact(client, project.id)
    logger.info("    run %d started", run_id)

    try:
        # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
        impacts.wait_for_impact(client, run_id)
    except (RuntimeError, TimeoutError) as error:
        # One failed run should not stop a batch of fifty. Report it and carry on.
        logger.info("    run %d did not complete: %s", run_id, error)
        return None

    destination = config.REPORTS_DIRECTORY / FOLDER_NAME / f"{label}-{run_id}"
    filters = ResultFilters(year=config.current_dollar_year())
    for report_label, fetch in REPORTS:
        csv_text = fetch(client, run_id, filters)
        impact_results.save_csv(csv_text, destination / f"{report_label}.csv")

    return run_id


def run() -> None:
    """Build regions from CSV, run a project for each, then one holding them all."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Bulk work needs the throttle. Without it, a few hundred region calls earn a
    # 429 and then a temporary ban.
    client.rate_limiter = RateLimiter(REGION_REQUESTS_PER_MINUTE)

    # Step 1. Resolve identifiers and read the input files.
    logging_setup.heading("Step 1: resolve identifiers and read the input files")
    ids = identifiers.resolve(client, MapCode.US)

    state_rows = _read_csv(config.DATA_DIRECTORY / "state_based.csv")
    county_rows = _read_csv(config.DATA_DIRECTORY / "county_based.csv")
    event_rows = _read_csv(config.DATA_DIRECTORY / "demo_events.csv")
    logger.info(
        "  %d state rows, %d county rows, %d event rows",
        len(state_rows),
        len(county_rows),
        len(event_rows),
    )

    # Step 2. Build the combined regions. The lookup is shared so the state list is
    # fetched once for both files.
    logging_setup.heading("Step 2: build the combined regions")
    lookup = RegionLookup(client, ids)
    models = _build_models(client, ids, state_rows, lookup)
    models += _build_models(client, ids, county_rows, lookup)
    logger.info("  %d regions ready", len(models))

    # Step 3. A folder to keep the projects together.
    logging_setup.heading("Step 3: find or create the folder")

    # GET /api/v1/impact/folder, then POST if needed  (wiki: Projects, folders)
    folder = projects.find_or_create_folder(client, FOLDER_NAME)
    logger.info("  folder '%s' id %s", folder.title, folder.id)

    # Step 4. One project per region.
    logging_setup.heading("Step 4: one Project per region")
    dollar_year = config.current_dollar_year()

    for model in models:
        logger.info("  %s", model.description)

        # POST /api/v1/impact/project  (wiki: Create Project)
        project = projects.create_project(
            client,
            Project(
                title=config.unique_title(model.description),
                aggregation_scheme_id=ids.aggregation_scheme_id,
                household_set_id=ids.household_set_id,
                folder_id=folder.folder_id_for_project,
            ),
        )

        created = _add_events_from_csv(client, project, event_rows)

        # POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
        groups.create_group(
            client,
            project.id,
            Group(
                title=config.unique_title(model.description),
                hash_id=model.hash_id,
                dataset_id=ids.dataset_id,
                dollar_year=dollar_year,
                group_events=[GroupEvent(event_id=event.id) for event in created],
            ),
        )

        _run_and_download(client, project, model.description[:40])

    # Step 5. One project holding every region, so the whole set can be read as a
    # single analysis.
    logging_setup.heading("Step 5: one Project holding every region")

    combined_project = projects.create_project(
        client,
        Project(
            title=config.unique_title("All Models"),
            aggregation_scheme_id=ids.aggregation_scheme_id,
            household_set_id=ids.household_set_id,
            folder_id=folder.folder_id_for_project,
        ),
    )
    logger.info("  %s", combined_project.describe())

    # The events are created once and shared by every group, exactly as in the
    # MultiEventToMultiGroup workflow.
    all_events = _add_events_from_csv(client, combined_project, event_rows)
    event_links = [GroupEvent(event_id=event.id) for event in all_events]

    for model in models:
        groups.create_group(
            client,
            combined_project.id,
            Group(
                title=config.unique_title(model.description),
                hash_id=model.hash_id,
                dataset_id=ids.dataset_id,
                dollar_year=dollar_year,
                group_events=event_links,
            ),
        )
    logger.info("  %d groups added", len(models))

    _run_and_download(client, combined_project, "all-models")

    logging_setup.heading("Done")
    logger.info("Folder:  %s", FOLDER_NAME)
    logger.info("Regions: %d", len(models))
    logger.info("Reports: %s", config.REPORTS_DIRECTORY / FOLDER_NAME)
    logger.info("")
    logger.info("Delete the folder and its projects from IMPLAN Cloud when you are done.")
