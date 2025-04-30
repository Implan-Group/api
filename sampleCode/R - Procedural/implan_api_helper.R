library(httr) #library for making HTTP calls
library(jsonlite) #library for JSON
library(glue) #library for string interpolation 
library(uuid) # library for creating uuids

aggregation_scheme_id = 14 # aggregation scheme 8 is 546 
data_set_id = 98 # DatasetId 
group_dollar_year <- 2021 #dollar year for groups
folder_name <- "r_demo_folder_11" #folder name to save to on Implan

base_url_implan <- "https://api.implan.com" #base url for API calls
implan_env_path <- "/api" #environment #Beta:/beta/api Prod:/api 



private_dir <- "private" #private directory for sensitive information like credentials.  
cache_dir <- "cache" #cache directory for tokens and model data.  
results_dir <- "results" #directory for results


#creating directory if needed
if(file.exists(cache_dir) == FALSE){
  dir.create(cache_dir)
}

#creating directory if needed
if(file.exists(results_dir) == FALSE){
  dir.create(results_dir)
}

#helper function that changes the name of a file to be put into the directory
getCacheFile <- function(fileName){
  filepath = glue("{cache_dir}/{fileName}")
  return (filepath)
}

#helper function that changes the name of a file to be put into the directory
getPrivateFile <- function(fileName){
  filepath = glue("{private_dir}/{fileName}")
  return (filepath)
}

#helper function that changes the name of a file to be put into the directory
getResultsFile <- function(fileName){
  filepath = glue("{results_dir}/{fileName}")
  return (filepath)
}

#method to get the JWT token.  We save it to a file and refresh it before expiration of 480 minutes. 
getImplanAuth <- function(){
  refresh <- FALSE
  
  #getting the file to save the token in
  savedTokenFile = getCacheFile("saved_token.json")
  
  if(file.exists(savedTokenFile)){
    #if the file exists, extract the JSON
    json_data <- fromJSON(savedTokenFile)
    
    #get the saved date
    saved_date <- json_data$date
    #get the token
    token <- json_data$token
    
    #get the time difference
    time_diff <- difftime(Sys.time(), saved_date , units = "min")
   
    #determine if we need to refresh the token
    refresh = time_diff > 479;
    
  }else{
    refresh = TRUE
  }
  
  if(refresh){
    #making the URL for the auth URL
    url <- glue("{base_url_implan}/auth")
    print(url)
    
    credsFile = getPrivateFile("creds.json")
    credsJson <- fromJSON(credsFile)
    
    .email <- credsJson$username
    .password <- credsJson$password
    
    #making an object to send credentials 
    body <- list(username = .email, password = .password)
    
    #converting the object to json
    body_json <- toJSON(body, auto_unbox = TRUE)
    
    #making the post and getting the token
    response <- POST(url, body = body_json, add_headers("Content-Type" = "application/json"))
    
    #extacting the token
    implan_token = content(response,"text", encoding = "UTF-8")
    
    #creating an object to save the time and token
    data <- list(date = Sys.time(), token = implan_token)
    #converting it to Json
    json_data <- toJSON(data, pretty = TRUE)
    
    #writing to a file for later use
    writeLines(json_data, savedTokenFile)
  }
  
  #pulling from the file into dataframe
  json_data <- fromJSON(savedTokenFile)
  
  date <- json_data$date
  jwt_token <- json_data$token
  
  #returning the token
  return (jwt_token)
}

