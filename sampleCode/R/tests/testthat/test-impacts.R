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

test_that("a run that ends in error raises an implan_run_error", {
  httr2::local_mocked_responses(list(mock_response(200, "Error", "text/plain")))

  expect_error(
    utils::capture.output(wait_for_impact(test_client(), 1L, poll_seconds = 0)),
    class = "implan_run_error"
  )
})

test_that("a run that outlasts the timeout raises an implan_run_timeout", {
  httr2::local_mocked_responses(list(mock_response(200, "InProgress", "text/plain")))

  expect_error(
    utils::capture.output(wait_for_impact(test_client(), 1L, timeout_seconds = 0, poll_seconds = 0)),
    class = "implan_run_timeout"
  )
})

# A Summary Economic Indicators report as the API writes it: spaces after the
# header's commas, a Group name that needs quotes, and a closing "Totals" row.
test_that("effect totals split direct from the rest and skip the Totals row", {
  report <- paste0(
    "GroupName, EventName, ModelName, Impact, Employment, LaborIncome, ValueAdded, Output, TagName\r\n",
    "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),1 - Direct,10.5,100,200,1000,\r\n",
    "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),2 - Indirect,1.25,10,20,300,\r\n",
    "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),3 - Induced,0.25,5,10,200,\r\n",
    "Totals,,,,12,115,230,1500,\r\n"
  )

  expect_equal(
    effect_totals(report),
    list(direct_output = 1000, indirect_and_induced_output = 500, employment = 12)
  )
})

test_that("a report without an Impact column says so", {
  expect_error(
    effect_totals("GroupName,Output,Employment\r\nOregon (2024),1000,10\r\n"),
    "no Impact column"
  )
})
