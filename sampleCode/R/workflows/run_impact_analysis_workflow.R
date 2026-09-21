# Workflow 7: RunImpactAnalysis.
#
# Goal: run a project, wait for it correctly, and download every standard report.
#
# Running is asynchronous. The POST returns a run id immediately and the analysis
# takes a few minutes, so the interesting part of this workflow is the waiting,
# and specifically knowing when to stop:
#
#   - "Complete" means the results are ready.
#   - "Error" and "UserCancelled" are terminal. Polling past them waits forever,
#     which is the bug in most first attempts at this.
#   - A 404 from the status endpoint is also terminal, and means the run never
#     attached to a project. The usual cause is a Group saved without a dollar
#     year.
#
# Poll the status endpoint and not the results endpoints. Status is cheap;
# results are not, and reading one before the run finishes produces an error that
# reads like a different problem.
#
# Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
# Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results


run_impact_analysis_workflow <- function(project_id = NULL) {
  client <- create_client()

  # Step 1. Find the project. Passing an id is the normal path; without one, the
  # most recently created project is used, which makes this easy to chain after
  # CreateProject.
  log_heading("Step 1: find the Project")
  if (is.null(project_id)) {
    # GET /api/v1/impact/project  (wiki: Get Projects)
    mine <- get_projects(client)
    if (length(mine) == 0L) {
      stop(
        "You have no projects. Run the CreateProject workflow first, or pass --project-id.",
        call. = FALSE
      )
    }
    # The API returns projects oldest first, so the newest is last.
    project <- mine[[length(mine)]]
    log_info("  no --project-id given, so using your most recent project")
  } else {
    # GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
    project <- get_project(client, project_id)
  }

  log_info("  %s", describe(project))

  # Projects other people have shared with you can be run too; this is how you
  # find them.
  # GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
  shared <- get_shared_projects(client)
  log_info("  (%d projects have also been shared with you)", length(shared))

  # Step 2. Start the run.
  log_heading("Step 2: start the impact")

  # POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
  run_id <- run_impact(client, project$id)
  log_info("  run id %d", run_id)
  log_info("  a run id means the request was accepted, not that it succeeded")

  # Step 3. Wait. The helper handles the terminal states and the timeout, which
  # is the part worth copying.
  log_heading("Step 3: wait for it to finish")
  log_info(
    "  polling every %ds, giving up after %d minutes",
    IMPACT_POLL_SECONDS, IMPACT_TIMEOUT_SECONDS %/% 60
  )

  # GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
  wait_for_impact(client, run_id)
  log_info("  complete")

  # Cancelling is the other half of this endpoint pair. Not run here, but this is
  # the call:
  #
  #   cancel_impact(client, run_id)
  #
  # PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)

  # Step 4. Download the reports. Every one of them is CSV text.
  log_heading("Step 4: download the results")
  destination <- file.path(reports_directory(), safe_file_name(project$title, 120))

  # Setting the dollar year explicitly keeps repeated runs comparable. Left
  # unset, the API uses your account preference, which may differ from a
  # colleague's.
  filters <- result_filters(year = current_dollar_year())
  log_info("  dollar year %d", filters$year)

  for (report in STANDARD_REPORTS) {
    # GET /api/v1/impact/results/...  (wiki: Impact Results)
    csv_text <- report$fetch(client, run_id, filters)
    save_csv(csv_text, file.path(destination, paste0(report$label, ".csv")))
  }

  # Estimated Growth Percentage is the odd one out: its filters go in a JSON body
  # on a GET, and all five lists have to be present even when empty.
  growth_request <- impact_results_export_request(dollar_year = current_dollar_year())

  # GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
  # (wiki: Results - Estimated Growth Percentage)
  growth_csv <- get_estimated_growth_percentage(client, run_id, growth_request)
  save_csv(growth_csv, file.path(destination, "Estimated Growth Percentage.csv"))

  # Step 5. Confirm what landed. A report whose first line is JSON rather than a
  # header row means something went wrong that the status check did not catch.
  log_heading("Step 5: check the files")
  for (path in sort(list.files(destination, pattern = "\\.csv$", full.names = TRUE))) {
    first_line <- trimws(readLines(path, n = 1, warn = FALSE))
    if (length(first_line) == 0L) {
      first_line <- ""
    }
    looks_like_csv <- grepl(",", first_line, fixed = TRUE) && !startsWith(first_line, "{")
    log_info(
      "  %-34s %s  %s",
      basename(path),
      if (looks_like_csv) "ok " else "??",
      substr(first_line, 1, 60)
    )
  }

  log_heading("Done")
  log_info("Run id:  %d", run_id)
  log_info("Reports: %s", destination)

  invisible(run_id)
}
