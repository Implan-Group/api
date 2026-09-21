# Reading the results of a completed impact run.
#
# Every endpoint here returns CSV as text. Save it with a `.csv` extension and it
# opens in Excel or Sheets. All of them take the same optional filters, so the
# same run can be read whole or sliced by region, impact type, group, event, or
# tag.
#
# Only read these once the run reports "Complete".
#
# Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results


RESULTS_PATH <- "/api/v1/impact/results"


# Employment, Labor Income, Value Added, and Output by impact type.
#
# GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}
# (wiki: Results - Summary Economic Indicators)
#
# The headline report, and the one to start with. Rows are split Direct,
# Indirect, and Induced for each Group, Event, and Region.
get_summary_economic_indicators <- function(client, run_id, filters = NULL) {
  get_text(
    client,
    sprintf("%s/SummaryEconomicIndicators/%s", RESULTS_PATH, run_id),
    query = filters_to_query(filters)
  )
}


# The same indicators, broken out by industry.
#
# GET /api/v1/impact/results/ExportDetailEconomicIndicators/{runId}
# (wiki: Results - Detailed Economic Indicators)
#
# Note the year in parentheses after a Group or Model name in this report: that
# is the Data Year of the underlying dataset, not the Dollar Year the figures are
# expressed in. They differ whenever you analyze an older data year in today's
# dollars.
get_detailed_economic_indicators <- function(client, run_id, filters = NULL) {
  get_text(
    client,
    sprintf("%s/ExportDetailEconomicIndicators/%s", RESULTS_PATH, run_id),
    query = filters_to_query(filters)
  )
}


# Tax revenue by level of government.
#
# GET /api/v1/impact/results/SummaryTaxes/{runId}
# (wiki: Results - Summary Taxes)
get_summary_taxes <- function(client, run_id, filters = NULL) {
  get_text(
    client,
    sprintf("%s/SummaryTaxes/%s", RESULTS_PATH, run_id),
    query = filters_to_query(filters)
  )
}


# Tax revenue by tax type and level of government.
#
# GET /api/v1/impact/results/DetailedTaxes/{runId}
# (wiki: Results - Detailed Taxes)
get_detailed_taxes <- function(client, run_id, filters = NULL) {
  get_text(
    client,
    sprintf("%s/DetailedTaxes/%s", RESULTS_PATH, run_id),
    query = filters_to_query(filters)
  )
}


# How large the impact is relative to each industry already in the region.
#
# GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}
# (wiki: Results - Estimated Growth Percentage)
#
# This one is different from its neighbours in two ways, and both matter.
#
# First, it takes its filters as a JSON body rather than as query parameters, on
# a GET. That is unusual, it is what the endpoint requires, and IMPLAN's API
# Gateway passes the body through, so do not rewrite it as a POST or move the
# filters to the query string.
#
# Second, all five filter lists have to be present even when empty. Send [] for
# any dimension you are not filtering on; omitting one is an error rather than a
# default. `impact_results_export_request()` defaults them to empty vectors for
# exactly this reason, and `to_api()` keeps them as arrays.
#
# A 409 means the run has not finished, or that its project has no completed run
# to compare against.
get_estimated_growth_percentage <- function(client, run_id, request_body) {
  get_text(
    client,
    sprintf("%s/EstimatedGrowthPercentage/%s", RESULTS_PATH, run_id),
    body = to_api(request_body)
  )
}


# The four reports that share the query-string filters, and the label each is
# saved under. Two workflows download exactly this set, so it lives here rather
# than in one of them.
#
# Estimated Growth Percentage is deliberately absent: its filters go in a body
# rather than on the query string, so it does not share this shape.
STANDARD_REPORTS <- list(
  list(label = "Summary Economic Indicators", fetch = get_summary_economic_indicators),
  list(label = "Detailed Economic Indicators", fetch = get_detailed_economic_indicators),
  list(label = "Summary Taxes", fetch = get_summary_taxes),
  list(label = "Detailed Taxes", fetch = get_detailed_taxes)
)


# Writes a CSV report to disk, creating the folder if it is not there.
#
# `useBytes = TRUE` writes the text exactly as the API sent it, so the line
# endings survive intact rather than being doubled on Windows.
save_csv <- function(csv_text, destination) {
  directory <- dirname(destination)
  if (!dir.exists(directory)) {
    dir.create(directory, recursive = TRUE)
  }

  connection <- file(destination, open = "wb")
  on.exit(close(connection), add = TRUE)
  writeChar(csv_text, connection, eos = NULL, useBytes = TRUE)

  log_info("  saved %s", destination)
  invisible(destination)
}


# Counts the data rows in a CSV report, ignoring the header and any blank lines.
#
# The workflows print this so the console says something useful without trying to
# parse a report whose columns vary by account.
csv_data_row_count <- function(csv_text) {
  lines <- strsplit(csv_text, "\r?\n")[[1]]
  max(sum(nzchar(trimws(lines))) - 1L, 0L)
}
