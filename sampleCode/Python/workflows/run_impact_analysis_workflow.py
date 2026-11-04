"""Workflow 7: RunImpactAnalysis.

Goal: run a project, wait for it correctly, and download every standard report.

Running is asynchronous. The POST returns a run id immediately and the analysis
takes a few minutes, so the interesting part of this workflow is the waiting, and
specifically knowing when to stop:

  - `Complete` means the results are ready.
  - `Error` and `UserCancelled` are terminal. Polling past them waits forever,
    which is the bug in most first attempts at this.
  - A 404 from the status endpoint is also terminal, and means the run never
    attached to a project. The usual cause is a Group saved without a dollar year.

Poll the status endpoint and not the results endpoints. Status is cheap; results
are not, and reading one before the run finishes produces an error that reads like
a different problem.

Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results
"""

import re

from endpoints import aggregation_schemes, impact_results, impacts, projects
from models.reference import MapCode
from models.results import ImpactResultsExportRequest, ImpactType, ResultFilters
from utilities import auth, config, logging_setup

# The query-filtered reports, and the file each is saved as. Summary Taxes is read
# separately, because its route depends on the Project's country.
REPORTS = [
    ("Summary Economic Indicators", impact_results.get_summary_economic_indicators),
    ("Detailed Economic Indicators", impact_results.get_detailed_economic_indicators),
    ("Detailed Taxes", impact_results.get_detailed_taxes),
]


def _safe_folder_name(text: str) -> str:
    """Turn a project title into something safe to use as a folder name."""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", text).strip().rstrip(".")
    return cleaned[:120] or "impact-results"


def run(project_id: str | None = None) -> int:
    """Run a project, wait for it, download the reports, and return the run id."""
    logger = logging_setup.get_logger()

    # The project to run is always named. The API documents no order for the list
    # of your projects, so "the most recent one" cannot be picked from it safely.
    if not project_id:
        raise ValueError(
            "Name the project to run with --project-id. The CreateProject and "
            "ImportEvents workflows print the id of the project they create."
        )

    client = auth.create_client()

    # Step 1. Find the project, and the country its Aggregation Scheme covers, which
    # decides the Summary Taxes route in Step 4.
    logging_setup.heading("Step 1: find the Project")

    # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
    project = projects.get_project(client, project_id)
    logger.info("  %s", project.describe())

    # GET /api/v1/aggregationSchemes/{aggregationSchemeId}  (wiki: Aggregation Scheme by Id)
    scheme = aggregation_schemes.get_aggregation_scheme(client, project.aggregation_scheme_id)
    map_code = MapCode(scheme.map_code)
    logger.info("  Aggregation Scheme %d covers %s data", scheme.id, map_code.value)

    # Your own projects, and the ones other people have shared with you, can all be
    # run; these two lists are where to find the id to pass.
    # GET /api/v1/impact/project  (wiki: Get Projects)
    mine = projects.get_projects(client)
    # GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
    shared = projects.get_shared_projects(client)
    logger.info("  (you have %d projects of your own, and %d shared with you)", len(mine), len(shared))

    # Step 2. Start the run.
    logging_setup.heading("Step 2: start the impact")

    # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
    run_id = impacts.run_impact(client, project.id)
    logger.info("  run id %d", run_id)
    logger.info("  a run id means the request was accepted, not that it succeeded")

    # Step 3. Wait. The helper handles the terminal states and the timeout, which
    # is the part worth copying.
    logging_setup.heading("Step 3: wait for it to finish")
    logger.info(
        "  polling every %ds, giving up after %d minutes",
        config.IMPACT_POLL_SECONDS,
        config.IMPACT_TIMEOUT_SECONDS // 60,
    )

    # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
    impacts.wait_for_impact(client, run_id)
    logger.info("  complete")

    # Step 4. Download the reports. Every one of them is CSV text.
    logging_setup.heading("Step 4: download the results")
    destination = config.REPORTS_DIRECTORY / _safe_folder_name(project.title)

    # Setting the dollar year explicitly keeps repeated runs comparable. Left
    # unset, the API uses your account preference, which may differ from a
    # colleague's.
    filters = ResultFilters(year=config.current_dollar_year())
    logger.info("  dollar year %d", filters.year)

    for label, fetch in REPORTS:
        # GET /api/v1/impact/results/...  (wiki: Impact Results)
        csv_text = fetch(client, run_id, filters)
        impact_results.save_csv(csv_text, destination / f"{label}.csv")

    # GET /api/v1/impact/results/SummaryTaxes/{runId}, or its can/ or intl/ route
    # (wiki: Results - Summary Taxes)
    taxes_csv = impact_results.get_summary_taxes(client, run_id, filters, map_code)
    impact_results.save_csv(taxes_csv, destination / "Summary Taxes.csv")

    # Estimated Growth Percentage is the odd one out: its filters go in a JSON body
    # on a GET, and all five lists have to be present even when empty.
    growth_request = ImpactResultsExportRequest(dollar_year=config.current_dollar_year())

    # GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
    # (wiki: Results - Estimated Growth Percentage)
    growth_csv = impact_results.get_estimated_growth_percentage(
        client, run_id, growth_request
    )
    impact_results.save_csv(growth_csv, destination / "Estimated Growth Percentage.csv")

    # The CSV reports all take the same filters. `impacts` keeps only the effects
    # you name, out of Direct, Indirect, and Induced, so this reads the headline
    # report again for the activity itself, without its supply chain or household
    # spending.
    direct_filters = ResultFilters(
        year=config.current_dollar_year(),
        impacts=[ImpactType.DIRECT.value],
    )

    # GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?impacts=Direct
    # (wiki: Results - Summary Economic Indicators)
    direct_csv = impact_results.get_summary_economic_indicators(client, run_id, direct_filters)
    impact_results.save_csv(direct_csv, destination / "Summary Economic Indicators - Direct.csv")

    # Step 5. Confirm what landed. A report whose first line is JSON rather than a
    # header row means something went wrong that the status check did not catch.
    logging_setup.heading("Step 5: check the files")
    for path in sorted(destination.glob("*.csv")):
        with open(path, encoding="utf-8") as handle:
            first_line = handle.readline().strip()
        looks_like_csv = "," in first_line and not first_line.startswith("{")
        logger.info(
            "  %-42s %s  %s",
            path.name,
            "ok " if looks_like_csv else "??",
            first_line[:60],
        )

    logging_setup.heading("Done")
    logger.info("Run id:  %d", run_id)
    logger.info("Reports: %s", destination)
    return run_id
