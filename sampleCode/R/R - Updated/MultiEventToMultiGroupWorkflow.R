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

# ── Multi-Event to Multi-Group Workflow ────────────────────────────────────────
# This workflow demonstrates how to model the same set of economic events
# across multiple geographic regions simultaneously.
#

#   - Complete AuthenticationWorkflow.R first
#   - Provide a valid projectGuid for an existing, empty IMPLAN project below
# ──────────────────────────────────────────────────────────────────────────────

# ── Load Dependencies ──────────────────────────────────────────────────────────

source(auth_env$Rest)                   
source(auth_env$CommonFunctions)        
source(auth_env$ProjectEndpoints)      
source(auth_env$IndustrySetEndpoints)  
source(auth_env$IndustryCodeEndpoints)  
source(auth_env$EventEndpoints)        
source(auth_env$DataSetEndpoints)     
source(auth_env$RegionEndpoints)   
source(auth_env$GroupEndpoints)        
source(auth_env$SpecificationEndpoints) 
source(auth_env$Iworkflow)            
source(auth_env$RunImpactAnalysisWorkflow) 

setClass("MultiEventToMultiGroupWorkflow",
         contains = "Iworkflow")


# Changing these values is all that's needed to adapt this workflow to a new use case.
# Set your project and analysis parameters here.
AGGREGATION_SCHEME_ID  <- 8L    # 8 = 546 Un-Aggregated 
INDUSTRY_SET_ID        <- 8L    # 8 = 546 Industries 
DATA_SET_ID            <- 96L   # 96 = 2022 economic data
DOLLAR_YEAR            <- 2024L # Dollar year for value adjustments in groups

# !!! You will need to enter in the GUID of your own empty Project here !!!
PROJECT_GUID <- Sys.getenv("IMPLAN_PROJECT_GUID")

# The states to compare in this analysis. You can add, remove, or replace
TARGET_STATES <- c("Oregon", "Wisconsin", "North Carolina")

