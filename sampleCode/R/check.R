# Checks the sample's own behavior, without a network or credentials.
#
#   Rscript check.R
#
# Exits 0 when everything passes and 1 otherwise, so it can run in CI.
#
# This is not a test suite for the API. It exercises the handful of places where
# R, jsonlite, and httr2 will quietly do something other than what this API
# needs, and where a mistake produces a request that is accepted and wrong rather
# than one that fails loudly:
#
#   - A filter with several values has to become a repeated query parameter,
#     `regions=A&regions=B`, not one comma-joined value.
#   - `auto_unbox = TRUE` turns a one-element vector into a JSON scalar, so a
#     single tag would go out as "capital" instead of ["capital"].
#   - The growth report requires all five filter arrays even when empty.
#   - `req_body_json()` switches a request to POST, so a GET that carries a body
#     has to have its method set again afterwards.
#   - The bearer token must never appear when a request is printed or logged.
#   - A response carrying a field this sample has never heard of must still read.
#
# Every one of those is invisible to a code review, which is why they are checked
# here rather than trusted.

SAMPLE_ROOT <- local({
  arguments <- commandArgs(trailingOnly = FALSE)
  file_argument <- grep("^--file=", arguments, value = TRUE)
  if (length(file_argument) == 1L) {
    normalizePath(dirname(sub("^--file=", "", file_argument)), winslash = "/")
  } else {
    normalizePath(getwd(), winslash = "/")
  }
})

source(file.path(SAMPLE_ROOT, "main.R"))


FAILURES <- 0L

# Reports one check. Keeping the expected and actual values on failure is the
# difference between a red line and knowing what to change.
ok <- function(label, actual, expected) {
  if (identical(actual, expected)) {
    cat("  PASS  ", label, "\n", sep = "")
  } else {
    FAILURES <<- FAILURES + 1L
    cat("  FAIL  ", label, "\n", sep = "")
    cat("          expected: ",
        paste(utils::capture.output(dput(expected)), collapse = ""), "\n", sep = "")
    cat("          actual:   ",
        paste(utils::capture.output(dput(actual)), collapse = ""), "\n", sep = "")
  }
  invisible(NULL)
}

as_json <- function(x) as.character(jsonlite::toJSON(x, auto_unbox = TRUE, null = "null"))


cat("\n-- case conversion between R and the API --\n")
ok("snake_case(hashId)", snake_case("hashId"), "hash_id")
ok("snake_case(isMrioAllowed)", snake_case("isMrioAllowed"), "is_mrio_allowed")
ok("snake_case(m49Code)", snake_case("m49Code"), "m49_code")
ok("camel_case(hash_ids)", camel_case("hash_ids"), "hashIds")
ok("camel_case(dollar_year)", camel_case("dollar_year"), "dollarYear")
ok("round trip", camel_case(snake_case("spendingPatternCommodities")), "spendingPatternCommodities")


cat("\n-- a Group sends exactly one region identifier --\n")
group <- new_group(
  title = "T", hash_id = "abc", dollar_year = 2026, dataset_id = 124,
  group_events = list(group_event("e1"), group_event("e2", scaling_factor = 0.01))
)
body <- to_api(group)
ok("urid omitted when NULL", "urid" %in% names(body), FALSE)
ok("user_model_id omitted when NULL", "userModelId" %in% names(body), FALSE)
ok("both group events kept", length(body$groupEvents), 2L)


cat("\n-- one group event still serializes as an array --\n")
one <- to_api(new_group(
  title = "T", hash_id = "a", dollar_year = 2026,
  group_events = list(group_event("only"))
))
ok("groupEvents renders as [ ]", grepl('"groupEvents":\\[\\{', as_json(one)), TRUE)


cat("\n-- one tag must not unbox to a bare string --\n")
tagged <- industry_output_event(title = "E", industry_code = 1, output = 1000, tags = "spending")
ok("tags renders as [ ]", grepl('"tags":\\["spending"\\]', as_json(to_api(tagged))), TRUE)


cat("\n-- the growth report keeps all five arrays, even empty --\n")
growth <- as_json(to_api(impact_results_export_request(dollar_year = 2026)))
for (field in c("regions", "impacts", "groupNames", "eventNames", "eventTags")) {
  ok(paste0(field, " present and empty"), grepl(paste0('"', field, '":\\[\\]'), growth), TRUE)
}


