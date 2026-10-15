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
# The body is a bare word such as "Complete", sent as plain text rather than as
# JSON. get_json() falls back to the trimmed text when a body is not JSON, which is
# why reading it that way works. Anything other than "Complete" means not ready;
# "Error" and "UserCancelled" mean it stopped and will not produce results.
#
# A 404 means the run has no analyses. For a few seconds after a run starts that
# is normal, because the analyses are still being created; see wait_for_impact(),
# which allows for it. A 404 that persists means the run never attached to a
# project.
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
# Stops on a terminal failure, on a 404 that outlasts the start-up window, and on
# a run that has not finished inside `timeout_seconds`.
#
# Poll this endpoint and not the results endpoints. The status call is cheap; the
# results endpoints are not, and reading one before the run is complete produces
# an error that looks like a different problem.
#
# Expect a 404 on the first poll. For a few seconds after a run starts its
# analyses do not exist yet, and status answers 404 "No analyses exist" until they
# do; on INT the window was under 20 seconds. So a 404 is treated as "not
# registered yet" for the first IMPACT_START_GRACE_SECONDS, and only a 404 that
# persists past that is reported as a run that never attached.
wait_for_impact <- function(client,
                            run_id,
                            timeout_seconds = IMPACT_TIMEOUT_SECONDS,
                            poll_seconds = IMPACT_POLL_SECONDS) {
  started <- Sys.time()
  deadline <- started + timeout_seconds
  last_status <- ""
  said_not_registered <- FALSE

  repeat {
    status <- tryCatch(
      get_impact_status(client, run_id),
      implan_api_error = function(condition) {
        if (condition$status != 404L) {
          stop(condition)
        }

        waited <- as.numeric(difftime(Sys.time(), started, units = "secs"))
        if (waited < IMPACT_START_GRACE_SECONDS) {
          # Not registered yet. NA tells the loop below to wait and ask again.
          return(NA_character_)
        }

        stop(
          sprintf(
            paste0(
              "Impact run %s still has no analyses after %d seconds, which means it ",
              "never attached to the project. A common cause is a Group saved without ",
              "a dollar year. This is terminal: fix the Group and run the Project ",
              "again.\n%s"
            ),
            run_id, IMPACT_START_GRACE_SECONDS, describe(condition$problem)
          ),
          call. = FALSE
        )
      }
    )

    if (is.na(status)) {
      if (!said_not_registered) {
        log_info("  run %s: starting, not registered yet", run_id)
        said_not_registered <- TRUE
      }
      Sys.sleep(poll_seconds)
      next
    }

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
