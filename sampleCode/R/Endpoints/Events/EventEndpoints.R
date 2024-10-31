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
source(auth_env$Extensions)
source(auth_env$Event)
source(auth_env$IndustryOutputEvent)
source(auth_env$IndustryImpactAnalysisEvent)
source(auth_env$SpendingPatternValueType)
source(auth_env$HouseholdIncomeEvent)


setClass("EventEndpoints",
         contains = c("Event","IndustryOutputEvent","IndustryImpactAnalysisEvent"))


# Create a generic function for Create
setGeneric("GetEventsTypes", function(object,projectGuid) standardGeneric("GetEventsTypes"))

# Define a method for the Create function with the EventEndpoints class
setMethod("GetEventsTypes", signature = "EventEndpoints", function(object,projectGuid){
  
  url <- paste0("api/v1/impact/project/",projectGuid,"/eventtype")
  
  print(url)

  events <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "GET"))
  
  return(events) 
  
})

# Create a generic function for Create
setGeneric("GetEvent", function(object,projectGuid,eventGuid) standardGeneric("GetEvent"))

# Define a method for the Create function with the EventEndpoints class
setMethod("GetEvent", signature = "EventEndpoints", function(object,projectGuid,eventGuid){
  
  url <- paste0("api/v1/impact/project/",projectGuid,"/event/",eventGuid)
  
  print(url)
  
  events <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "GET"))
  
  return(events) 
  
})


# Create a generic function for Create
setGeneric("GetEvents", function(object,projectGuid) standardGeneric("GetEvents"))

# Define a method for the Create function with the EventEndpoints class
setMethod("GetEvents", signature = "EventEndpoints", function(object,projectGuid){
  
  url <- paste0("api/v1/impact/project/",projectGuid,"/event")
  
  print(url)
  
  events <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "GET"))
  
  return(events) 
  
})




# # Define a constructor for the Project class
# EventEndpoints <- function(Title, IndustryCode, Output){
#   new("IndustryOutputEvent",
#       Title = Title,
#       IndustryCode = IndustryCode,
#       Output = Output)
# }

# Create a generic function for Create
setGeneric("AddEvent", function(object,projectGuid) standardGeneric("AddEvent"))

# Define a method for the Create function with the IndustryOutputEvent class
setMethod("AddEvent", signature = "IndustryOutputEvent", function(object,projectGuid){
  
  print(object)
  url <- paste0("api/v1/impact/project/",projectGuid,"/event")
  
  print(url)
  
  event_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  event_list_body <- lapply(event_list_body, convert_na_to_null)
  
  # Print the updated event1_list
  print(event_list_body)
  
  add_event <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "POST", response_body = event_list_body))
  return(add_event) 
  
})


# Create a generic function for Create
#setGeneric("AddEvents", function(object,projectGuid) standardGeneric("AddEvents"))

# Define a method for the Create function with the IndustryImpactAnalysisEvent class
setMethod("AddEvent", signature = "IndustryImpactAnalysisEvent", function(object,projectGuid){
  
  print(object)
  url <- paste0("api/v1/impact/project/",projectGuid,"/event")
  
  print(url)
  
  event_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  event_list_body <- lapply(event_list_body, convert_na_to_null)
  
  # Print the updated event1_list
  print(event_list_body)
  
  add_event <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "POST", response_body = event_list_body))
  return(add_event) 
  
})



# Define a method for the Create function with the HouseholdIncomeEvent class
setMethod("AddEvent", signature = "HouseholdIncomeEvent", function(object,projectGuid){
  
  print(object)
  url <- paste0("api/v1/impact/project/",projectGuid,"/event")
  
  print(url)
  
  event_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  event_list_body <- lapply(event_list_body, convert_na_to_null)
  
  # Print the updated event1_list
  print(event_list_body)
  
  add_event <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "POST", response_body = event_list_body))
  return(add_event) 
  
})
