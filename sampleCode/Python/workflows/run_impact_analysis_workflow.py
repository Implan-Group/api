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

from endpoints import impact_results, impacts, projects
from models.results import ImpactResultsExportRequest, ResultFilters
from utilities import auth, config, logging_setup

# The five standard reports, and the file each is saved as.
REPORTS = [
    ("Summary Economic Indicators", impact_results.get_summary_economic_indicators),
    ("Detailed Economic Indicators", impact_results.get_detailed_economic_indicators),
    ("Summary Taxes", impact_results.get_summary_taxes),
    ("Detailed Taxes", impact_results.get_detailed_taxes),
]


def _safe_folder_name(text: str) -> str:
    """Turn a project title into something safe to use as a folder name."""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", text).strip().rstrip(".")
    return cleaned[:120] or "impact-results"


def run(project_id: str | None = None) -> int:
    """Run a project, wait for it, download the reports, and return the run id."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Find the project. Passing an id is the normal path; without one, the
    # most recently created project is used, which makes this easy to chain after
    # CreateProject.
    logging_setup.heading("Step 1: find the Project")
    if project_id is None:
        # GET /api/v1/impact/project  (wiki: Get Projects)
        mine = projects.get_projects(client)
        if not mine:
            raise LookupError(
                "You have no projects. Run the CreateProject workflow first, or "
                "pass --project-id."
            )
        # The API returns projects oldest first, so the newest is last.
        project = mine[-1]
        logger.info("  no --project-id given, so using your most recent project")
    else:
        # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
        project = projects.get_project(client, project_id)

    logger.info("  %s", project.describe())

    # Projects other people have shared with you can be run too; this is how you
    # find them.
    # GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
    shared = projects.get_shared_projects(client)
    logger.info("  (%d projects have also been shared with you)", len(shared))

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

    # Cancelling is the other half of this endpoint pair. Not run here, but this is
    # the call:
    #
    #   impacts.cancel_impact(client, run_id)
    #
    # PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)

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

    # Estimated Growth Percentage is the odd one out: its filters go in a JSON body
    # on a GET, and all five lists have to be present even when empty.
    growth_request = ImpactResultsExportRequest(dollar_year=config.current_dollar_year())

    # GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
    # (wiki: Results - Estimated Growth Percentage)
    growth_csv = impact_results.get_estimated_growth_percentage(
        client, run_id, growth_request
    )
    impact_results.save_csv(growth_csv, destination / "Estimated Growth Percentage.csv")

    # Step 5. Confirm what landed. A report whose first line is JSON rather than a
    # header row means something went wrong that the status check did not catch.
    logging_setup.heading("Step 5: check the files")
    for path in sorted(destination.glob("*.csv")):
        with open(path, encoding="utf-8") as handle:
            first_line = handle.readline().strip()
        looks_like_csv = "," in first_line and not first_line.startswith("{")
        logger.info(
            "  %-34s %s  %s",
            path.name,
            "ok " if looks_like_csv else "??",
            first_line[:60],
        )

    logging_setup.heading("Done")
    logger.info("Run id:  %d", run_id)
    logger.info("Reports: %s", destination)
    return run_id
