# Configuration shared by every workflow.
#
# This file holds the handful of settings the samples need and nothing else:
# where the API lives, where credentials come from, where files are written, and
# the two conventions (a title prefix and a dollar year) that the workflows apply
# to everything they create.
#
# Credentials are read from a `.env` file that sits next to `main.R`. That file is
# listed in `.gitignore` and must never be committed. Copy `.env.example` to
# `.env` and fill in the two values.
#
# Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started


# The root of this sample, which is the folder holding `main.R`.
#
# Every other path is derived from it so the samples behave the same no matter
# which directory you start them from. `main.R` works the folder out and records
# it in an option; sourcing a file directly without going through `main.R` falls
# back to the working directory.
implan_root <- function() {
  root <- getOption("implan.sample_root")
  if (is.null(root)) {
    root <- getwd()
  }
  normalizePath(root, winslash = "/", mustWork = FALSE)
}


# Reads a `.env` file into this session's environment variables.
#
# Deliberately small rather than a package: the format needed here is
# `KEY=value`, one per line, with `#` comments and optional quotes. A variable
# that is already set in the environment is left alone, so a value exported in
# your shell or set by a CI system wins over the file.
load_env_file <- function(path = file.path(implan_root(), ".env")) {
  if (!file.exists(path)) {
    return(invisible(FALSE))
  }

  for (line in readLines(path, warn = FALSE)) {
    line <- trimws(line)
    if (!nzchar(line) || startsWith(line, "#")) {
      next
    }

    separator <- regexpr("=", line, fixed = TRUE)
    if (separator < 2) {
      next
    }

    key <- trimws(substr(line, 1, separator - 1))
    value <- trimws(substr(line, separator + 1, nchar(line)))
    value <- gsub('^["\']|["\']$', "", value)

    if (!nzchar(Sys.getenv(key))) {
      args <- list(value)
      names(args) <- key
      do.call(Sys.setenv, args)
    }
  }

  invisible(TRUE)
}


# Reads one setting, returning NULL rather than "" when it is not set.
implan_setting <- function(name, default = NULL) {
  value <- Sys.getenv(name, unset = "")
  if (nzchar(value)) value else default
}


# The host serving the API. Authentication is at `/api/auth`; everything else is
# under `/api/v1/`.
implan_base_url <- function() {
  sub("/+$", "", implan_setting("IMPLAN_API_URL", "https://api.implan.com"))
}

# Your IMPLAN sign-in, the same one you use at app.implan.com.
implan_username <- function() implan_setting("IMPLAN_USERNAME")

# Your IMPLAN password.
implan_password <- function() implan_setting("IMPLAN_PASSWORD")


# Where the bearer token is cached between runs. A token is good for 24 hours,
# and asking for a new one on every run risks a temporary ban, so the samples
# always reuse this file while the token in it still works.
token_cache_path <- function() file.path(implan_root(), "implan_auth.jwt")

# Request and response logs, one file per day.
log_directory <- function() file.path(implan_root(), "logs")

# Exported CSV reports and other downloads.
reports_directory <- function() file.path(implan_root(), "reports")

# Input files that ship with the samples.
data_directory <- function() file.path(implan_root(), "data")


# Everything these samples create in your IMPLAN account is named with this
# prefix, so you can find it later and delete it.
TITLE_PREFIX <- "ImpactApi Sample"

# How long a workflow waits for a long-running operation before giving up. An
# impact usually finishes in a couple of minutes and a combined-region build in
# under one, so these are generous.
IMPACT_TIMEOUT_SECONDS <- 15 * 60
IMPACT_POLL_SECONDS <- 15
REGION_BUILD_TIMEOUT_SECONDS <- 10 * 60
REGION_BUILD_POLL_SECONDS <- 15

# How long to wait for a single HTTP request. The gateway itself gives up at 30
# seconds, so anything longer than this is a network problem rather than a slow
# endpoint.
REQUEST_TIMEOUT_SECONDS <- 60


# Region model requests are the most tightly limited family of endpoints, so the
# two bulk workflows stay under the published five per minute. The other limits,
# ten per minute for Industry Codes and for Datasets, are not reached by any
# workflow here.
#
# Limits are on the wiki home page: https://github.com/Implan-Group/api/wiki
REGION_REQUESTS_PER_MINUTE <- 5


# The dollar year the samples use, which is the current calendar year.
#
# Dollar Year is the year results are expressed in; Data Year is the year of the
# underlying IMPLAN dataset. They are different things and often differ. The
# samples use the current year so they never go stale, and every Group they
# create carries it explicitly, because the API has no default: a Group saved
# without a dollar year produces an impact run that never attaches.
#
# Support: Which Year Is It Anyway? Data Year, Model Year, and Dollar Year
# https://support.implan.com/hc/en-us/articles/360039290593
current_dollar_year <- function() {
  as.integer(format(Sys.Date(), "%Y"))
}


# Builds a title that is unique per run and easy to find in IMPLAN Cloud.
#
# Titles must be unique for your user, and the API rejects an ampersand and the
# characters | ; % * ? ! = ' " ^ #, so keep `label` to plain words.
unique_title <- function(label) {
  sprintf("%s - %s - %s", TITLE_PREFIX, label, format(Sys.time(), "%Y%m%d-%H%M%S"))
}


# Returns the username and password, or explains exactly what is missing.
#
# Every workflow calls this before its first request, so a missing `.env` fails
# immediately with a useful message rather than as a confusing 401 later.
require_credentials <- function() {
  username <- implan_username()
  password <- implan_password()

  if (is.null(username) || is.null(password)) {
    stop(
      "IMPLAN credentials are not set.\n",
      "Copy ", file.path(implan_root(), ".env.example"), " to ",
      file.path(implan_root(), ".env"), " and fill in\n",
      "IMPLAN_USERNAME and IMPLAN_PASSWORD, or set them as environment variables.",
      call. = FALSE
    )
  }

  list(username = username, password = password)
}


# Turns a title into something safe to use as a file or folder name on Windows.
safe_file_name <- function(text, max_length = 150) {
  cleaned <- gsub('[<>:"/\\\\|?*]', "_", text)
  cleaned <- sub("\\.+$", "", trimws(cleaned))
  cleaned <- substr(cleaned, 1, max_length)
  if (nzchar(cleaned)) cleaned else "untitled"
}