buildCombinedRegion <- function(model_name, urids){
  #making the URL for the building a combined region
  url <- glue("{base_url_implan}{implan_env_path}/v1/region/build/combined/{aggregation_scheme_id}")
  
  #creating object to post to endpoint
  model_data <- list(description = model_name, urids = urids)

  #converting it to json
  json_data <- toJSON(model_data, auto_unbox = TRUE, pretty = TRUE)
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #posting to create the combined region and getting the response
  response <- POST(url, body = json_data, add_headers("Content-Type" = "application/json","Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response,"text")
  
  #converting from json to data frame
  json_content <- fromJSON(content)
  
  #returning the regioncard
  return(json_content[[1]])
  
}

getRegionCardByFipsCode <- function(fips_code){
 
  #using the last 3 characters to determine if the fips code is for a state or not.
  isState = nchar(fips_code) == 2 || (nchar(fips_code) >= 3 && substr(fips_code, nchar(fips_code) - 2, nchar(fips_code)) == "000")
 
  #getting the first two characters for the state fips
  state_fips <- substr(fips_code, 1, 2)
  
  #creating the file to save the states file in cache
  file_prefix = gsub("/", "_", implan_env_path)
  env_state_fips_to_urid_file_name = glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_states.json")
  env_state_fips_to_urid_file_name <- getCacheFile(env_state_fips_to_urid_file_name)
  
  #checking to see if the file exists
  if(file.exists(env_state_fips_to_urid_file_name) == FALSE){
    #making the URL for the getting the state region cards
    url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/children")
  
    #getting the json token
    authorization_header <- getImplanAuth()
    
    #making the get call to get the state regions
    response <- GET(url, add_headers(Authorization = authorization_header))
    
    #extracting the content
    content <- content(response, "text", encoding = "UTF-8")
  
    #converting from json to object
    json_content <- fromJSON(content)
  
    #writing response to cache
    writeLines(toJSON(json_content, pretty = TRUE), env_state_fips_to_urid_file_name)
  }
  #reading state region cards from cache
  state_data <- fromJSON(env_state_fips_to_urid_file_name)
  #getting the state region card we're interested in
  region_card <- state_data[state_data$fipsCode == state_fips, ]
 
  if(isState == FALSE){
    #the requested fips code was not for a state
    
    #creating file name for cache
    state_children_file_name = glue("{file_prefix}_{state_fips}_{aggregation_scheme_id}_{data_set_id}_children.json")
    state_children_file_name <- getCacheFile(state_children_file_name)
   
    #checking to see if we already have the state's children saved in cache
    if(file.exists((state_children_file_name)) == FALSE){
      #making the URL for the getting the children of states
      url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/{region_card$urid}/children")
      print((url))
      print((state_children_file_name))
    
      #getting the json token
      authorization_header <- getImplanAuth()
      print(url)
 
       #making the get call to get the county regions
      response <- GET(url, add_headers(Authorization = authorization_header))
     
      #extracting the content
      content <- content(response, "text")
      
      #converting json to object
      json_content <- fromJSON(content)
      
      #writing response to cache
      writeLines(toJSON(json_content, pretty = TRUE), state_children_file_name)
    }
    #reading from the state child cache
    child_data <- fromJSON(state_children_file_name)
    
    #remove empty rows
    child_data <- child_data[!is.na(child_data$fipsCode), ]
    
    #getting the region card requested
    region_card_child <- child_data[child_data$fipsCode == fips_code, ]
    
    #returning requested child of state regioncard
    return(region_card_child)
  }
  #returning state card
  return (region_card)
}

getUserModel <- function(model_name, force_refresh = FALSE){
  #creating file name for user model cache
  file_prefix = gsub("/", "_", implan_env_path)
  env_user_models_file_name = glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_user_models.json")
  env_user_models_file_name <- getCacheFile(env_user_models_file_name)
  
  if(force_refresh ||  file.exists(env_user_models_file_name) == FALSE) {
    #we need to refresh the usermodel cache 
      
    #making the URL to get the user models
    url <- glue("{base_url_implan}{implan_env_path}/v1/region/{aggregation_scheme_id}/{data_set_id}/user")
    print(url)
    #getting the json token
    authorization_header <- getImplanAuth()
    
    #making the get call to get user models
    response <- GET(url, add_headers(Authorization = authorization_header))
    
    #extracting the content
    content <- content(response, "text", encoding = "UTF-8")
    
    #converting json to object
    json_content <- fromJSON(content)
   
    #writing response to cache
    writeLines(toJSON(json_content, pretty = TRUE), env_user_models_file_name)
  }

  #pulling the user model cache
  user_data <- fromJSON(env_user_models_file_name)
  
  #handling case where there are no user models for the aggregation scheme/dataset pair
  if(is.data.frame(user_data) == FALSE){
    return(NULL)
  }
 
  #getting the requested user card
  region_card <- user_data[user_data$description == model_name, ]
  
  #returning the requested card
  return (region_card)
}

doesUserModelExist <- function(model_name){
  #creating file name for user model cache
  file_prefix = gsub("/", "_", implan_env_path)
  env_user_models_file_name = glue("{file_prefix}_{aggregation_scheme_id}_{data_set_id}_user_models.json")
  env_user_models_file_name <- getCacheFile(env_user_models_file_name)
  
  #checking to see if the file exists and creating it if it doesn't
  if(file.exists(env_user_models_file_name) == FALSE){
    getUserModel(model_name)
  }
 
  #pulling user models from cache
  user_data <- fromJSON(env_user_models_file_name)
 
  #handling when there are no user models available for the aggregation scheme dataset pair
  if(is.data.frame(user_data) == FALSE){
    return(FALSE)
  }
  
  #getting the requested region card from the userdata cache
  region_card <- user_data[user_data$description == model_name, ]
 
  #if there is no data, force a refresh
  if(nrow(region_card) == 0){
   region_card = getUserModel(model_name, TRUE)
  }
  
  #if there is no data return false
  return (nrow(region_card) > 0)
}


waitForModelToBuild <- function(model_name){
  #checking to see if the model exists
  exists <- doesUserModelExist(model_name)
  
  #if it doesn't exist stop running
  if(exists == FALSE)
    return (FALSE)
  
  #getting the region card
  region_card <- getUserModel(model_name)
  
  #checking to see if it's already built
  build_complete <- region_card["modelBuildStatus"] == "Complete"
  
  if(build_complete == FALSE){
    #it's not built so we're checking 30 times with 30 seconds in between requests for the model to build
    for (i in 1:30) {
      print("model not built checking again in 30 seconds")
      
      #sleeping for 30 seconds
      Sys.sleep(30)
      
      #getting the region card and forcing a refresh
      region_card <- getUserModel(model_name, TRUE)
      
      #checking to see if the model build is complete
      build_complete <- region_card["modelBuildStatus"] == "Complete"
      
      #if the model is built stop looping
      if(build_complete){
        break;
      }
    }
  }
  #return the status of the model build
  return (build_complete)
}

createFolder <- function(folder_name){
  
  #making the URL to create folders
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")
  
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #creating folderdata to post
  folder_data <- list(title = folder_name)
  
  #converting object to Json
  json_data <- toJSON(folder_data, auto_unbox = TRUE, pretty = TRUE)

  #making HTTP request to create the folder
  response <- POST(url,body=json_data, add_headers("Content-Type" = "application/json","Authorization" = authorization_header))
  
  #returning the created folder
  return (getFolder(folder_name))
}

doesFolderExist <- function(folder_name){
  #making the URL to get a folder
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get a folder
  response <- GET(url, add_headers("Content-Type" = "application/json","Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #converting from json to data frame
  json_content <- fromJSON(content)
  
  #pulling the folder from the response
  folder <- json_content[json_content$title == folder_name, ]
  
  #returning false if the folder doesn't exist
  return (nrow(folder) > 0)
}

getFolder <- function(folder_name){
  #making the URL to get a folder
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/folder")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get a folder
  response <- GET(url, add_headers(Authorization = authorization_header))
 
  #extracting the content
  content <- content(response, "text")
  
  #converting from json to data frame
  json_content <- fromJSON(content)
  #pulling the folder from the response
  folder <- json_content[json_content$title == folder_name, ]
  
  #returning folder
  return (folder)
}

createProject <- function(name, folderId = NA, isMrio = FALSE, householdSetId = 1){
  
  #making the URL to create a project
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project")
  #getting the json token
  authorization_header <- getImplanAuth()
 
  #creating project data object for posting to create the Project
  project_data <- list(Id=UUIDgenerate(), AggregationSchemeId = aggregation_scheme_id, HouseholdSetId = householdSetId, Title = name, FolderId = folderId, IsMrio = isMrio)
  
  #converting object to Json
  json_data <- toJSON(project_data, auto_unbox = TRUE, pretty = TRUE, na = "null")
 
  #making HTTP Post request to create project
  response <- POST(url, body = json_data, add_headers("Content-Type" = "application/json", "Authorization" = authorization_header))
  
  #returing the created project
  return (getProject(name))
}

getProject <- function(project_name){
  #making the URL to get projects
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get projects
  response <- GET(url, add_headers(Authorization = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #converting from Json to data frame
  json_content <- fromJSON(content)
  
  #getting the requested project
  project <- json_content[json_content$title == project_name, ]
  
  #returning the project
  return (project)
}

addIndustryOutputEvent <- function(project, title, industry_code, output){
  #making the URL to add an event to a project
  project_id = project["id"][[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/event")

  #getting the json token
  authorization_header <- getImplanAuth()
  event_data <- list(Id=UUIDgenerate(), Title= title, IndustryCode= industry_code, Output = output, ImpactEventType="IndustryOutput")
  
  #converting object to Json
  json_data <- toJSON(event_data, auto_unbox = TRUE, pretty = TRUE, na = "null")

  #making the post request to add the event to the project
  response <- POST(url, body = json_data, add_headers("Content-Type" = "application/json", "Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #converting from json to data frame
  json_content <- fromJSON(content)

  #returning the event
  return (json_content)
}

addCommodityOutput <- function(project, title, commodity_code, output){
  #making the URL to add an event to a project
  project_id = project["id"][[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/event")
  
  #getting the json token
  authorization_header <- getImplanAuth()
 
   #making the URL to add an event to a project
  event_data <- list(Id=UUIDgenerate(), Title= title, CommodityCode= commodity_code, Output = output, ImpactEventType="CommodityOutput")
  
  #converting object to Json
  json_data <- toJSON(event_data, auto_unbox = TRUE, pretty = TRUE, na = "null")
  
  #making the post request to add the event to the project
  response <- POST(url, body = json_data, add_headers("Content-Type" = "application/json", "Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #converting from json to data frame
  json_content <- fromJSON(content)
  
  #returning the event
  return (json_content)
}

addGroup <- function(project, title, region_card, dollar_year, events_for_group){
  #making the URL to add an group to a project
  project_id = project["id"][[1]]
 

  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/project/{project_id}/group")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #creating the list of group events to link events to the group
  group_events =  lapply(events_for_group, function(x) list(EventId = x["id"][[1]], scalingFactor = 1.0))
  
  #getting the hashId to map the group to the region card of the model 
  hash_id = region_card["hashId"][[1]]
  
  #creating the object to post to add a group to the project
  group_data <- list(Id=UUIDgenerate(), Title= title, DatasetId=data_set_id, DollarYear=dollar_year, HashId = hash_id, GroupEvents = group_events )
  
  #converting the object to Json
  json_data <- toJSON(group_data, auto_unbox = TRUE, pretty = TRUE, na = "null")

  #posting the object to add the group to the project
  response <- POST(url, body = json_data, add_headers("Content-Type" = "application/json", "Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #converting from Json to data frame
  json_content <- fromJSON(content)

  #returning the group
  return (json_content)
}


runProject <- function(project){
  #creating url to run the project
  project_id = project["id"][[1]]
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/{project_id}")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the post request to run the Impact
  response <- POST(url, add_headers("Content-Type" = "application/json", "Authorization" = authorization_header))
  
  #extracting the content
  content <- content(response, "text")
  
  #returning the runId
  return(as.integer(content))
}

waitForProjectRunToComplete <- function(runId){
  impact_complete = FALSE
  
  #creating url for getting impact status
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/status/{runId}")

  #getting the json token
  authorization_header <- getImplanAuth()
  
  #looping 90 times
  for (i in 1:90) {
    #making the get call to get the status of the Impact run
    response <- GET(url, add_headers(Authorization = authorization_header))
    
    #extracting the content from the response
    content <- content(response, "text")
    
    #checking to see if the response is complete
    impact_complete <- grepl("Complete", content) 
    
    #If complete we can stop looping
    if(impact_complete){
      break;
    }
    print("project not complete checking again in 10 seconds")
    #waiting for 10 seconds
    Sys.sleep(10)
  }
}

getSummaryEconomicIndiciators <- function(project, runId){
  #creating folder name to save results in
  projectTitle <- project["title"]
  folder_name <- glue("{projectTitle}-{runId}")
  folder_name <-  getResultsFile(folder_name)
  
  #making the URL to get results
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/results/SummaryEconomicIndicators/{runId}")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get the results
  response <- GET(url, add_headers(Authorization = authorization_header))
 
  #extracting the content
  content <- content(response, "text", encoding = "UTF-8")
  
  #if the folder doesn't exist create it
  if(file.exists(folder_name) == FALSE){
    dir.create(folder_name)
  }
  #creating file name to write results to
  fileName = glue("{folder_name}/summaryEconomicIndiciators.csv")
  
  #writing response to results
  writeLines(content, fileName)
}

getSummaryTaxes <- function(project, runId){
  #creating folder name to save results in
  projectTitle <- project["title"]
  folder_name <- glue("{projectTitle}-{runId}")
  folder_name <-  getResultsFile(folder_name)
  
  #making the URL to get results
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/results/SummaryTaxes/{runId}")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get the results
  response <- GET(url, add_headers(Authorization = authorization_header))
  
  #extracting the content
  content <- content(response, "text", encoding = "UTF-8")
  
  #if the folder doesn't exist create it
  if(file.exists(folder_name) == FALSE){
    dir.create(folder_name)
  }
  #creating file name to write results to
  fileName = glue("{folder_name}/summaryTaxes.csv")
  
  #writing response to results
  writeLines(content, fileName)
}

getDetailedTaxes <- function(project, runId){
  #creating folder name to save results in
  projectTitle <- project["title"]
  folder_name <- glue("{projectTitle}-{runId}")
  folder_name <-  getResultsFile(folder_name)
  
  #making the URL to get results
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/results/DetailedTaxes/{runId}")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get the results
  response <- GET(url, add_headers(Authorization = authorization_header))
  
  #extracting the content
  content <- content(response, "text", encoding = "UTF-8")
  
  #if the folder doesn't exist create it
  if(file.exists(folder_name) == FALSE){
    dir.create(folder_name)
  }
  
  #creating file name to write results to
  fileName = glue("{folder_name}/detailedTaxes.csv")
  
  #writing response to results
  writeLines(content, fileName)
}

getDetailEconomicIndicators <- function(project, runId){
  #creating folder name to save results in
  projectTitle <- project["title"]
  folder_name <- glue("{projectTitle}-{runId}")
  folder_name <-  getResultsFile(folder_name)
 
  #making the URL to get results
  url <- glue("{base_url_implan}{implan_env_path}/v1/impact/results/ExportDetailEconomicIndicators/{runId}")
  
  #getting the json token
  authorization_header <- getImplanAuth()
  
  #making the get call to get the results
  response <- GET(url, add_headers(Authorization = authorization_header))
  
  #extracting the content
  content <- content(response, "text", encoding = "UTF-8")
  
  #if the folder doesn't exist create it
  if(file.exists(folder_name) == FALSE){
    dir.create(folder_name)
  }
  
  #creating file name to write results to
  fileName = glue("{folder_name}/detailEconomicIndicators.csv")
  
  #writing response to results
  writeLines(content, fileName)
}