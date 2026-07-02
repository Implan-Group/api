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

# Run AuthenticationWorkflow.R first — you must be logged in before this will work.

source(auth_env$Authentication)           # Login and token handling
source(auth_env$AggregationSchemeEndpoints) # For looking up industry classification schemes
source(auth_env$Rest)                     # HTTP communication layer
source(auth_env$ProjectEndpoints)         # For creating and retrieving projects
source(auth_env$IndustrySetEndpoints)     # For looking up industry sets
source(auth_env$IndustryCodeEndpoints)    # For looking up specific industry codes
source(auth_env$EventEndpoints)           # For creating economic events
source(auth_env$DataSetEndpoints)         # For finding available dataset years
source(auth_env$RegionEndpoints)          # For finding geographic regions
source(auth_env$GroupEndpoints)           # For creating groups (event + region pairings)
source(auth_env$Iworkflow)               # Base workflow interface
source(auth_env$RunImpactAnalysisWorkflow) # Needed to run the analysis at the end

# Define the CreateProjectWorkflow class, inheriting from the base Iworkflow interface
setClass("CreateProjectWorkflow",
         contains = "Iworkflow")

# Define what the Examples() method does for this workflow
setMethod("Examples", signature = "CreateProjectWorkflow", function(object) {

  #Find the Aggregation Scheme
  AllSchemes <- new("AggregationSchemeEndpoints")  # Create an endpoint handler object

  aggregationSchemes <- GetAggregationSchemes(AllSchemes, IndustrySetId = INDUSTRY_SET_ID)

  implan546AggScheme <- aggregationSchemes[
    aggregationSchemes$description == TARGET_SCHEME_DESCRIPTION, ]

  # Confirm we found the scheme, stop with a helpful message if not
  if (nrow(implan546AggScheme) == 0) {
    stop("Aggregation scheme '", TARGET_SCHEME_DESCRIPTION, "' not found. ",
         "Check available schemes by printing the aggregationSchemes data frame.")
  }

  # Extract the numeric ID of the scheme
  aggregationSchemeId <- implan546AggScheme$id

  # Extract the household set ID
  householdSetId <- as.integer(implan546AggScheme$householdSetIds)

  message("Using aggregation scheme: ", TARGET_SCHEME_DESCRIPTION,
          " (ID: ", aggregationSchemeId, ")")

  # Generate a unique title using the current timestamp so duplicate names are avoided
  projectTitle <- paste0("ProjectWorkflow ", format(Sys.time(), "%Y-%m-%d %H:%M:%S"))

  # Create an instance of `project_instance`
  project_instance <- new("ProjectEndpoints",
                          Title = projectTitle,           
                          AggregationSchemeId = aggregationSchemeId, 
                          HouseholdSetId = householdSetId[1]         
  )

  # Send the create request to the API
  project <- Create(project_instance)

  # Validate that the project was created successfully before continuing
  if (is.null(project) || is.null(project$id)) {
    stop("Project creation failed. Check your API credentials and request parameters.")
  }

  message("Project created successfully. Project ID: ", project$id)

  #Look Up the Industry Code 
  industries <- new("IndustrySetEndpoints")   
  industrySets <- GetIndustrySets(industries) 

  # Find the industry set matching our target (546 Industries)
  implan546IndustriesSet <- industrySets[
    industrySets$description == "546 Industries", ][1, ] # [1,] takes the first match if duplicates exist

  # Create an endpoint handler for individual industry codes
  industryCodes <- new("IndustryCodeEndpoints")

  # Get industry codes within our chosen aggregation scheme and industry set
  IndustryCodes <- GetIndustryCodes(industryCodes, aggregationSchemeId, implan546IndustriesSet$id)

  # Find the specific industry code for our target industry
  IndustryCode <- IndustryCodes[IndustryCodes$description == TARGET_INDUSTRY, ][1, ]

  # Confirm the industry was found
  if (nrow(IndustryCode) == 0) {
    stop("Industry '", TARGET_INDUSTRY, "' not found. ",
         "Print IndustryCodes to see all available options.")
  }

  message("Using industry: ", TARGET_INDUSTRY, " (Code: ", IndustryCode$code, ")")

  #Create Events
  # Create an instance of `IndustryOutputEvent`
  industry_output_event <- new("IndustryOutputEvent",
                               Output = 100000,               
                               IndustryCode = IndustryCode$code, 
                               Title = "Industry Output Event"   
  )

  # Send the event to the API 
  industryOutputEvent <- AddEvent(industry_output_event, projectGuid = project$id)

  # Validate the event was created
  if (is.null(industryOutputEvent) || is.null(industryOutputEvent$id)) {
    stop("Failed to create Industry Output Event. Check event parameters.")
  }

  message("Industry Output Event created. ID: ", industryOutputEvent$id)

  #Industry Impact Analysis Event

  industryImpactAnalysisEvent <- new("IndustryImpactAnalysisEvent",
                                     Title = "Industry Impact Analysis Event", 
                                     IndustryCode = IndustryCode$code,          
                                     IntermediateInputs = 500000,   
                                     EmployeeCompensation = 250000, 
                                     ProprietorIncome = 50000,      
                                     WageAndSalaryEmployment = 4,  
                                     ProprietorEmployment = 1,     
                                     TotalEmployment = 5,           
                                     TotalLaborIncome = 300000,    
                                     OtherPropertyIncome = 100000,  
                                     TaxOnProductionAndImports = 100000, 
                                     SpendingPatternDatasetId = as.integer(87),
                                     SpendingPatternValueType = as.character(  
                                       SpendingPatternValueType[
                                         SpendingPatternValueType == "IntermediateExpenditure"])
  )

  # Send the second event to the API
  industryImpactAnalysisEvent <- AddEvent(industryImpactAnalysisEvent, projectGuid = project$id)

  # Validate the second event was created
  if (is.null(industryImpactAnalysisEvent) || is.null(industryImpactAnalysisEvent$id)) {
    stop("Failed to create Industry Impact Analysis Event. Check event parameters.")
  }

  message("Industry Impact Analysis Event created. ID: ", industryImpactAnalysisEvent$id)

  #Find Dataset and Region 

  # Get all available datasets for our aggregation scheme
  datasets_instance <- new("DataSetEndpoints")
  datasets <- GetDataSets(datasets_instance, aggregationSchemeId)

  # Find the dataset matching our target year
  dataset <- datasets[datasets$description == TARGET_DATASET_DESCRIPTION, ][1, ]

  if (nrow(dataset) == 0) {
    stop("Dataset '", TARGET_DATASET_DESCRIPTION, "' not found. ",
         "Print datasets to see all available options.")
  }

  message("Using dataset: ", TARGET_DATASET_DESCRIPTION, " (ID: ", dataset$id, ")")

  # Get all state-level regions for our scheme and dataset
  Regions_instance <- new("RegionEndpoints")
  stateRegions <- GetRegionChildren(Regions_instance,
                                    aggregationSchemeId = aggregationSchemeId,
                                    dataSetId = dataset$id,
                                    regionType = "State") 

  # Find our target state
  targetStateRegion <- stateRegions[stateRegions$description == TARGET_STATE, ][1, ]

  if (nrow(targetStateRegion) == 0) {
    stop("State '", TARGET_STATE, "' not found. ",
         "Print stateRegions to see all available states.")
  }

  # Extract the hashId 
  stateHashId <- targetStateRegion$hashId

  message("Using region: ", TARGET_STATE, " (HashId: ", stateHashId, ")")

  #Create a Group 

  group_instance <- new("GroupEndpoints",
                        ProjectId = project$id,      
                        Title = "Sample Group",       
                        DatasetId = dataset$id,       
                        DollarYear = DOLLAR_YEAR,     
                        HashId = stateHashId,         

                        # Attach both events to this group
                    
                        GroupEvents = list(
                          GroupEvent(new("Event", eventId = industryOutputEvent$id)),
                          GroupEvent(new("Event", eventId = industryImpactAnalysisEvent$id))
                        )
  )

  # Send the group to the API — links the events to the region within this project
  group <- AddGroupToProject(projectGuid = project$id, group_instance)

  # Validate the group was created successfully
  if (is.null(group)) {
    stop("Failed to create group. Check that all event IDs and region hashId are valid.")
  }

  message("Group created and linked to project. Running impact analysis...")

  #Run the Impact Analysis 
  
  RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")

  # Pass the project ID so the analysis workflow knows which project to run
  print(Examples(RunImpactAnalysisWorkflow_instance, ProjectId = project$id))
})
