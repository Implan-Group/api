# The request and response models: what they send, and what they tolerate.

test_that("names convert between R and the API", {
  expect_equal(snake_case("hashId"), "hash_id")
  expect_equal(snake_case("isMrioAllowed"), "is_mrio_allowed")
  expect_equal(snake_case("m49Code"), "m49_code")
  expect_equal(camel_case("hash_ids"), "hashIds")
  expect_equal(camel_case("dollar_year"), "dollarYear")
  expect_equal(camel_case(snake_case("spendingPatternCommodities")), "spendingPatternCommodities")
})

test_that("a group sends only the region identifier it has", {
  body <- to_api(new_group(
    title = "T", hash_id = "abc", dollar_year = 2026, dataset_id = 124,
    group_events = list(group_event("e1"), group_event("e2", scaling_factor = 0.01))
  ))

  expect_equal(body$hashId, "abc")
  expect_false("urid" %in% names(body))
  expect_false("userModelId" %in% names(body))
  expect_length(body$groupEvents, 2)
})

test_that("one group event is still an array", {
  body <- to_api(new_group(
    title = "T", hash_id = "a", dollar_year = 2026,
    group_events = list(group_event("only"))
  ))

  expect_match(as_json(body), '"groupEvents":[{', fixed = TRUE)
})

test_that("one tag is still an array, not a bare string", {
  event <- industry_output_event(title = "E", industry_code = 1, output = 1000, tags = "spending")

  expect_match(as_json(to_api(event)), '"tags":["spending"]', fixed = TRUE)
})

test_that("the growth report keeps all five arrays, even empty", {
  json <- as_json(to_api(impact_results_export_request(dollar_year = 2026)))

  for (field in c("regions", "impacts", "groupNames", "eventNames", "eventTags")) {
    expect_match(json, paste0('"', field, '":[]'), fixed = TRUE)
  }
})

test_that("an event keeps fields this sample has never heard of", {
  known <- event_from_api(list(
    impactEventType = "IndustryOutput", title = "New", id = "x1",
    industryCode = 1, output = 5, brandNewField = 42
  ))
  expect_equal(known$industry_code, 1)
  expect_equal(known$brandNewField, 42)

  unknown <- event_from_api(list(
    impactEventType = "SomethingNew", title = "U", id = "x2", weird = TRUE
  ))
  expect_equal(unknown$impact_event_type, "SomethingNew")
  expect_true(unknown$weird)
})

test_that("a region reads its build status and keeps unknown fields", {
  region <- region_from_api(list(
    hashId = "h", description = "Oregon", modelBuildStatus = "Complete",
    isMrioAllowed = TRUE, fipsCode = "41000", somethingAddedLater = 1
  ))

  expect_true(is_built(region))
  expect_false(is_user_defined(region))
  expect_equal(region$somethingAddedLater, 1)
})

test_that("a user-defined region says it is yours", {
  region <- region_from_api(list(hashId = "h", description = "Two counties", userModelId = 42))

  expect_true(is_user_defined(region))
  expect_match(describe(region), "yours, userModelId=42", fixed = TRUE)
})

test_that("combining regions sends hashIds as an array", {
  body <- to_api(combine_region_request("desc", hash_ids = c("a", "b")))

  expect_match(as_json(body), '"hashIds":["a","b"]', fixed = TRUE)
  expect_false("urids" %in% names(body))
})

test_that("result filters drop the empty dimensions", {
  query <- filters_to_query(result_filters(year = 2026, regions = c("Oregon (2024)", "Wisconsin (2024)")))

  expect_equal(query$year, 2026)
  expect_length(query$regions, 2)
  expect_false("impacts" %in% names(query))
  expect_length(filters_to_query(result_filters()), 0)
})

test_that("a folder's string id becomes a project's numeric folderId", {
  folder <- folder_from_api(list(title = "F", id = "1234"))

  expect_identical(folder_id_for_project(folder), 1234L)
})
