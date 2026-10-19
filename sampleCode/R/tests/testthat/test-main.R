# The command line: what it accepts, and the exit code each kind of failure gets.


# Runs `code` with every workflow failing with `failure`, and returns its value.
#
# The samples are sourced rather than a package, so testthat's
# local_mocked_bindings() cannot reach run_workflow(); this swaps it in the global
# environment and puts it back afterwards.
with_failing_workflow <- function(failure, code) {
  original <- run_workflow
  assign("run_workflow", function(...) stop(failure), envir = globalenv())
  on.exit(assign("run_workflow", original, envir = globalenv()), add = TRUE)
  code
}

test_that("regional-exports options parse", {
  options <- parse_arguments(c("regional-exports", "--region-type", "County", "--limit", "0"))

  expect_equal(options$workflow, "regional-exports")
  expect_equal(options$region_type, "County")
  expect_null(options$limit)
})

test_that("an unknown region type is rejected", {
  expect_error(parse_arguments(c("regions", "--region-type", "Planet")), "Unknown region type")
})

test_that("a project id parses, and the map code defaults to US", {
  options <- parse_arguments(c("run-impact-analysis", "--project-id", "abc-123"))

  expect_equal(options$project_id, "abc-123")
  expect_equal(options$map_code, "US")
})

test_that("each kind of failure gets its own exit code", {
  problem <- structure(
    list(status = 404L, title = "Not Found", detail = "", trace_id = NULL),
    class = "implan_problem"
  )
  failures <- list(
    "2" = structure(
      class = c("implan_authentication_error", "error", "condition"),
      list(message = "refused", call = NULL)
    ),
    "3" = implan_api_error("GET", "/x", problem),
    "4" = simpleError("no workbook"),
    "5" = implan_transport_error("https://example.invalid", simpleError("refused"))
  )

  for (code in names(failures)) {
    failure <- failures[[code]]
    utils::capture.output(result <- with_failing_workflow(failure, main(c("identifiers"))))
    expect_identical(result, as.integer(code), label = paste("exit code for", class(failure)[1]))
  }
})

test_that("small helpers", {
  expect_equal(safe_file_name("a/b:c*d?"), "a_b_c_d_")
  expect_equal(csv_data_row_count("h1,h2\r\na,b\r\nc,d\r\n"), 2L)
  expect_equal(bare_token("Bearer abc.def"), "abc.def")
  expect_true(startsWith(unique_title("X"), paste(TITLE_PREFIX, "- X -")))
})
