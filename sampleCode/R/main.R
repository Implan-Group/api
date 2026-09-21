# IMPLAN Impact API samples: the entry point.
#
# Run one workflow at a time:
#
#   Rscript main.R authentication
#   Rscript main.R identifiers
#   Rscript main.R create-project
#   Rscript main.R run-impact-analysis --project-id <guid>
#
# `Rscript main.R --list` prints every workflow with a one-line description.
#
# From an R console or RStudio, source this file and then call a workflow by
# name:
#
#   source("main.R")
#   run_workflow("regions")
#
# Each workflow is a file in `workflows/`, written to be read top to bottom.
# Start with `authentication`, then `identifiers`, then follow the numbered
# order.
#
# Before the first run, copy `.env.example` to `.env` and put your IMPLAN
# username and password in it. See README.md.


# Works out the folder this file lives in.
#
# R has no equivalent of __file__, so this tries the three ways this file is
# normally reached, most specific first.
find_sample_root <- function() {
  # 1. source() records the file it is reading in `ofile` on its own frame. This
  #    is checked before the command line because it is the more specific
  #    answer: when one script sources another, `--file=` names the outer script
  #    and only `ofile` names this one. RStudio's Source button lands here too.
  for (frame in rev(sys.frames())) {
    if (!is.null(frame$ofile)) {
      return(normalizePath(dirname(frame$ofile), winslash = "/"))
    }
  }

  # 2. Rscript passes the script it was given as `--file=`, which is this file
  #    when the samples are started with `Rscript main.R`.
  arguments <- commandArgs(trailingOnly = FALSE)
  file_argument <- grep("^--file=", arguments, value = TRUE)
  if (length(file_argument) == 1L) {
    return(normalizePath(dirname(sub("^--file=", "", file_argument)), winslash = "/"))
  }

  # 3. Last resort: the working directory, walked up until main.R is found, so
  #    running from `workflows/` still works.
  directory <- normalizePath(getwd(), winslash = "/")
  repeat {
    if (file.exists(file.path(directory, "main.R"))) {
      return(directory)
    }
    parent <- dirname(directory)
    if (identical(parent, directory)) {
      stop(
        "Could not work out where the samples live. Set the working directory to ",
        "the folder holding main.R and try again.",
        call. = FALSE
      )
    }
    directory <- parent
  }
}


# Loads every file in the sample, in dependency order.
#
# R has no module system, so the order matters: configuration first, then the
# HTTP plumbing, then the models, then the endpoints that use them, then the
# workflows on top.
load_samples <- function(root = find_sample_root()) {
  options(implan.sample_root = root)

  source(file.path(root, "packages.R"), local = FALSE)
  check_required_packages()

  source(file.path(root, "utilities", "config.R"))
  load_env_file()

  for (folder in c("utilities", "models", "endpoints", "workflows")) {
    files <- sort(list.files(file.path(root, folder), pattern = "\\.R$", full.names = TRUE))
    for (path in files) {
      # config.R is already loaded, and loading it twice would be harmless but
      # confusing to trace.
      if (!identical(basename(path), "config.R")) {
        source(path)
      }
    }
  }

  invisible(root)
}


# Every workflow, in the order of the set.
#
# The name is what you type on the command line; the function is what runs; the
# description is what `--list` prints. Keeping the names identical to the C# and
# Python samples means a workflow can be compared across languages by name.
workflow_catalog <- function() {
  list(
    list(
      name = "authentication",
      description = "1  Get a bearer token, cache it, and verify it",
      run = function(options) authentication_workflow()
    ),
    list(
      name = "identifiers",
      description = "2  Resolve the current scheme, dataset, and industry codes",
      run = function(options) identifiers_workflow()
    ),
    list(
      name = "regions",
      description = "3  Walk the region hierarchy and find regions by name",
      run = function(options) regions_workflow()
    ),
    list(
      name = "combine-regions",
      description = "4  Combine two counties and wait for the model to build",
      run = function(options) combine_regions_workflow()
    ),
    list(
      name = "create-project",
      description = "5  Create a project with two events and one group",
      run = function(options) create_project_workflow(options$map_code)
    ),
    list(
      name = "multi-event-to-multi-group",
      description = "6  The same events across three states",
      run = function(options) multi_event_to_multi_group_workflow(options$project_id)
    ),
    list(
      name = "run-impact-analysis",
      description = "7  Run a project and download the five standard reports",
      run = function(options) run_impact_analysis_workflow(options$project_id)
    ),
    list(
      name = "bulk-from-csv",
      description = "8  Build regions, projects, and runs from CSV input files",
      run = function(options) bulk_from_csv_workflow()
    ),
    list(
      name = "regional-exports",
      description = "9  Download a regional data export for many regions",
      run = function(options) {
        regional_exports_workflow(
          region_type = options$region_type,
          export_name = options$export_name,
          limit = options$limit
        )
      }
    ),
    list(
      name = "import-events",
      description = "10 Fill a project from an IMPLAN Event Template workbook",
      run = function(options) import_events_workflow(options$workbook)
    ),
    list(
      name = "mrio-project",
      description = "11 Multi-regional analysis, with spillover between regions",
      run = function(options) mrio_project_workflow()
    ),
    list(
      name = "advanced-events",
      description = "12 Contribution and spending-pattern events, with tags",
      run = function(options) advanced_events_workflow()
    )
  )
}


