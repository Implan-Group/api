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


source('implan_api_helper.R')
library(httr2)
library(uuid)
library(glue)

options(warn=1)
options(width = 300)  # Set the maximum width of the output
options(max.print = 10000)  # Set the maximum number of lines to print


#getting authorization token
jwt_token = getImplanAuth();

#reading in state data and not losing the leading 0's on the fips codes
state_based_csv_data <- read.csv("state_based.csv",colClasses = c("character", "character"))

#grabbing the model name and fips code 
state_model_name_to_fips <- state_based_csv_data[c("model_name","fips")]

#getting a unique list of model names 
unique_state_model_names <- unique(state_model_name_to_fips$model_name)

#creating a list to keep track of the models we're building for the projects that need to be built
models_for_projects <- list()

#loop over each unique model name
for (model_name in unique_state_model_names) {
  #getting a model name that's unique for the dataset so we can run the script across different datasets
  dataset_specific_model_name <- glue("{model_name}_{aggregation_scheme_id}_{data_set_id}")
  
  #calling to Implan to see if the model exists
  does_model_exist = doesUserModelExist(dataset_specific_model_name)
 
  #creating a data.frame() to save a regionCard we need to.
  regionCard <- data.frame()
 
  if(does_model_exist == FALSE){
    #if we're here the model does not exist and needs to be built.
    
    #extracting the fips codes we need for the combined model
    fipcodes <- state_model_name_to_fips[state_model_name_to_fips$model_name == model_name, "fips"]
    
    #creating a list to capture the urids based on the fips codes.
    urids <- list()
    
    #loop over each fips code to get the URIDs and add it to the list
    for(fips in fipcodes){
      #taking the urid from the regionCard that is returned and adding it to the list of URIDs to build the combined model with
      urids[length(urids)+1] <- getRegionCardByFipsCode(fips)["urid"]
    }
    #build the combined region and get the regionCard
    regionCard = buildCombinedRegion(dataset_specific_model_name,urids)
    
    #wait until the model is built
    waitForModelToBuild(dataset_specific_model_name)
  }
  #now that the model is built let's update the regionCard
  regionCard = getUserModel(dataset_specific_model_name)
  
  #add the regionCard we need to the list of models we will use in our projects
  models_for_projects <- c(models_for_projects, list(regionCard))
}

#reading in county data and not losing the leading 0's on the fips codes
county_based_csv_data <- read.csv("county_based.csv",colClasses = c("character", "character"))

#grabbing the model name and fips code 
county_model_name_to_fips <- county_based_csv_data[c("model_name","fips")]

#getting a unique list of model names 
unique_county_model_names <- unique(county_model_name_to_fips$model_name)

#loop over each unique model name
for (model_name in unique_county_model_names) {
  #getting a model name that's unique for the dataset so we can run the script across different datasets
  dataset_specific_model_name <- glue("{model_name}_{aggregation_scheme_id}_{data_set_id}")
  
  #calling to Implan to see if the model exists
  does_model_exist = doesUserModelExist(dataset_specific_model_name)
  
  #creating a data.frame() to save a regionCard we need to.
  regionCard <- data.frame()
  
  if(does_model_exist == FALSE){
    #if we're here the model does not exist and needs to be built.
    
    #extracting the fips codes we need for the combined model
    fipcodes <- county_model_name_to_fips[county_model_name_to_fips$model_name == model_name, "fips"]
    
    #creating a list to capture the urids based on the fips codes.
    urids <- list()
    
    #loop over each fips code to get the URIDs and add it to the list
    for(fips in fipcodes){
      #taking the urid from the regionCard that is returned and adding it to the list of URIDs to build the combined model with
      urids[length(urids)+1] <- getRegionCardByFipsCode(fips)["urid"]
    }
    #build the combined region and get the regionCard
    regionCard = buildCombinedRegion(dataset_specific_model_name,urids)
    
    #wait until the model is built
    waitForModelToBuild(dataset_specific_model_name)
  }
  #now that the model is built let's update the regionCard
  regionCard = getUserModel(dataset_specific_model_name)
  
  #add the regionCard we need to the list of models we will use in our projects
  models_for_projects <- c(models_for_projects, list(regionCard))
}

