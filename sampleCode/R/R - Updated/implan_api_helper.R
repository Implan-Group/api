# This file contains all the functions needed to interact with
# the IMPLAN API. 
#
# BEFORE USING THIS FILE:
#   1. Create a folder called "private" in your working directory
#   2. Inside it, create a file called "creds.json" with this format:
#      {
#        "username": "your@email.com",
#        "password": "yourpassword"
#      }

library(httr) #library for making HTTP calls
library(jsonlite) #library for JSON
library(glue) #library for string interpolation 
library(uuid) # library for creating uuids

# Configuration 
# These values control which IMPLAN dataset and scheme are used throughout.

aggregation_scheme_id = 14 # aggregation scheme 8 is 546 
data_set_id = 98 # DatasetId 
group_dollar_year <- 2021 #dollar year for groups
folder_name <- "r_demo_folder_11" #folder name to save to on Implan

# The root URL for all IMPLAN API calls
base_url_implan <- "https://api.implan.com" #base url for API calls

# The API path prefix prepended to every endpoint
implan_env_path <- "/api" #environment #Prod:/api 

# Directory Setup 
# These folders are used to store credentials, cached API responses, and results.

private_dir <- "private"   # Where credentials (creds.json) are stored
cache_dir   <- "cache"     # Where token and region data are cached to avoid repeat API calls
results_dir <- "results"   # Where exported CSV result files are saved

# Create the cache and results directories if they don't already exist.
if (!dir.exists(cache_dir))   dir.create(cache_dir)   # Creates ./cache/
if (!dir.exists(results_dir)) dir.create(results_dir) # Creates ./results/

# File Path Helpers

# Returns the full path to a file inside the cache directory
getCacheFile   <- function(fileName) glue("{cache_dir}/{fileName}")

# Returns the full path to a file inside the private (credentials) directory
getPrivateFile <- function(fileName) glue("{private_dir}/{fileName}")

# Returns the full path to a file inside the results directory
getResultsFile <- function(fileName) glue("{results_dir}/{fileName}")

# AUTHENTICATION

# IMPLAN uses JWT bearer tokens for authentication.
# A token is valid for ~480 minutes (8 hours). This function:
#   - Checks if a valid cached token already exists
#   - If the token is still fresh (< 475 min old), reuses it
#   - If expired or missing, logs in with credentials and saves a new token

getImplanAuth <- function() {

  # Path to the file where the token is cached between sessions
  savedTokenFile <- getCacheFile("saved_token.json")

  # Assume we need to refresh until proven otherwise
  refresh <- TRUE

  # If a cached token file exists, check how old it is
  if (file.exists(savedTokenFile)) {

    # Read the cached token data (contains the token and the time it was saved)
    json_data <- fromJSON(savedTokenFile)

    # If the saved data includes a timestamp, calculate how many minutes have passed
    if (!is.null(json_data$date)) {
      age_minutes <- as.numeric(difftime(Sys.time(),
                                         as.POSIXct(json_data$date),
                                         units = "mins"))

      # If the token is less than 475 minutes old, it's still valid
      refresh <- age_minutes > 475
    }
  }

  # If we need a fresh token, log in using the stored credentials
  if (refresh) {

    # Read credentials from the private/creds.json file
    credsPath <- getPrivateFile("creds.json")
    if (!file.exists(credsPath)) {
      stop(
        "Credentials file not found at: ", credsPath, "\n",
        "Create a file at that path with this content:\n",
        "  { \"username\": \"your@email.com\", \"password\": \"yourpassword\" }"
      )
    }

    credsJson <- fromJSON(credsPath)  # Load the credentials as an R list

    # Validate that both fields are present and non-empty
    if (!nzchar(credsJson$username) || !nzchar(credsJson$password)) {
      stop("creds.json must contain non-empty 'username' and 'password' fields.")
    }

    # Build the JSON request body with the credentials
    body_json <- toJSON(
      list(username = credsJson$username,
           password = credsJson$password),
      auto_unbox = TRUE  # Prevents single values from being wrapped in JSON arrays
    )

    # Send the login POST request to the IMPLAN authentication endpoint
    response <- POST(
      glue("{base_url_implan}/auth"),           # Authentication endpoint URL
      body = body_json,                          # Credentials as JSON
      add_headers("Content-Type" = "application/json")  # Tell the API we're sending JSON
    )

    # If the login request failed (wrong credentials, server error, etc.), stop immediately
    if (http_error(response)) {
      stop(
        "Authentication failed. HTTP status: ", status_code(response), "\n",
        "Check that your username and password in private/creds.json are correct."
      )
    }

    # Extract the token text from the response body
    implan_token <- content(response, "text", encoding = "UTF-8")

    # Save the token and the current timestamp to the cache file for future reuse
    writeLines(
      toJSON(list(date  = Sys.time(),   # Record when the token was saved
                  token = implan_token), # The token itself
             auto_unbox = TRUE),
      savedTokenFile
    )

    message("Authentication successful. Token cached at: ", savedTokenFile)
  }

  # Return the token string from the cache file (whether freshly fetched or reused)
  fromJSON(savedTokenFile)$token
}

