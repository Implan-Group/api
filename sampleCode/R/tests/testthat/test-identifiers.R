# Resolving identifiers from an existing Project rather than from today's defaults.

# A Project on an older Industry Set: scheme 8 is not the current default.
OLDER_SCHEME <- paste0(
  '{"id":8,"description":"546 Unaggregated","industrySetId":8,',
  '"householdSetIds":[1],"mapCode":"US","status":"Complete"}'
)
INDUSTRY_SETS <- paste0(
  '[{"id":8,"description":"546 Industries","isDefault":false,"activeStatus":true,',
  '"defaultAggregationSchemeId":8},',
  '{"id":12,"description":"528 Industries","isDefault":true,"activeStatus":true,',
  '"defaultAggregationSchemeId":14}]'
)
SCHEME_DATASETS <- paste0(
  '[{"id":86,"description":"2021","isDefault":false},',
  '{"id":87,"description":"2022","isDefault":true}]'
)

# Answers each request with the next body, and records the URLs asked for.
scripted_bodies <- function(bodies, env = parent.frame()) {
  urls <- character(0)
  httr2::local_mocked_responses(function(req) {
    urls <<- c(urls, req$url)
    mock_response(200, bodies[[length(urls)]])
  }, env = env)
  function() urls
}

test_that("identifiers come from the project's own scheme", {
  requested <- scripted_bodies(list(OLDER_SCHEME, INDUSTRY_SETS, SCHEME_DATASETS))
  project <- new_project(title = "Older", aggregation_scheme_id = 8L, household_set_id = 3L)

  ids <- resolve_identifiers_for_project(test_client(), project)

  expect_equal(ids$aggregation_scheme_id, 8)
  expect_equal(ids$industry_set$id, 8)
  expect_equal(ids$dataset_id, 87)
  expect_equal(ids$household_set_id, 3)
  expect_equal(ids$map_code, MAP_CODES[["US"]])
  expect_match(requested()[[1]], "/api/v1/aggregationSchemes/8$")
  expect_match(requested()[[3]], "/api/v1/datasets/8$")
})

test_that("the map code comes from the scheme", {
  canadian <- sub('"mapCode":"US"', '"mapCode":"CAN"', sub('"id":8,', '"id":9,', OLDER_SCHEME))
  scripted_bodies(list(canadian, INDUSTRY_SETS, SCHEME_DATASETS))
  project <- new_project(title = "Canadian", aggregation_scheme_id = 9L, household_set_id = 1L)

  ids <- resolve_identifiers_for_project(test_client(), project)

  expect_equal(ids$map_code, MAP_CODES[["CANADA"]])
})