# Prints the workflows and the options they take.
print_workflows <- function() {
  cat("IMPLAN Impact API sample workflows\n\n")
  for (workflow in workflow_catalog()) {
    cat(sprintf("  %-28s %s\n", workflow$name, workflow$description))
  }
  cat("\nRun one with:  Rscript main.R <name>\n")
  cat("\nOptions:\n")
  cat("  --project-id <guid>   an existing project, for the workflows that take one\n")
  cat("  --map-code <code>     US, CAN, or INTL (create-project)\n")
  cat("  --region-type <type>  Country, State, Msa, County, CongressionalDistrict,\n")
  cat("                        or Zipcode (regional-exports)\n")
  cat("  --export-name <name>  which regional data export to download\n")
  cat("  --limit <n>           how many regions to process, or 0 for all\n")
  cat("  --workbook <path>     a filled Event Template workbook (import-events)\n")
  cat("\nDetails for every workflow:  README.md and ../../CLAUDE.md\n")
  invisible(NULL)
}


# The command line, parsed.
#
# Hand-written rather than taken from a package, because the samples keep their
# dependencies to two and because a reader should not have to learn an argument
# library to follow them. The shape matches the C# and Python samples: one
# workflow name, then optional `--name value` pairs.
parse_arguments <- function(arguments) {
  options <- list(
    workflow = NULL,
    show_list = FALSE,
    project_id = NULL,
    map_code = MAP_CODES[["US"]],
    region_type = "Msa",
    export_name = REGION_OVERVIEW_INDUSTRIES,
    limit = 10,
    workbook = NULL
  )

  index <- 1L
  while (index <= length(arguments)) {
    argument <- arguments[index]

    next_value <- function() {
      if (index + 1L > length(arguments)) {
        stop(sprintf("%s needs a value after it.", argument), call. = FALSE)
      }
      arguments[index + 1L]
    }

    if (argument %in% c("--list", "-l", "--help", "-h")) {
      options$show_list <- TRUE
    } else if (identical(argument, "--project-id")) {
      options$project_id <- next_value()
      index <- index + 1L
    } else if (identical(argument, "--map-code")) {
      options$map_code <- toupper(next_value())
      index <- index + 1L
    } else if (identical(argument, "--region-type")) {
      options$region_type <- next_value()
      index <- index + 1L
    } else if (identical(argument, "--export-name")) {
      options$export_name <- next_value()
      index <- index + 1L
    } else if (identical(argument, "--limit")) {
      # 0 means no cap, which is how the C# and Python samples spell it too.
      parsed <- suppressWarnings(as.integer(next_value()))
      options$limit <- if (is.na(parsed) || parsed <= 0L) NULL else parsed
      index <- index + 1L
    } else if (identical(argument, "--workbook")) {
      options$workbook <- next_value()
      index <- index + 1L
    } else if (startsWith(argument, "-")) {
      stop(
        sprintf("Unknown option '%s'. Run with --list to see the options.", argument),
        call. = FALSE
      )
    } else if (is.null(options$workflow)) {
      options$workflow <- argument
    }

    index <- index + 1L
  }

  options
}


# Runs one workflow by name. This is what to call from an R console after
# sourcing this file.
run_workflow <- function(name, ...) {
  options <- parse_arguments(c(name, ...))

  for (workflow in workflow_catalog()) {
    if (identical(workflow$name, options$workflow)) {
      log_info("IMPLAN Impact API sample: %s", workflow$name)
      log_info("API: %s", implan_base_url())
      log_debug(sprintf(
        "Starting workflow %s against %s", workflow$name, implan_base_url()
      ))
      return(invisible(workflow$run(options)))
    }
  }

  stop(
    sprintf(
      "Unknown workflow '%s'. Run print_workflows() to see the twelve names.",
      options$workflow
    ),
    call. = FALSE
  )
}


# Runs the command line and returns an exit code.
#
# 0 success, 2 authentication, 3 the API refused the request, 4 a problem with
# the input or the account, so a scheduler or a CI job can tell what went wrong.
main <- function(arguments = commandArgs(trailingOnly = TRUE)) {
  options <- parse_arguments(arguments)

  if (isTRUE(options$show_list) || is.null(options$workflow)) {
    print_workflows()
    return(0L)
  }

  known <- vapply(workflow_catalog(), function(workflow) workflow$name, character(1))
  if (!options$workflow %in% known) {
    cat(sprintf("Unknown workflow '%s'.\n\n", options$workflow))
    print_workflows()
    return(4L)
  }

  tryCatch(
    {
      do.call(run_workflow, as.list(arguments))
      0L
    },
    implan_authentication_error = function(condition) {
      # Credentials or subscription. The message says which.
      log_info("")
      log_info("Authentication failed.")
      log_info(conditionMessage(condition))
      2L
    },
    implan_api_error = function(condition) {
      # The API refused the request and said why. Quote the traceId to support.
      log_info("")
      log_info("The API returned an error.")
      log_info(conditionMessage(condition))
      log_info("")
      log_info("Full request and response detail: %s", log_file_path())
      3L
    },
    error = function(condition) {
      # Everything the workflows raise deliberately: a missing input file, a
      # region or industry that is not in this dataset, a run that failed.
      log_info("")
      log_info(conditionMessage(condition))
      4L
    }
  )
}


# Loading this file always makes the samples available. It additionally runs the
# command line, and exits with a status code, only when this file is the script
# Rscript was handed.
#
# The test is which file `--file=` names, not `interactive()`. Sourcing this file
# from another script is a non-interactive context too, and keying off that would
# make `source("main.R")` run the command line and then quit out of the caller's
# session.
load_samples()

started_directly <- function() {
  arguments <- commandArgs(trailingOnly = FALSE)
  file_argument <- grep("^--file=", arguments, value = TRUE)
  length(file_argument) == 1L &&
    identical(basename(sub("^--file=", "", file_argument)), "main.R")
}

if (started_directly()) {
  quit(status = main(), save = "no")
}