#reading event data
events_csv <- read.csv("demo_events.csv",colClasses = c("character", "character"))

#extracting only industry output events
industry_output_events = events_csv[events_csv$Type == "Industry Output", ]

#extracting only commodity output events
commodity_output_events = events_csv[events_csv$Type == "Commodity Output", ]


#checking to see if the folder exists on Implan.  This is where we're putting the projects
if(doesFolderExist(folder_name) == FALSE){
  #creating the folder if it does not exist
  createFolder(folder_name)
}

#getting the folder
folder <- getFolder(folder_name)

#looping over all the models we captured from above
for(regionCard in models_for_projects){
  #getting the model name or description from the region card
  model_name <- regionCard["description"]
  
  #generating some random data to avoid naming conflicts when running the script many times
  uniqueId <- UUIDgenerate()
  
  #getting a unique project name
  project_name <- glue("{model_name}-{uniqueId}")
  
  #creating the project on Implan in the folder with the specified name
  project = createProject(project_name, folder["id"][[1]])
  
  #creating a list to capture the events we're creating to add to the group later
  events_for_project <- list()
  
  #looping over all the industry output events
  for (i in 1:nrow(industry_output_events)) {
    #getting the event information
    row <- industry_output_events[i, ]
    #adding the event to the project
    industryEvent = addIndustryOutputEvent(project, row$Name, row$Code, row$Value)
    #saving the event in our list for the group creation later
    events_for_project <- c(events_for_project, list(industryEvent))
  }
  
  #looping over all the commodity output events
  for (i in 1:nrow(commodity_output_events)) {
    #getting the event information
    row <- commodity_output_events[i, ]
    #adding the event to the project
    commodityEvent = addCommodityOutput(project, row$Name, row$Code, row$Value)
    #saving the event in our list for the group creation later
    events_for_project <- c(events_for_project, list(commodityEvent))
  }
  
  #Create group in the project with the name of the regionCard and  events we created
  addGroup(project, regionCard$description, regionCard,group_dollar_year, events_for_project )
  
  #run the project and get the runId
  runId = runProject(project)
  
  #wait for the project to complete running
  waitForProjectRunToComplete(runId)
  
  
  #get the results from the Impact and save them
  getSummaryEconomicIndiciators(project, runId)
  getSummaryTaxes(project, runId)
  getDetailedTaxes(project, runId)
  getDetailEconomicIndicators(project, runId)
}

#generating some random data to avoid naming conflicts when running the script many times
uniqueId = UUIDgenerate()

#creating a project name for all the models in one project
project_name <- glue("All Models Project {uniqueId}")

#creating the project on Implan
project = createProject(project_name, folder["id"][[1]])

#creating a list to capture the events we're creating to add to the group later
events_for_project <- list()

#looping over all the industry output events
for (i in 1:nrow(industry_output_events)) {
  #getting the event information
  row <- industry_output_events[i, ]
  #adding the event to the project
  industryEvent = addIndustryOutputEvent(project, row$Name, row$Code, row$Value)
  #saving the event in our list for the group creation later
  events_for_project <- c(events_for_project, list(industryEvent))
}

#looping over all the commodity output events
for (i in 1:nrow(commodity_output_events)) {
  #getting the event information
  row <- commodity_output_events[i, ]
  #adding the event to the project
  commodityEvent = addCommodityOutput(project, row$Name, row$Code, row$Value)
  #saving the event in our list for the group creation later
  events_for_project <- c(events_for_project, list(commodityEvent))
}
#looping over all the models we captured from above
for(regionCard in models_for_projects){
  #Create group in the project with the name of the regionCard and  events we created
  addGroup(project, regionCard$description, regionCard,group_dollar_year, events_for_project )
}

#run the project and get the runId
runId = runProject(project)

#wait for the project to complete running
waitForProjectRunToComplete(runId)

#get the results from the Impact and save them
getSummaryEconomicIndiciators(project, runId)
getSummaryTaxes(project, runId)
getDetailedTaxes(project, runId)
getDetailEconomicIndicators(project, runId)

#output any warnings 
warnings()