# REGION LOOKUP & COMBINED MODEL MANAGEMENT

buildCombinedRegion <- function(model_name, urids) {

  # Validate inputs before making the API call
  if (!nzchar(model_name)) stop("model_name must not be empty.")
  if (length(urids) < 2)   stop("At least 2 URIDs are required to build a combined region.")

  # Build the URL for the combined region build endpoint
  url <- glue("{base_url_implan}{implan_env_path}/v1/region/build/combined/{aggregation_scheme_id}")

  # Build the JSON request body with the model name and list of URIDs to combine
  json_data <- toJSON(
    list(description = model_name, urids = urids),
    auto_unbox = TRUE,  # Single values won't be wrapped in arrays
    pretty = TRUE       # Makes the JSON human-readable (useful for debugging)
  )

  # Send the POST request to create the combined region
  response <- POST(
    url,
    body = json_data,
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())  # Include the bearer token
  )

  # If the request failed, stop with a clear message
  if (http_error(response)) {
    stop(
      "Failed to build combined region '", model_name, "'. ",
      "HTTP status: ", status_code(response), "\n",
      "Check that all URIDs are valid for aggregation scheme ", aggregation_scheme_id, "."
    )
  }

  message("Combined region build submitted: ", model_name)

  # Return the hash ID of the new combined region (first element of the response)
  fromJSON(content(response, "text"))[[1]]
}


getRegionCardByFipsCode <- function(fips_code) {

  # Validate that a FIPS code was actually provided
  if (!nzchar(fips_code)) stop("fips_code must not be empty.")

  # Determine whether this FIPS code refers to a state or a county.
  isState <- nchar(fips_code) == 2 ||
    (nchar(fips_code) >= 3 &&
       substr(fips_code, nchar(fips_code) - 2, nchar(fips_code)) == "000")

  # Extract just the 2-digit state FIPS — needed for both state and county lookups
  state_fips <- substr(fips_code, 1, 2)

  # Build a safe filename prefix from the API path (replacing / with _)
  file_prefix <- gsub("/", "_", implan_env_path)

  # State-Level Cache
  # If the file exists, we read it instead of calling the API again.
  state_cache <- getCacheFile(
    glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_states.json")
  )

  if (!file.exists(state_cache)) {

    # Cache doesn't exist, fetch all state-level child regions from the API
    url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/children")

    response <- GET(url, add_headers("Authorization" = getImplanAuth()))

    if (http_error(response)) {
      stop("Failed to retrieve state region cards. HTTP status: ", status_code(response))
    }

    # Parse the response and write it to the cache file for future use
    json_content <- fromJSON(content(response, "text", encoding = "UTF-8"))
    writeLines(toJSON(json_content, pretty = TRUE), state_cache)

    message("State region data cached at: ", state_cache)
  }

  # Load the state data from the cache and find the row matching our state FIPS
  state_data  <- fromJSON(state_cache)
  region_card <- state_data[state_data$fipsCode == state_fips, ]

  # If no matching state was found, the FIPS code is likely invalid
  if (nrow(region_card) == 0) {
    stop("No state found for FIPS code '", state_fips, "'. ",
         "Check that the FIPS code is valid and matches the current dataset.")
  }

  # If the input was a state FIPS, we're done — return the state region card
  if (isState) {
    return(region_card)
  }

  # ── County-Level Cache ─────────────────────────────────────────────────────
  # County data is cached per state (one file per state FIPS).
  # This avoids downloading all counties in the country at once.

  county_cache <- getCacheFile(
    glue("{file_prefix}_{state_fips}_{aggregation_scheme_id}_{data_set_id}_children.json")
  )

  if (!file.exists(county_cache)) {

    # Cache doesn't exist — fetch all counties within this state from the API
    url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/{region_card$urid}/children")

    response <- GET(url, add_headers("Authorization" = getImplanAuth()))

    if (http_error(response)) {
      stop("Failed to retrieve county data for state FIPS '", state_fips,
           "'. HTTP status: ", status_code(response))
    }

    # Parse and cache the county data
    json_content <- fromJSON(content(response, "text"))
    writeLines(toJSON(json_content, pretty = TRUE), county_cache)

    message("County region data for state FIPS ", state_fips, " cached at: ", county_cache)
  }

  # Load county data from cache
  child_data <- fromJSON(county_cache)

  # Remove any rows where the FIPS code is missing (some regions may lack FIPS codes)
  child_data <- child_data[!is.na(child_data$fipsCode), ]

  # Find and return the row matching our target county FIPS code
  county_card <- child_data[child_data$fipsCode == fips_code, ]

  if (nrow(county_card) == 0) {
    stop("No county found for FIPS code '", fips_code, "'. ",
         "Check that the FIPS code is valid and exists in dataset ", data_set_id, ".")
  }

  county_card
}


