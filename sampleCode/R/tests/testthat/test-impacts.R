# Starting an impact run and reading its status, both of which answer in plain text.

test_that("the status reads with or without quotes", {
  httr2::local_mocked_responses(list(
    mock_response(200, "Complete", "text/plain"),
    mock_response(200, '"Complete"')
  ))

  expect_equal(get_impact_status(test_client(), 1L), "Complete")
  expect_equal(get_impact_status(test_client(), 1L), "Complete")
})

test_that("an unknown status is reported, not guessed", {
  httr2::local_mocked_responses(list(mock_response(200, "SomethingNew", "text/plain")))

  expect_equal(get_impact_status(test_client(), 1L), IMPACT_STATUSES[["UNKNOWN"]])
})

test_that("a run id is a bare number", {
  httr2::local_mocked_responses(list(mock_response(200, "30542")))

  expect_identical(run_impact(test_client(), "project"), 30542L)
})
