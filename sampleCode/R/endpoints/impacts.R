# Running an impact, and waiting for it.
#
# Running is asynchronous. The POST returns a run id straight away, the analysis
# takes a few minutes, and the status endpoint says when results are ready.
#
# Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts


# Starts an impact analysis and returns its run id.
#
# POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
#
# The Project needs at least one Group holding at least one Event. The response
# body is the run id as a bare number, not an object.
#
# The run id coming back does not mean the analysis started successfully; that is
# what the status endpoint is for.
run_impact <- function(client, project_id) {
  as.integer(post_json(client, sprintf("/api/v1/impact/%s", project_id)))
}


# Reads where an impact run has got to.
#
# GET /api/v1/impact/status/{runId}  (wiki: Get Impact Status)
#
# The body is a bare string. Anything other than "Complete" means not ready;
# "Error" and "UserCancelled" mean it stopped and will not produce results.
#
# A 404 is also terminal and means something specific: the run never attached to
# a project. The usual cause is a Group saved without a dollar year. Retrying
# does not help; fix the Group and run again.
get_impact_status <- function(client, run_id) {
  raw <- get_json(client, sprintf("/api/v1/impact/status/%s", run_id))
  text <- gsub('^"|"$', "", trimws(as.character(raw)))

  if (!text %in% IMPACT_STATUSES) {
    # A status this sample has not seen. Report it rather than guessing.
    log_debug(sprintf("Unrecognized impact status '%s'", text))
    return(IMPACT_STATUSES[["UNKNOWN"]])
  }
  text
}


# Cancels a running impact analysis.
#
# PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)
#
# Useful when a run is taking far longer than expected, or when you spotted a
# mistake in the Project. Answers with a short sentence confirming the
# cancellation.
cancel_impact <- function(client, run_id) {
  as.character(put_json(client, sprintf("/api/v1/impact/cancel/%s", run_id)))
}


# Polls until an impact run finishes, and returns its final status.
#
# Stops on a terminal failure, on a 404 meaning the run never attached, and on a
# run that has not finished inside `timeout_seconds`.
#
# Poll this endpoint and not the results endpoints. The status call is cheap; the
# results endpoints are not, and reading one before the run is complete produces
# an error that looks like a different problem.
wait_for_impact <- function(client,
                            run_id,
                            timeout_seconds = IMPACT_TIMEOUT_SECONDS,
                            poll_seconds = IMPACT_POLL_SECONDS) {
  deadline <- Sys.time() + timeout_seconds
  last_status <- ""

  repeat {
    status <- tryCatch(
      get_impact_status(client, run_id),
      implan_api_error = function(condition) {
        if (condition$status == 404L) {
          stop(
            sprintf(
              paste0(
                "Impact run %s has no analyses, which means it never attached to the ",
                "project. The usual cause is a Group saved without a dollar year. This ",
                "is terminal: fix the Group and run the Project again.\n%s"
              ),
              run_id, describe(condition$problem)
            ),
            call. = FALSE
          )
        }
        stop(condition)
      }
    )

    if (!identical(status, last_status)) {
      last_status <- status
      log_info("  run %s: %s", run_id, status)
    }

    if (identical(status, IMPACT_STATUSES[["COMPLETE"]])) {
      return(status)
    }

    if (is_terminal_failure(status)) {
      stop(
        sprintf(
          paste0(
            "Impact run %s ended with status '%s'. Check the Project's Events and ",
            "Groups in IMPLAN Cloud, then run it again."
          ),
          run_id, status
        ),
        call. = FALSE
      )
    }

    if (Sys.time() >= deadline) {
      stop(
        sprintf(
          paste0(
            "Impact run %s was still '%s' after %d seconds. It may still finish; check ",
            "the Project in IMPLAN Cloud."
          ),
          run_id, status, timeout_seconds
        ),
        call. = FALSE
      )
    }

    Sys.sleep(poll_seconds)
  }
}