# Retrieves a user-created combined region model by name.
# Results are cached to avoid repeated API calls.

# model_name    : The name of the combined model to look up
# force_refresh : If TRUE, bypasses the cache and fetches fresh data from the API
getUserModel <- function(model_name, force_refresh = FALSE) {

  # Build the cache file path for user models
  file_prefix      <- gsub("/", "_", implan_env_path)
  user_model_cache <- getCacheFile(
    glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_user_models.json")
  )

  # Get fresh data from the API if cache is missing or a refresh was requested
  if (force_refresh || !file.exists(user_model_cache)) {

    url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/user")

    response <- GET(url, add_headers("Authorization" = getImplanAuth()))

    if (http_error(response)) {
      stop("Failed to retrieve user models. HTTP status: ", status_code(response))
    }

    # Parse and write the response to the cache
    json_content <- fromJSON(content(response, "text", encoding = "UTF-8"))
    writeLines(toJSON(json_content, pretty = TRUE), user_model_cache)
  }

  # Load the cached user model data
  user_data <- fromJSON(user_model_cache)

  # If there are no user models yet, the API returns something other than a data frame
  # Return NULL so the caller can handle this gracefully
  if (!is.data.frame(user_data)) {
    return(NULL)
  }

  # Find and return the row matching the requested model name
  user_data[user_data$description == model_name, ]
}


# Checks whether a named user model exists in IMPLAN.
# Tries the cache first, then refreshes from the API if not found.
#
# Returns TRUE if the model exists, FALSE if it does not.
doesUserModelExist <- function(model_name) {

  # Build the cache file path (same logic as getUserModel)
  file_prefix      <- gsub("/", "_", implan_env_path)
  user_model_cache <- getCacheFile(
    glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_user_models.json")
  )

  # If no cache exists at all, trigger a fresh fetch to populate it
  if (!file.exists(user_model_cache)) {
    getUserModel(model_name)
  }

  # Load the cached data
  user_data <- fromJSON(user_model_cache)

  # If the API returned no models (not a data frame), we know the model doesn't exist
  if (!is.data.frame(user_data)) {
    return(FALSE)
  }

  # Check if any row matches the model name
  region_card <- user_data[user_data$description == model_name, ]

  # If not found in the cache, do one forced refresh before giving up
  # (the model may have been created after the cache was last written)
  if (nrow(region_card) == 0) {
    region_card <- getUserModel(model_name, force_refresh = TRUE)
  }

  # Return TRUE if we found at least one matching row, FALSE otherwise
  return(!is.null(region_card) && nrow(region_card) > 0)
}