cat("\n-- a response may carry fields this sample has never heard of --\n")
known_type <- event_from_api(list(
  impactEventType = "IndustryOutput", title = "New", id = "x1",
  industryCode = 1, output = 5, brandNewField = 42
))
ok("declared field read", known_type$industry_code, 1)
ok("undeclared field kept", known_type$brandNewField, 42)

unknown_type <- event_from_api(list(
  impactEventType = "SomethingNew", title = "U", id = "x2", weird = TRUE
))
ok("unmodeled event type preserved", unknown_type$impact_event_type, "SomethingNew")
ok("its fields kept too", unknown_type$weird, TRUE)

region <- region_from_api(list(
  hashId = "h", description = "Oregon", modelBuildStatus = "Complete",
  isMrioAllowed = TRUE, fipsCode = "41000", somethingAddedLater = 1
))
ok("region is_built", is_built(region), TRUE)
ok("region is_user_defined", is_user_defined(region), FALSE)
ok("region keeps the unknown field", region$somethingAddedLater, 1)


cat("\n-- combining regions --\n")
combine <- to_api(combine_region_request("desc", hash_ids = c("a", "b")))
ok("hashIds is an array", grepl('"hashIds":\\["a","b"\\]', as_json(combine)), TRUE)
ok("urids omitted when not supplied", "urids" %in% names(combine), FALSE)


cat("\n-- result filters --\n")
query <- filters_to_query(result_filters(year = 2026, regions = c("Oregon", "Wisconsin")))
ok("year kept", query$year, 2026)
ok("both regions kept", length(query$regions), 2L)
ok("empty dimensions dropped", "impacts" %in% names(query), FALSE)
ok("no filters gives an empty query", length(filters_to_query(result_filters())), 0L)


cat("\n-- a folder's id is a string, a project's folderId is a number --\n")
ok("folder_id_for_project converts",
   folder_id_for_project(folder_from_api(list(title = "F", id = "1234"))), 1234L)


cat("\n-- small helpers --\n")
ok("safe_file_name replaces every reserved character",
   safe_file_name("a/b:c*d?"), "a_b_c_d_")
ok("csv_data_row_count ignores the header", csv_data_row_count("h1,h2\r\na,b\r\nc,d\r\n"), 2L)
ok("bare_token strips the prefix", bare_token("Bearer abc.def"), "abc.def")
ok("unique_title carries the prefix",
   startsWith(unique_title("X"), paste(TITLE_PREFIX, "- X -")), TRUE)


cat("\n-- the command line --\n")
exports <- parse_arguments(c("regional-exports", "--region-type", "County", "--limit", "0"))
ok("workflow name", exports$workflow, "regional-exports")
ok("region type", exports$region_type, "County")
ok("--limit 0 means all", is.null(exports$limit), TRUE)

impact <- parse_arguments(c("run-impact-analysis", "--project-id", "abc-123"))
ok("project id", impact$project_id, "abc-123")
ok("map code defaults to US", impact$map_code, "US")


cat("\n-- an API error carries its status and problem details --\n")
problem <- structure(
  list(status = 409L, title = "Conflict", detail = "That title is taken.", trace_id = "t-1"),
  class = "implan_problem"
)
ok("status reachable on the condition",
   implan_api_error("POST", "/x", problem)$status, 409L)
ok("traceId reaches the message",
   grepl("t-1", conditionMessage(implan_api_error("POST", "/x", problem))), TRUE)


cat("\n-- requests are built correctly, without sending anything --\n")
client <- api_client(token_provider = function() "Bearer not.a.real.token")

filtered <- build_request(
  client, "/api/v1/impact/results/SummaryEconomicIndicators/1", "GET",
  query = list(year = 2026, regions = c("Oregon", "Wisconsin"))
)
ok("a repeated filter becomes repeated parameters",
   grepl("regions=Oregon&regions=Wisconsin", httr2::req_get_url(filtered)), TRUE)
ok("the token is redacted when the request is inspected",
   httr2::req_get_headers(filtered, redacted = "redact")$Authorization, "<REDACTED>")

with_body <- build_request(
  client, "/api/v1/impact/results/EstimatedGrowthPercentage/1", "GET",
  body = to_api(impact_results_export_request(2026))
)
ok("a GET carrying a body stays a GET", httr2::req_get_method(with_body), "GET")
ok("and the body is JSON", httr2::req_get_body_type(with_body), "json")


cat("\n")
if (FAILURES == 0L) {
  cat("All checks passed.\n")
  quit(status = 0, save = "no")
}

cat(FAILURES, "check(s) failed.\n")
quit(status = 1, save = "no")
