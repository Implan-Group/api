# The packages these samples need, and a one-line way to install them.
#
# Run this once before the first workflow:
#
#   Rscript packages.R
#
# Two packages, both from CRAN:
#
#   httr2     the HTTP client. Everything the samples do with the network goes
#             through it, including the bearer token, the retries, and the rate
#             limiting.
#   jsonlite  reading and writing JSON.
#
# `curl` comes along with httr2 and is used directly in one place, for the
# multipart upload in the ImportEvents workflow.
#
# Nothing else is needed. Reading the `.env` file, parsing the command line, and
# reading the CSV inputs are all done with base R, so there is less to install
# and less to read that is not about the API.

REQUIRED_PACKAGES <- c(
  httr2 = "1.2.0", # req_throttle(capacity=), req_get_headers(), req_get_body()
  jsonlite = "1.8.0"
)

# The native pipe |> and the \(x) lambda shorthand both arrived in R 4.1, and the
# samples use them throughout.
MINIMUM_R_VERSION <- "4.1.0"


# Returns a library folder this user can write to, creating it if needed.
#
# This matters on a fresh install. R's default library sits inside the R
# installation, under Program Files on Windows and /usr/lib on Linux, and a
# standard user cannot write there. An interactive session offers to create a
# personal library instead; a script run with Rscript is not asked, so
# `install.packages()` simply fails with "unable to install packages".
#
# R already names the personal library in `R_LIBS_USER`, so the fix is to create
# that folder and put it on the search path rather than to invent a location.
user_library <- function() {
  # The variable can hold several paths; the first is the one R would use.
  path <- strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep, fixed = TRUE)[[1]][1]

  if (is.na(path) || !nzchar(path)) {
    # No personal library configured, so fall back to whatever is already
    # writable, which on most Linux and macOS setups is the site library.
    writable <- Filter(function(candidate) file.access(candidate, mode = 2) == 0, .libPaths())
    if (length(writable) == 0L) {
      stop(
        "No writable R library was found, and R_LIBS_USER is not set.\n",
        "Set R_LIBS_USER to a folder you can write to and run this again.",
        call. = FALSE
      )
    }
    return(writable[[1]])
  }

  path <- path.expand(path)
  if (!dir.exists(path)) {
    message("Creating your personal R library at ", path)
    dir.create(path, recursive = TRUE, showWarnings = FALSE)
  }

  if (!dir.exists(path)) {
    stop("Could not create an R library at ", path, ".", call. = FALSE)
  }

  # Put it first so this session installs into it and finds what it installed.
  if (!path %in% .libPaths()) {
    .libPaths(c(path, .libPaths()))
  }
  path
}


# Installs anything missing, and reports anything too old.
install_required_packages <- function(repos = "https://cloud.r-project.org") {
  if (getRversion() < MINIMUM_R_VERSION) {
    stop(
      "These samples need R ", MINIMUM_R_VERSION, " or newer; this is ",
      getRversion(), ". Download the current release from https://cran.r-project.org.",
      call. = FALSE
    )
  }

  library_path <- user_library()
  message("Installing into ", library_path)

  for (package_name in names(REQUIRED_PACKAGES)) {
    wanted <- REQUIRED_PACKAGES[[package_name]]
    installed <- tryCatch(
      as.character(utils::packageVersion(package_name)),
      error = function(condition) NA_character_
    )

    if (is.na(installed)) {
      message("Installing ", package_name, " ...")
      utils::install.packages(package_name, lib = library_path, repos = repos)
    } else if (package_version(installed) < package_version(wanted)) {
      message(
        "Updating ", package_name, " from ", installed, " to at least ", wanted, " ..."
      )
      utils::install.packages(package_name, lib = library_path, repos = repos)
    } else {
      message(package_name, " ", installed, " is already installed.")
    }
  }

  invisible(NULL)
}


# Stops with a clear message when something is missing, rather than letting a
# workflow fail on an unexplained "could not find function".
check_required_packages <- function() {
  if (getRversion() < MINIMUM_R_VERSION) {
    stop(
      "These samples need R ", MINIMUM_R_VERSION, " or newer; this is ", getRversion(), ".",
      call. = FALSE
    )
  }

  for (package_name in names(REQUIRED_PACKAGES)) {
    wanted <- REQUIRED_PACKAGES[[package_name]]
    installed <- tryCatch(
      as.character(utils::packageVersion(package_name)),
      error = function(condition) NA_character_
    )

    if (is.na(installed)) {
      stop(
        "The '", package_name, "' package is not installed.\n",
        "Run this once, from this folder:  Rscript packages.R",
        call. = FALSE
      )
    }

    if (package_version(installed) < package_version(wanted)) {
      stop(
        "The '", package_name, "' package is version ", installed,
        "; these samples need ", wanted, " or newer.\n",
        "Run this from this folder:  Rscript packages.R",
        call. = FALSE
      )
    }
  }

  invisible(NULL)
}


# Running this file directly installs; sourcing it from main.R only defines the
# two functions above.
if (identical(environment(), globalenv()) && !interactive()) {
  args <- commandArgs(trailingOnly = FALSE)
  this_file <- sub("^--file=", "", grep("^--file=", args, value = TRUE))
  if (length(this_file) == 1L && identical(basename(this_file), "packages.R")) {
    install_required_packages()
  }
}