# Polls the IMPLAN API until a combined region model finishes building.
# Returns TRUE if the model built successfully, FALSE if it never completed.
waitForModelToBuild <- function(model_name) {

  # Before polling, confirm the model exists at all
  if (!doesUserModelExist(model_name)) {
    message("Model '", model_name, "' does not exist — cannot wait for it to build.")
    return(FALSE)
  }

  # Get current model status
  region_card    <- getUserModel(model_name, force_refresh = TRUE)
  build_complete <- !is.null(region_card) &&
                    nrow(region_card) > 0 &&
                    region_card$modelBuildStatus == "Complete"

  # If already complete, no need to poll
  if (build_complete) {
    message("Model '", model_name, "' is already built.")
    return(TRUE)
  }

  # Poll up to 30 times (30 sec intervals = up to 15 minutes)
  for (i in 1:30) {

    message("Model '", model_name, "' not yet built — checking again in 30 seconds ",
            "(attempt ", i, " of 30)")

    Sys.sleep(30)  # Wait 30 seconds before checking again

    # Force a fresh fetch from the API (bypass cache) to get the latest status
    region_card    <- getUserModel(model_name, force_refresh = TRUE)
    build_complete <- !is.null(region_card) &&
                      nrow(region_card) > 0 &&
                      region_card$modelBuildStatus == "Complete"

    if (build_complete) {
      message("Model '", model_name, "' build complete.")
      return(TRUE)  # Exit the loop early — no need to keep checking
    }
  }

  # If we reach here, the model never finished within the timeout
  message("WARNING: Model '", model_name, "' did not complete within the allotted time.")
  return(FALSE)
}

# FOLDER MANAGEMENT

createFolder <- function(folder_name) {

  # Validate input
  if (!nzchar(folder_name)) stop("folder_name must not be empty.")

  # Build the URL for the folder creation endpoint
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")

  # Send the POST request to create the folder
  response <- POST(
    url,
    body = toJSON(list(title = folder_name), auto_unbox = TRUE),  # Folder title as JSON
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Failed to create folder '", folder_name, "'. HTTP status: ", status_code(response))
  }

  message("Folder created: ", folder_name)

  # Retrieve and return the newly created folder so the caller has its ID and metadata
  getFolder(folder_name)
}


# Checks whether a folder with the given name already exists in IMPLAN.
# Returns TRUE if found, FALSE if not.
doesFolderExist <- function(folder_name) {

  # Build the URL to list all folders
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")

  response <- GET(url,
                  add_headers("Content-Type" = "application/json",
                              "Authorization" = getImplanAuth()))

  if (http_error(response)) {
    stop("Failed to retrieve folder list. HTTP status: ", status_code(response))
  }

  # Parse the list of all folders
  json_content <- fromJSON(content(response, "text"))

  # Check if any folder matches the requested name
  folder <- json_content[json_content$title == folder_name, ]

  return(nrow(folder) > 0)  # TRUE if found, FALSE if not
}


# Retrieves a folder by name and returns its metadata (including its ID).
# The folder ID is needed when creating projects inside it.
getFolder <- function(folder_name) {

  # Build the URL to list all folders
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")

  response <- GET(url, add_headers("Authorization" = getImplanAuth()))

  if (http_error(response)) {
    stop("Failed to retrieve folder list. HTTP status: ", status_code(response))
  }

  # Parse all folders and find the one matching the requested name
  json_content <- fromJSON(content(response, "text"))
  folder       <- json_content[json_content$title == folder_name, ]

  # Confirm the folder was found
  if (nrow(folder) == 0) {
    stop("Folder '", folder_name, "' not found. ",
         "Check that the folder was created before calling getFolder().")
  }

  folder
}

# PROJECT MANAGEMENT
# Creates a new IMPLAN project and returns its metadata.
#
# name           : The title of the new project
# folderId       : ID of the folder to place this project in (use getFolder()$id)
# isMrio         : Whether to use Multi-Regional Input-Output modeling (default FALSE)
# householdSetId : Which household classification set to use (default 1)

createProject <- function(name,
                          folderId       = NA,
                          isMrio         = FALSE,
                          householdSetId = 1) {

  # Validate inputs
  if (!nzchar(name)) stop("Project name must not be empty.")

  # Build the URL for the project creation endpoint
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project")

  # Build the project data payload
  project_data <- list(
    Id                  = UUIDgenerate(),       
    AggregationSchemeId = aggregation_scheme_id, 
    HouseholdSetId      = householdSetId,       
    Title               = name,                  
    FolderId            = folderId,              
    IsMrio              = isMrio                 
  )

  # Send the POST request to create the project
  response <- POST(
    url,
    body = toJSON(project_data, auto_unbox = TRUE, na = "null"),  # na="null" converts NA to JSON null
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Project creation failed for '", name, "'. HTTP status: ", status_code(response))
  }

  message("Project created: ", name)

  # Retrieve and return the full project object (includes its server-assigned ID)
  getProject(name)
}


