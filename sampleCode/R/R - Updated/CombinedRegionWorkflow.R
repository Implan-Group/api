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

# This workflow demonstrates how to combine two or more counties into a
# single custom region, and then wait for IMPLAN to build the combined model.

#   - Complete AuthenticationWorkflow.R first

source(auth_env$AggregationSchemeEndpoints) 
source(auth_env$DataSetEndpoints)           
source(auth_env$Iworkflow)          


MAX_WAIT_SECONDS  <- 600L # Maximum seconds to wait before giving up (10 minutes)
POLL_INTERVAL_SEC <- 30L  # Seconds to wait between each status check

# Define the CombinedRegionWorkflow class
setClass("CombinedRegionWorkflow",
         contains = "Iworkflow",
         slots = list(
           dummy = "character"  
         ))

# Define what Examples() does for this workflow
setMethod("Examples", signature = "CombinedRegionWorkflow", function(object) {

  #Validate Configuration
  if (length(COUNTIES_TO_COMBINE) < 2) {
    stop("COUNTIES_TO_COMBINE must contain at least 2 county names. ",
         "Add more names to the configuration vector at the top of this file.")
  }

  message("Starting Combined Region Workflow for: ", paste(COUNTIES_TO_COMBINE, collapse = ", "))

  #Get County-Level Regions

  regionTypes_instance <- new("RegionEndpoints")  # Create the endpoint handler

  # Get all county-level regions 
  regions <- GetRegionChildren(regionTypes_instance,
                               AGGREGATION_SCHEME_ID,
                               DATA_SET_ID,
                               regionType = "County")

  message("County regions retrieved. Building lookup dictionary...")

  #Build a Region Lookup Dictionary 
  
  regions_list <- split(regions, seq(nrow(regions)))  # Split data frame into one-row-per-item list

  # Assign lowercase county names as the keys for easy case-insensitive lookup
  descriptionToRegionDict <- setNames(
    regions_list,
    tolower(regions$description)  
  )

  message("Region dictionary built with ", length(descriptionToRegionDict), " counties.")

  # Look Up HashIds for Target Counties
  lookup_hash <- function(dict, county_name) {
    key   <- tolower(county_name)           
    entry <- dict[[key]]                    

    # If nothing was found, the name might be misspelled or not in this dataset
    if (is.null(entry)) {
      stop(
        "County '", county_name, "' was not found in the region data.\n",
        "Check that the name matches exactly (including state abbreviation, e.g. 'Autauga County, AL').\n",
        "Print descriptionToRegionDict to see all available county names."
      )
    }

    entry$hashId  # Return just the hashId — this is what the API needs
  }

  # Apply the helper to every county in our target list
  hashIds <- lapply(COUNTIES_TO_COMBINE, function(name) lookup_hash(descriptionToRegionDict, name))

  message("HashIds retrieved for all target counties.")

  #Send the Combine Regions Request

  # Build a unique description using a timestamp to avoid duplicate region names
  combinedDescription <- paste0("Combined Region - ", format(Sys.time(), "%Y%m%d_%H%M%S"))

  combineRegionPayload_instance <- new("CombineRegionRequest",
                                       Description = combinedDescription, 
                                       HashIds = hashIds                  
  )

  # Send the request 
  combinedRegion <- CombineRegions(combineRegionPayload_instance,
                                   aggregationSchemeId = AGGREGATION_SCHEME_ID)

  # Parse the JSON response into an R list so we can access individual fields
  combinedRegion <- fromJSON(combinedRegion)

  message("Combined region request submitted.",
          " AggregationSchemeId: ", combinedRegion$aggregationSchemeId,
          " | DatasetId: ", combinedRegion$datasetId)

  #Poll Until the Combined Region Model is Built
  poll_start <- Sys.time()  # Record when polling started so we can enforce the timeout

  repeat {

    # Calculate how long we've been waiting
    elapsed <- as.numeric(difftime(Sys.time(), poll_start, units = "secs"))

    # If we've been waiting too long, stop and tell the user to check manually
    if (elapsed > MAX_WAIT_SECONDS) {
      stop(
        "Combined region build timed out after ", MAX_WAIT_SECONDS, " seconds.\n",
        "The region may still be building on IMPLAN's servers.\n",
        "Log in to your IMPLAN account to check the status of: ", combinedDescription
      )
    }

    # Get user's saved regions 
    userRegions <- GetUserRegions(regionTypes_instance,
                                  combinedRegion$aggregationSchemeId,  
                                  combinedRegion$datasetId)             

    # Find the row in userRegions that matches our newly created combined region
    region <- userRegions[userRegions$hashId == combinedRegion$hashId, ]

    # Check the model build status for our combined region
    if (!is.null(region$modelBuildStatus) && nrow(region) > 0) {

      currentStatus <- region$modelBuildStatus

      message("Model build status: ", currentStatus, " (", round(elapsed), "s elapsed)")

      # If the status is "Complete", the combined region is ready to use
      if (tolower(currentStatus) == "complete") {
        message("Combined region '", combinedDescription, "' is ready to use.")
        break  # Exit the polling loop
      }

      # If the build failed, stop immediately with a clear message
      if (tolower(currentStatus) %in% c("failed", "error")) {
        stop("Combined region model build failed with status: '", currentStatus, "'.\n",
             "Try submitting the request again or contact IMPLAN support.")
      }
    }

    # Region not ready, wait before checking again
    Sys.sleep(POLL_INTERVAL_SEC)
  }

  # Return the combined region object so the caller can use it in a project
  invisible(combinedRegion)
})
