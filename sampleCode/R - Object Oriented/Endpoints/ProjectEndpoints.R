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
source(auth_env$Extensions)

# Define the Project class
setClass("Project",
         slots = list(
           Id = "character",
           Title = "character",
           AggregationSchemeId = "integer",
           HouseholdSetId = "integer",
           IsMrio = "logical",
           FolderId = "integer",
           LastImpactRunId = "integer"
         ))


# Define the ProjectEndpoints class which contains Project
setClass("ProjectEndpoints",
         contains = "Project")

# Create a generic function for Create
setGeneric("Create", function(object) standardGeneric("Create"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("Create", signature = "ProjectEndpoints", function(object){
  #url_object <- new("Rest", baseurl = auth_env$baseurl, lastSet = Sys.time())
  #url <- auth_env$createproject_url
  
  url <- "api/v1/impact/project"
  
  print(url)
  
  project_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  project_list_body <- lapply(project_list_body, convert_na_to_null)
  
  # Print the updated event1_list
  print(project_list_body)
  
  title <- class(object)
  
  # Make the POST request
  project_creation <- ThrowIfNull(extension,GetResponseData(rest, url = url, method_type = "POST", title_instances = title, response_body = project_list_body))
  
  return(project_creation)
})


# Create a generic function for Create
setGeneric("GetProject", function(object,ProjectId) standardGeneric("GetProject"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("GetProject", signature = "ProjectEndpoints", function(object,ProjectId){
  
  print(paste0("I came here with",ProjectId))

  GetProject_url <- paste0("api/v1/impact/project/",ProjectId)
  
  title <- class(object)

  GetProject <- ThrowIfNull(extension,GetResponseData(rest, url = GetProject_url, method_type = "GET",title_instances = title))

  return(GetProject)

})


# Create a generic function for Create
setGeneric("GetProjects", function(object) standardGeneric("GetProjects"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("GetProjects", signature = "ProjectEndpoints", function(object){

  GetProjects_url <- "api/v1/impact/project"
  
  title <- class(object)

  GetProjects <- ThrowIfNull(extension,GetResponseData(rest, url = GetProjects_url, method_type = "GET", title_instances = title))

  return(GetProjects)

})


# Create a generic function for Create
setGeneric("GetSharedProjects", function(object) standardGeneric("GetSharedProjects"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("GetSharedProjects", signature = "ProjectEndpoints", function(object){

  GetSharedProjects_url <- "api/v1/impact/project/shared"
  
  title <- class(object)

  GetSharedProjects <- ThrowIfNull(extension,GetResponseData(rest, url = GetSharedProjects_url, method_type = "GET", title_instances = title))

  return(GetSharedProjects)

})