# Retrieves an existing project by its title.
# Returns a data frame row with the project's metadata (including its ID).
getProject <- function(project_name) {

  # Build the URL to list all projects
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project")

  response <- GET(url, add_headers("Authorization" = getImplanAuth()))

  if (http_error(response)) {
    stop("Failed to retrieve project list. HTTP status: ", status_code(response))
  }

  # Parse all projects and find the one matching the requested name
  json_content <- fromJSON(content(response, "text"))
  project      <- json_content[json_content$title == project_name, ]

  # Confirm the project was found
  if (nrow(project) == 0) {
    stop("Project '", project_name, "' not found after creation. ",
         "This may indicate the create request did not complete successfully.")
  }

  project
}

# EVENTS & GROUPS

# Adds an Industry Output event to a project.
# Use this to model a specific dollar amount of output from a given industry.

# project       : The project object returned by createProject() or getProject()
# title         : A name to identify this event in results
# industry_code : The IMPLAN industry code (e.g. 1 for Oilseed Farming)
# output        : Dollar value of industry output to model

addIndustryOutputEvent <- function(project, title, industry_code, output) {

  # Validate inputs
  if (!nzchar(title)) stop("Event title must not be empty.")
  if (is.na(output) || output <= 0) stop("Output value must be a positive number.")

  # Extract the project ID from the project data frame
  project_id <- project$id[[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/event")

  # Build the event data payload
  event_data <- list(
    Id              = UUIDgenerate(),    # Unique ID for this event
    Title           = title,             
    IndustryCode    = industry_code,     
    Output          = output,
    ImpactEventType = "IndustryOutput"   # Tells the API what type of event this is
  )

  # Send the POST request to add the event
  response <- POST(
    url,
    body = toJSON(event_data, auto_unbox = TRUE, na = "null"),
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Failed to add Industry Output event '", title, "'. ",
         "HTTP status: ", status_code(response))
  }

  message("Industry Output event added: ", title)

  # Return the created event object (includes its server-assigned ID)
  fromJSON(content(response, "text"))
}


# Adds a Commodity Output event to a project.
addCommodityOutput <- function(project, title, commodity_code, output) {

  # Validate inputs
  if (!nzchar(title)) stop("Event title must not be empty.")
  if (is.na(output) || output <= 0) stop("Output value must be a positive number.")

  # Extract the project ID
  project_id <- project$id[[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/event")

  # Build the commodity event payload
  event_data <- list(
    Id              = UUIDgenerate(),     
    Title           = title,              
    CommodityCode   = commodity_code,     
    Output          = output,             
    ImpactEventType = "CommodityOutput"   
  )

  response <- POST(
    url,
    body = toJSON(event_data, auto_unbox = TRUE, na = "null"),
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Failed to add Commodity Output event '", title, "'. ",
         "HTTP status: ", status_code(response))
  }

  message("Commodity Output event added: ", title)

  # Return the created event object
  fromJSON(content(response, "text"))
}


# Creates a Group that links a set of events to a region and year within a project
addGroup <- function(project, title, region_card, dollar_year, events_for_group) {

  # Validate inputs
  if (!nzchar(title))           stop("Group title must not be empty.")
  if (length(events_for_group) == 0) stop("At least one event must be provided to create a group.")

  # Extract project ID and region hash ID
  project_id <- project$id[[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/group")

  # Build the list of event linkages for this group
  # Each event is referenced by its ID with a scaling factor of 1.0 (no scaling)
  group_events <- lapply(events_for_group, function(x) {
    list(EventId       = x$id[[1]],  # The event's unique ID
         scalingFactor = 1.0)         # 1.0 means use the event value as-is (no scaling)
  })

  # Extract the region's hash ID — this is the identifier the API uses for the region
  hash_id <- region_card$hashId[[1]]

  # Build the group payload
  group_data <- list(
    Id          = UUIDgenerate(),   
    Title       = title,            
    DatasetId   = data_set_id,      
    DollarYear  = dollar_year,      
    HashId      = hash_id,          
    GroupEvents = group_events      
  )

  response <- POST(
    url,
    body = toJSON(group_data, auto_unbox = TRUE, na = "null"),
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Failed to add group '", title, "'. HTTP status: ", status_code(response))
  }

  message("Group added: ", title)

  # Return the created group object
  fromJSON(content(response, "text"))
}

# RUNNING PROJECTS


# Submits a project for impact analysis and returns the run ID.
runProject <- function(project) {

  # Extract the project ID
  project_id <- project$id[[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/{project_id}")

  # Send the POST request to start the analysis run
  response <- POST(
    url,
    add_headers("Content-Type" = "application/json",
                "Authorization" = getImplanAuth())
  )

  if (http_error(response)) {
    stop("Failed to start impact run for project '", project$title[[1]], "'. ",
         "HTTP status: ", status_code(response), "\n",
         "Ensure the project has at least one group with events before running.")
  }

  # The response body is the integer run ID — convert it from text to an integer
  runId <- as.integer(content(response, "text"))

  message("Impact analysis started. Run ID: ", runId)

  runId
}


# Polls the IMPLAN API until the impact analysis run completes.
# Checks every 10 seconds, up to 90 times (~15 minutes total).
waitForProjectRunToComplete <- function(runId) {

  # Validate that a run ID was provided
  if (is.na(runId) || runId <= 0) stop("runId must be a positive integer.")

  # Build the URL for the status check endpoint
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/status/{runId}")

  # Poll up to 90 times (10 second intervals = up to 15 minutes)
  for (i in 1:90) {

    response <- GET(url, add_headers("Authorization" = getImplanAuth()))

    # Read the status text from the response
    status <- content(response, "text")

    # Check if the status contains "Complete" (case-sensitive, as returned by the API)
    if (grepl("Complete", status, fixed = TRUE)) {
      message("Run ", runId, " completed successfully.")
      return(TRUE)
    }

    # Check for known failure states so we don't wait the full 15 minutes unnecessarily
    if (grepl("Error|Failed|Cancelled", status, ignore.case = TRUE)) {
      stop("Impact run ", runId, " ended with a failure status: ", status, "\n",
           "Check your project configuration and try re-running.")
    }

    message("Run ", runId, " not yet complete — checking again in 10 seconds ",
            "(attempt ", i, " of 90)")

    Sys.sleep(10)  # Wait 10 seconds before checking again
  }

  # If we exit the loop without returning, the run timed out
  stop("Impact run ", runId, " timed out after ~15 minutes. ",
       "The run may still be processing on IMPLAN's servers. ",
       "Check your IMPLAN account or try increasing the poll limit.")
}

# RESULT RETRIEVAL
# Results are saved as CSV files in:
#   results/<ProjectTitle>-<RunId>/<filename>.csv
#
# Each result type has its own named function for clarity.

# Internal helper: Gets one result type from the API and saves it as a CSV.

saveResult <- function(project, runId, endpoint, filename) {

  # Build the output folder path using the project title and run ID
  projectTitle <- project$title[[1]]
  folder_path  <- getResultsFile(glue("{projectTitle}-{runId}"))

  # Create the output folder if it doesn't exist yet
  if (!dir.exists(folder_path)) {
    dir.create(folder_path)
    message("Results folder created: ", folder_path)
  }

  # Build the URL for this result type
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/results/{endpoint}/{runId}")

  response <- GET(url, add_headers("Authorization" = getImplanAuth()))

  if (http_error(response)) {
    stop("Failed to retrieve results for endpoint '", endpoint, "'. ",
         "HTTP status: ", status_code(response))
  }

  # Write the CSV content to the output file
  output_path <- glue("{folder_path}/{filename}")
  writeLines(content(response, "text", encoding = "UTF-8"), output_path)

  message("Results saved: ", output_path)
}

# ── Individual Result Functions ────────────────────────────────────────────────
# Each function retrieves one report type and saves it as a named CSV file.
# Call these after waitForProjectRunToComplete() confirms the run is done.

# Saves a high-level summary of economic impacts (output, employment, labor income, value added)
# broken into Direct, Indirect, and Induced effect types.
getSummaryEconomicIndicators <- function(project, runId)
  saveResult(project, runId, "SummaryEconomicIndicators", "summaryEconomicIndicators.csv")

# Saves a high-level summary of tax impacts across federal, state, and local levels.
getSummaryTaxes <- function(project, runId)
  saveResult(project, runId, "SummaryTaxes", "summaryTaxes.csv")

# Saves detailed tax impacts broken down by tax type and government level.
getDetailedTaxes <- function(project, runId)
  saveResult(project, runId, "DetailedTaxes", "detailedTaxes.csv")

# Saves detailed economic impacts broken down by individual industry.
getDetailEconomicIndicators <- function(project, runId)
  saveResult(project, runId, "ExportDetailEconomicIndicators", "detailEconomicIndicators.csv")
