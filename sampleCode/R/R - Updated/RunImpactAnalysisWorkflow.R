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

# ── Configuration Constants ────────────────────────────────────────────────────
# Adjust these values if you need a different timeout or polling interval.

MAX_WAIT_SECONDS  <- 600L  # Maximum time to wait for analysis to complete (10 minutes)
POLL_INTERVAL_SEC <- 10L   # How many seconds to wait between status checks
DOLLAR_YEAR       <- 2024L # Dollar year used when requesting growth percentage results


source(auth_env$ProjectEndpoints)       # For fetching project details
source(auth_env$ImpactEndpoints)        # For triggering and checking analysis status
source(auth_env$ImpactResultEndpoints)  # For downloading results once analysis is done
source(auth_env$Iworkflow)              # Base workflow interface

setClass("RunImpactAnalysisWorkflow",
         contains = "Iworkflow",
         slots = list(
           ProjectId = "character"  
         ),
         prototype = list(
           ProjectId = ""           
         ))

# Create a generic function for Create
#setGeneric("Examples", function(object,ProjectId) standardGeneric("Examples"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("Examples", signature = "RunImpactAnalysisWorkflow", function(object, ProjectId) {

  # Make sure a non-empty ProjectId was passed in before making any API calls.
  if (!nzchar(ProjectId)) {
    stop("ProjectId must not be empty. Pass the GUID of the project you want to analyze.")
  }

  # Confirm the project exists before triggering the analysis.
  projects_instance <- new("ProjectEndpoints")  # Create an endpoint handler for projects

  # GetProjects() returns all projects owned by the authenticated user
  projects <- GetProjects(projects_instance)

  # GetSharedProjects() returns projects that have been shared with the user by others
  shared <- GetSharedProjects(projects_instance)

  # Retrieve the specific project by GUID — confirms it exists and is accessible
  project <- GetProject(projects_instance, ProjectId = ProjectId)

  # Validate the project was found before proceeding
  if (is.null(project)) {
    stop("Project not found. Check that ProjectId '", ProjectId,
         "' is correct and that you have access to it.")
  }

  message("Project found: ", project$title, " | ID: ", ProjectId)


  impactRun_instance <- new("ImpactEndpoints") # Create an endpoint handler for impact runs

  #check status and retrieve results later
  impactRunId <- RunImpact(impactRun_instance, ProjectId)

  # Validate that we received a valid run ID
  if (is.null(impactRunId) || !nzchar(as.character(impactRunId))) {
    stop("Failed to start impact analysis for project '", ProjectId, "'. ",
         "Ensure the project has at least one group with events assigned.")
  }

  message("Impact analysis started. Run ID: ", impactRunId)

  #Poll Until Analysis Completes
  poll_start <- Sys.time()  # Record when we started polling so we can enforce the timeout

  terminal_error_statuses <- c("failed", "error", "cancelled")

  while (TRUE) {

    # Calculate how many seconds have passed since we started polling
    elapsed <- as.numeric(difftime(Sys.time(), poll_start, units = "secs"))

    # If we've been waiting longer than the allowed maximum, give up and report an error
    if (elapsed > MAX_WAIT_SECONDS) {
      stop(
        "Impact analysis timed out after ", MAX_WAIT_SECONDS, " seconds.\n",
        "The analysis may still be running on IMPLAN's servers.\n",
        "Impact run ID: ", impactRunId, "\n",
        "You can check status manually or increase MAX_WAIT_SECONDS at the top of this file."
      )
    }

    # Ask the API for the current status of this analysis run
    status <- GetImpactStatus(impactRun_instance, impactRunId)

    message("Analysis status: ", status, " (", round(elapsed), "s elapsed)")

    # Check whether the status is a known terminal error — if so, fail fast
    # tolower() makes the comparison case-insensitive
    if (!is.null(status) && tolower(status) %in% terminal_error_statuses) {
      stop(
        "Impact analysis ended with a failure status: '", status, "'.\n",
        "Check your project configuration and try re-running the analysis.\n",
        "Impact run ID: ", impactRunId
      )
    }

    # Check whether the analysis has completed successfully
    if (!is.null(status) && tolower(status) == "complete") {
      message("Analysis complete. Retrieving results...")
      break  # Exit the polling loop and proceed to fetch results
    }

    # Analysis is still running — wait before checking again
    Sys.sleep(POLL_INTERVAL_SEC)
  }

  #Get Results 
  ImpactResults_instance <- new("CsvReports") 

  #Detailed Economic Indicators 
  detailedEconomicIndicators <- GetDetailedEconomicIndicators(ImpactResults_instance, impactRunId)
  print(detailedEconomicIndicators)

  summaryEconomicIndicators <- GetSummaryEconomicIndicators(ImpactResults_instance, impactRunId)
  print(summaryEconomicIndicators)

  detailedTaxes <- GetDetailedTaxes(ImpactResults_instance, impactRunId)
  print(detailedTaxes)

  summaryTaxes <- GetSummaryTaxes(ImpactResults_instance, impactRunId)
  print(summaryTaxes)

  #Estimated Growth Percentage 
  estimatedGrowthPercentageFilter <- new("EstimatedGrowthPercentageFilter",
                                         DollarYear  = DOLLAR_YEAR, # Dollar year for value adjustments
                                         Regions     = list(),       # Filter by region (empty = all regions)
                                         Impacts     = list(),       # Filter by impact type (empty = all)
                                         GroupNames  = list(),       # Filter by group name (empty = all)
                                         EventNames  = list(),       # Filter by event name (empty = all)
                                         EventTags   = list()        # Filter by event tag (empty = all)
  )

 #Get Growth percentage data
  estimatedGrowthPercentage <- GetEstimatedGrowthPercentage(
    estimatedGrowthPercentageFilter,
    impactRunId = impactRunId
  )
  print(estimatedGrowthPercentage)

  message("All results retrieved successfully for impact run ID: ", impactRunId)
})
