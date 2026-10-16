# The HTTP layer: how requests are built, what is logged, and how failures arrive.
#
# httr2's mocking answers a request before httr2's own retry loop and before it
# wraps a curl error, so retries cannot be exercised here. A refused connection is
# scripted as the `httr2_failure` condition httr2 raises when nothing answers.

test_that("a repeated filter becomes repeated query parameters", {
  req <- build_request(
    test_client(), "/api/v1/impact/results/SummaryEconomicIndicators/1", "GET",
    query = list(year = 2026, regions = c("Oregon", "Wisconsin"))
  )

  expect_match(httr2::req_get_url(req), "regions=Oregon&regions=Wisconsin", fixed = TRUE)
})

test_that("a GET carrying a body stays a GET, and the body is JSON", {
  req <- build_request(
    test_client(), "/api/v1/impact/results/EstimatedGrowthPercentage/1", "GET",
    body = to_api(impact_results_export_request(2026))
  )

  expect_equal(httr2::req_get_method(req), "GET")
  expect_equal(httr2::req_get_body_type(req), "json")
})

test_that("the token is redacted in the request and in the log", {
  req <- build_request(test_client(), "/api/v1/region/RegionTypes")
  expect_equal(httr2::req_get_headers(req, redacted = "redact")$Authorization, "<REDACTED>")

  httr2::local_mocked_responses(list(mock_response(200, "[]")))
  get_json(test_client(), "/api/v1/region/RegionTypes")

  log <- paste(readLines(log_file_path(), warn = FALSE), collapse = "\n")
  expect_match(log, "RegionTypes", fixed = TRUE)
  expect_match(log, "Authorization: <redacted>", fixed = TRUE)
  expect_no_match(log, "not.a.real.token", fixed = TRUE)
})

test_that("an error response arrives as implan_api_error with its problem details", {
  problem <- '{"title":"Project not found","detail":"No Project was found.","traceId":"00-abc-01"}'
  httr2::local_mocked_responses(list(mock_response(404, problem, "application/problem+json")))

  error <- expect_error(get_json(test_client(), "/api/v1/impact/project/x"), class = "implan_api_error")

  expect_equal(error$status, 404L)
  expect_equal(error$problem$title, "Project not found")
  expect_equal(error$problem$trace_id, "00-abc-01")
})

test_that("every way of sending raises an API error rather than returning NULL", {
  for (send in list(
    function(client) get_json(client, "/x"),
    function(client) post_json(client, "/x"),
    function(client) put_json(client, "/x")
  )) {
    httr2::local_mocked_responses(list(mock_response(409, '{"title":"Model not built"}')))
    expect_error(send(test_client()), class = "implan_api_error")
  }
})

test_that("a 401 refreshes the token once, then retries", {
  refreshes <- 0
  client <- test_client(token_refresher = function() {
    refreshes <<- refreshes + 1
    FAKE_TOKEN
  })
  httr2::local_mocked_responses(list(mock_response(401), mock_response(200, '{"ok":true}')))

  expect_equal(get_json(client, "/x"), list(ok = TRUE))
  expect_equal(refreshes, 1)
})

test_that("a second 401 is raised without refreshing again", {
  refreshes <- 0
  client <- test_client(token_refresher = function() {
    refreshes <<- refreshes + 1
    FAKE_TOKEN
  })
  httr2::local_mocked_responses(list(mock_response(401), mock_response(401)))

  error <- expect_error(get_json(client, "/x"), class = "implan_api_error")

  expect_equal(error$status, 401L)
  expect_equal(refreshes, 1)
})

test_that("a request that reaches nothing is a transport error, not an API error", {
  httr2::local_mocked_responses(function(req) {
    stop(errorCondition("Could not connect to server", class = "httr2_failure"))
  })

  error <- expect_error(get_json(test_client(), "/x"), class = "implan_transport_error")

  expect_false(inherits(error, "implan_api_error"))
})
