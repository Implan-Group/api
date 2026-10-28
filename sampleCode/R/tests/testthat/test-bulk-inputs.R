# BulkFromCsv's input files: read strictly, and checked before anything is created.

# Reads `text` as an input file with the workflow's own reader.
read_text <- function(text) {
  path <- withr::local_tempfile(fileext = ".csv")
  writeLines(text, path)
  read_input_csv(path, BULK_REGION_COLUMNS)
}

regions_of <- function(fips, model_name) {
  data.frame(
    fips = fips, region_description = rep("", length(fips)), model_name = model_name,
    line = as.character(seq_along(fips) + 1L), stringsAsFactors = FALSE
  )
}

events_of <- function(name, code = "1", type = "Industry Output", value = "1000") {
  data.frame(
    Name = name, Code = rep_len(code, length(name)), Type = rep_len(type, length(name)),
    Value = rep_len(value, length(name)),
    line = as.character(seq_along(name) + 1L), stringsAsFactors = FALSE
  )
}

test_that("an unquoted comma is reported with its line", {
  expect_error(
    read_text(c("fips,region_description,model_name", "41019,Douglas County, OR,MyModel")),
    "line 2 .*double quotes"
  )
})

test_that("a quoted comma is one value", {
  rows <- read_text(c("fips,region_description,model_name", '41019,"Douglas County, OR",MyModel'))

  expect_equal(rows$model_name, "MyModel")
})

test_that("a semicolon file is reported as not comma-separated", {
  expect_error(
    read_text(c("fips;region_description;model_name", "41019;Douglas;MyModel")),
    "comma-separated"
  )
})

test_that("rows of bare commas are skipped", {
  rows <- read_text(c("fips,region_description,model_name", "41019,Douglas,MyModel", ",,", ",,"))

  expect_equal(nrow(rows), 1L)
})

test_that("good rows pass and come back normalized", {
  checked <- check_inputs(
    regions_of(c("1000", "1"), c("South", "South")),
    regions_of(character(0), character(0)),
    events_of("Output", value = "$1,000,000")
  )

  expect_equal(checked$state_rows$fips, c("01000", "01"))
  expect_equal(checked$event_rows$Value, "1000000")
})

test_that("every problem is reported at once", {
  error <- expect_error(check_inputs(
    regions_of("ABC", "Lane & Douglas"),
    regions_of("41019", "Lane & Douglas"),
    events_of(c("Food", "Food"), code = c("1", "x"), type = c("Household Income", "Industry Output"),
              value = c("1000", "lots"))
  ))

  for (expected in c(
    "'ABC' is not a state or county FIPS code",
    "contains &",
    "is in both state_based.csv and county_based.csv",
    "is not Industry Output or Commodity Output",
    "'Food' is already used",
    "Code 'x' is not a whole number",
    "Value 'lots' is not an amount"
  )) {
    expect_match(conditionMessage(error), expected, fixed = TRUE)
  }
})

test_that("at least one region and one event are needed", {
  error <- expect_error(check_inputs(
    regions_of(character(0), character(0)),
    regions_of(character(0), character(0)),
    events_of(character(0))
  ))

  expect_match(conditionMessage(error), "both empty", fixed = TRUE)
  expect_match(conditionMessage(error), "demo_events.csv is empty", fixed = TRUE)
})
