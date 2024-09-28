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

# Define the S4 class
setClass("Event",
         slots = list(eventId = "character", scalingFactor = "numeric"))


# Define a method to convert an instance to a list
setGeneric("GroupEvent", function(object) standardGeneric("GroupEvent"))
setMethod("GroupEvent", "Event",
          function(object) {
            list(
              eventId = object@eventId,
              scalingFactor = 1
            )
          })


setClass("Group",
         contains = "Event",
         slots = list(
           Title = "character",
           Id = "character",
           ProjectId = "character",
           HashId = "character",
           Urid = "integer",
           UserModelId = "integer",
           ModelId = "integer",
           DollarYear = "integer",
           ScalingFactor = "numeric",
           DatasetId = "integer",
           GroupEvents = "list"
         ),
         prototype = list(
           Id =  "00000000-0000-0000-0000-000000000000",
           ScalingFactor = 1,
           GroupEvents = list()
         ))

setClass("GroupEndpoints",
         contains = "Group")

setGeneric("AddGroupToProject", function(object,projectGuid,group= NULL) standardGeneric("AddGroupToProject"))

# Define a method for the Create function with the GroupEndpoints class
setMethod("AddGroupToProject", signature = "GroupEndpoints", function(object,projectGuid,group = NULL){
  
  print(object)
  url <- paste0("api/v1/impact/project/",projectGuid,"/group")
  
  group_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  group_list_body <- lapply(group_list_body, convert_na_to_null)
  
  title <- class(object)
 
  AddGroup <- GetResponseData(rest, url = url, method_type = "POST", response_body = group_list_body,title_instances = title)
  return(AddGroup) 
  
})
