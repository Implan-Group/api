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

# Define a method for the Create function with the MultiEventToMultiGroupWorkflow class
setMethod("Examples", signature = "MultiEventToMultiGroupWorkflow", function(object){
  
  aggregationSchemeId <- 8  #546 Un-Aggregated
  industrySetId <- 8  #546 Industries
  dataSetId <- as.integer(96)  #2022
  
  # !!! You will need to enter in the GUID of your own empty Project here !!!
  projectGuid <- "4bc01909-BEEF-BEEF-af8a-2ad16d1dd50b"
  
  #/* Create the Events */
  
  #We need the industry code for restaurants first
  industryCodes_instance <- new("IndustryCodeEndpoints")
  
  IndustryCodes <- GetIndustryCodes(industryCodes_instance,aggregationSchemeId,industrySetId)
  
  industryCode <- IndustryCodes[IndustryCodes$description=="Full-service restaurants",][1,] #[1,] accessing first row
  
  # Create an instance of `project_instance`
  restaurantOutput <- new("IndustryOutputEvent",
                          Title = "Restaurants",
                          IndustryCode = industryCode$code,
                          Output = 1000000,
                          DatasetId = dataSetId
  )
  
  #// Now we need to create the housing events
  #// You need to lookup all the specification codes for Household Income Events
  
  SpecificationEndpoints_instance <- new("SpecificationEndpoints")
  
  householdIncomeSpecifications <- GetSpecifications(SpecificationEndpoints_instance,projectGuid,"HouseholdIncome")
  
  #// Create the 15-30k Household Event
  
  firstHouseholdIncomeEvent <- new("HouseholdIncomeEvent",
                                   Title = "Households 15-30k",
                                   HouseholdIncomeCode = as.integer(10002), #// Households 15-30k (spec code from above)
                                   Value = 25000)
  
  secondHouseholdIncomeEvent <- new("HouseholdIncomeEvent",
                                   Title = "Households 50-70k",
                                   HouseholdIncomeCode = as.integer(10005), #// Households 15-30k (spec code from above)
                                   Value = 125000)
  
  # /* We have created all the Events.
  # * By calling the `AddEvent` endpoint, the fully-hydrated Event is returned (including its Id, which will be required)
  # * We'll store them to an Array for future processing
  # */
  
  
  restaurantOutput = AddEvent(restaurantOutput,projectGuid)
  firstHouseholdIncomeEvent = AddEvent(firstHouseholdIncomeEvent, projectGuid)
  secondHouseholdIncomeEvent = AddEvent(secondHouseholdIncomeEvent, projectGuid)
  
  events <- list(restaurantOutput, firstHouseholdIncomeEvent, secondHouseholdIncomeEvent)
  
  
  # /* Now we need to create our Groups.
  # * For this example, we're comparing the impacts of these Events on several different states
  # */
  
  RegionEndpoints_instance <- new("RegionEndpoints")

  states <- GetRegionChildren(RegionEndpoints_instance, aggregationSchemeId, dataSetId, regionType = "State")

  oregon <- states[states$description == "Oregon",][1,] #[1,] accessing first row

  wisconsin <- states[states$description == "Wisconsin",][1,] #[1,] accessing first row

  northCarolina <- states[states$description == "North Carolina",][1,] #[1,] accessing first row

  #// We'll store these in an array or list for later use
  regions <- list(oregon, wisconsin, northCarolina)

  #// Now, for each Region
  for (region in regions) {

    #// Create a Group for that Region
    stateGroup <- new("GroupEndpoints",
                      ProjectId = projectGuid,
                      Title = paste0(region$description," State"),  #// each Group has to have a different Title
                      DatasetId = dataSetId,
                      DollarYear = as.integer(2024),                      #// latest year
                      HashId = region$hashId,                 #// associate this Region with this Group
                      GroupEvents = lapply(events, AddGroupEvent_function) #// Create a Group for that Region and #check the output and remove or add the $value under common function if needed
                      )

    #// Save the Group to the Project
    GroupEndpoints_instance <- new("GroupEndpoints")
    stateGroup <- AddGroupToProject(stateGroup, projectGuid)


  }

  #// Now that the Events and Groups have been added, see below
  RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")

  print(Examples(RunImpactAnalysisWorkflow_instance,ProjectId = projectGuid))
  #// for ways to run an Analysis and view the Results
  
  
})