# Define what Examples() does for this workflow
setMethod("Examples", signature = "MultiEventToMultiGroupWorkflow", function(object) {

  # ── Validate Project GUID ───────────────────────────────────────────────────
  if (!nzchar(PROJECT_GUID)) {
    stop(
      "PROJECT_GUID is not set.\n",
      "Set your project GUID as an environment variable before running:\n",
      "  Sys.setenv(IMPLAN_PROJECT_GUID = \"your-guid-here\")\n",
      "You can find your project GUID in your IMPLAN account, or by running CreateProjectWorkflow.R."
    )
  }

  message("Using project GUID: ", PROJECT_GUID)

  #We need the industry code for restaurants first
  industryCodes_instance <- new("IndustryCodeEndpoints")  # Create the endpoint handler

  IndustryCodes <- GetIndustryCodes(industryCodes_instance, AGGREGATION_SCHEME_ID, INDUSTRY_SET_ID)

  industryCode <- IndustryCodes[IndustryCodes$description == "Full-service restaurants", ][1, ]

  # Confirm the industry was found
  if (nrow(industryCode) == 0) {
    stop("Industry 'Full-service restaurants' not found. ",
         "Print IndustryCodes to see all available options.")
  }

  message("Industry code found: Full-service restaurants (Code: ", industryCode$code, ")")

  # Create an instance of `project_instance`
  restaurantOutput <- new("IndustryOutputEvent",
                          Title = "Restaurants",              # A label to identify this event
                          IndustryCode = industryCode$code,   # Which industry produces this output
                          Output = 1000000,                   # Dollar value of output to model
                          DatasetId = DATA_SET_ID             # Which year of data to use
  )

  #Look Up Household Income Specification Codes 
  # Household Income Events require specification codes that identify income brackets.
  #You need to lookup all the specification codes for Household Income Events
  SpecificationEndpoints_instance <- new("SpecificationEndpoints")

  # Fetch all available specification codes for HouseholdIncome event types
  householdIncomeSpecifications <- GetSpecifications(
    SpecificationEndpoints_instance,
    PROJECT_GUID,
    "HouseholdIncome"  # The event type category we want specifications for
  )

  message("Household income specifications retrieved. Creating household income events...")

  #Create Household Income Events
 
  # Event for households earning $15,000–$30,000 per year
  firstHouseholdIncomeEvent <- new("HouseholdIncomeEvent",
                                   Title = "Households 15-30k",           
                                   HouseholdIncomeCode = as.integer(10002), # Bracket code: $15k-$30k
                                   Value = 25000                            # Dollar value of income to model
  )

  # Event for households earning $50,000–$70,000 per year
  secondHouseholdIncomeEvent <- new("HouseholdIncomeEvent",
                                    Title = "Households 50-70k",           
                                    HouseholdIncomeCode = as.integer(10005), # Bracket code: $50k-$70k
                                    Value = 125000                           # Dollar value of income to model
  )

  #Add All Events to the Project 
  # AddEvent() sends each event to the API and returns a fully-hydrated event object,
  # including the event ID that is required when creating groups.

  restaurantOutput          <- AddEvent(restaurantOutput, PROJECT_GUID)
  firstHouseholdIncomeEvent <- AddEvent(firstHouseholdIncomeEvent, PROJECT_GUID)
  secondHouseholdIncomeEvent <- AddEvent(secondHouseholdIncomeEvent, PROJECT_GUID)

  # Validate all events were created successfully before building groups
  for (evt in list(restaurantOutput, firstHouseholdIncomeEvent, secondHouseholdIncomeEvent)) {
    if (is.null(evt) || is.null(evt$id)) {
      stop("One or more events failed to create. Check event parameters and project GUID.")
    }
  }

  # Collect all events into a list for easy iteration when building groups
  events <- list(restaurantOutput, firstHouseholdIncomeEvent, secondHouseholdIncomeEvent)

  message("All events created and added to project. Creating state groups...")

  #Create Groups
  #For this example, we're comparing the impacts of these Events on several different states
  RegionEndpoints_instance <- new("RegionEndpoints")  # Create the endpoint handler

  
  states <- GetRegionChildren(RegionEndpoints_instance,
                              AGGREGATION_SCHEME_ID,
                              DATA_SET_ID,
                              regionType = "State")

  # Look up each target state and collect them into a list
  regions <- lapply(TARGET_STATES, function(state_name) {

    # Find the row matching this state name
    region <- states[states$description == state_name, ][1, ]

    # If the state wasn't found, stop with a clear message so the user can fix it
    if (nrow(region) == 0) {
      stop("State '", state_name, "' not found in region data. ",
           "Check that the name matches exactly (e.g. 'North Carolina', not 'NC').")
    }

    region 
  })

  message("Regions found: ", paste(TARGET_STATES, collapse = ", "))

 
  for (region in regions) {

    # Build a unique title for this group using the state name
    groupTitle <- paste0(region$description, " State")

    # Create the group object with all required fields
    stateGroup <- new("GroupEndpoints",
                      ProjectId  = PROJECT_GUID,           
                      Title      = groupTitle,             
                      DatasetId  = DATA_SET_ID,            
                      DollarYear = DOLLAR_YEAR,            
                      HashId     = region$hashId,          

                      # Attach all events to this group using the helper function
                      # AddGroupEvent_function() formats each event into the structure the API expects
                      GroupEvents = lapply(events, AddGroupEvent_function)
    )

    # Send the group to the API 
    GroupEndpoints_instance <- new("GroupEndpoints")
    stateGroup <- AddGroupToProject(stateGroup, PROJECT_GUID)

    # Validate the group was created before moving to the next state
    if (is.null(stateGroup)) {
      stop("Failed to create group for state: ", region$description,
           ". Check that the project GUID and region hashId are valid.")
    }

    message("Group created for: ", region$description)
  }

  message("All state groups created. Launching impact analysis...")

  #Run the Impact Analysis
  # Now that all events and groups are in place, trigger the analysis.

  RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")

  # Pass the project GUID so the analysis workflow knows which project to run
  print(Examples(RunImpactAnalysisWorkflow_instance, ProjectId = PROJECT_GUID))
})
