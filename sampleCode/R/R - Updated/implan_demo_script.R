# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE. 

source("new_implan_api_helper.R")
library(httr2)
library(glue)
library(uuid)

options(warn = 1)
options(width = 300) # Set the maximum width of the output
options(max.print = 10000) # Set the maximum number of lines to print

# Authenticate with IMPLAN

# Trigger initial authentication so the token is cached.
# Helper functions call getImplanAuth() internally on each
# request, so no need to store the return value.
getImplanAuth()

# Read Model Definition Files

# Validate that required input files exist before proceeding
required_files <- c("state_based.csv", "county_based.csv", "demo_events.csv")
missing <- required_files[!file.exists(required_files)]
if (length(missing) > 0) {
  stop(glue("Missing required input file(s): {paste(missing, collapse = ', ')}"))
}

# Read state-level model definitions
# colClasses ensures FIPS codes keep leading zeros
state_data <- read.csv("state_based.csv",
                       colClasses = c("character", "character"))

# Read county-level model definitions
county_data <- read.csv("county_based.csv",
                        colClasses = c("character", "character"))

# Build or Retrieve Regional Models

buildModels <- function(mapping_df) {

  results <- list()
  unique_model_names <- unique(mapping_df$model_name)

  for (model_name in unique_model_names) {

    # Make model name dataset-specific
    dataset_model_name <- glue("{model_name}_{aggregation_scheme_id}_{data_set_id}")

    # Check if model already exists
    model_exists <- doesUserModelExist(dataset_model_name)

    if (!model_exists) {

      # Extract all FIPS codes for this model
      fips_codes <- mapping_df[mapping_df$model_name == model_name, "fips"]

      # Convert FIPS codes to URIDs
      urids <- list()
      for (fips in fips_codes) {
        urids <- c(urids, getRegionCardByFipsCode(fips)["urid"])
      }

      # Build the combined region model
      buildCombinedRegion(dataset_model_name, urids)

      # Wait until model build is complete
      if (!waitForModelToBuild(dataset_model_name)) {
        stop(glue("Model build failed for: {dataset_model_name}"))
      }
    }

    # Retrieve final model region card
    regionCard <- getUserModel(dataset_model_name)

    # Accumulate region cards via local return (no <<- needed)
    results <- c(results, list(regionCard))
  }

  return(results)
}

# Build state and county models, combine into one list
models_for_projects <- c(buildModels(state_data),
                         buildModels(county_data))

# Read Event Data

events_csv <- read.csv("demo_events.csv",
                       colClasses = c("character", "character"))

industry_output_events <-
  events_csv[events_csv$Type == "Industry Output", ]

commodity_output_events <-
  events_csv[events_csv$Type == "Commodity Output", ]

# Add all events to a project

addAllEventsToProject <- function(project, industry_df, commodity_df) {

  events <- list()

  for (i in seq_len(nrow(industry_df))) {
    row <- industry_df[i, ]
    evt <- addIndustryOutputEvent(project, row$Name, row$Code, row$Value)
    events <- c(events, list(evt))
  }

  for (i in seq_len(nrow(commodity_df))) {
    row <- commodity_df[i, ]
    evt <- addCommodityOutput(project, row$Name, row$Code, row$Value)
    events <- c(events, list(evt))
  }

  return(events)
}

# Save all result types for a completed run

saveAllResults <- function(project, runId) {
  getSummaryEconomicIndicators(project, runId)
  getSummaryTaxes(project, runId)
  getDetailedTaxes(project, runId)
  getDetailEconomicIndicators(project, runId)
}

# Ensure Folder Exists in IMPLAN

if (!doesFolderExist(folder_name)) {
  createFolder(folder_name)
}

folder <- getFolder(folder_name)

# Create & Run Individual Model Projects

for (regionCard in models_for_projects) {

  model_name <- regionCard$description
  uniqueId <- UUIDgenerate()

  project_name <- glue("{model_name}-{uniqueId}")

  # Create new project inside selected folder
  project <- createProject(project_name,
                           folder$id[[1]])

  # Add all events (industry + commodity)
  events_for_project <- addAllEventsToProject(
    project, industry_output_events, commodity_output_events
  )

  # Create Group Linked to Regional Model
  addGroup(project,
           regionCard$description,
           regionCard,
           group_dollar_year,
           events_for_project)

  # Run the Project
  runId <- runProject(project)
  waitForProjectRunToComplete(runId)

  # Save results
  saveAllResults(project, runId)
}

# Create Combined "All Models" Project

uniqueId <- UUIDgenerate()
project_name <- glue("All Models Project {uniqueId}")

project <- createProject(project_name,
                         folder$id[[1]])

# Add all events once
events_for_project <- addAllEventsToProject(
  project, industry_output_events, commodity_output_events
)

# Create a Group for Each Regional Model
for (regionCard in models_for_projects) {

  addGroup(project,
           regionCard$description,
           regionCard,
           group_dollar_year,
           events_for_project)
}

# Run Combined Project
runId <- runProject(project)
waitForProjectRunToComplete(runId)

# Save results
saveAllResults(project, runId)

# Display Any Warnings
warnings()
