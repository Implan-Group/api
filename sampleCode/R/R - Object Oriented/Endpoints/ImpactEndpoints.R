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

#extension <- new("Extensions")

setClass("ImpactEndpoints",
         slots = list(
           impactRunId = "numeric"
         ))

# Create a generic function for Create
setGeneric("RunImpact", function(object,ProjectId) standardGeneric("RunImpact"))

# Define a method for the Create function with the ImpactEndpoints class
setMethod("RunImpact", signature = "ImpactEndpoints", function(object,ProjectId){
  
  RunImpact_url <- paste0("api/v1/impact/",ProjectId)
  
  title <- "Int64"
  
  impactRunId <- ThrowIfNull(extension,GetResponseData(rest, url = RunImpact_url, method_type = "POST", title_instances = title))
  
  print(paste0("my impact id is",impactRunId))
  return(impactRunId)
  
})


# Create a generic function for Create
setGeneric("GetImpactStatus", function(object,impactRunId) standardGeneric("GetImpactStatus"))

# Define a method for the Create function with the ImpactEndpoints class
setMethod("GetImpactStatus", signature = "ImpactEndpoints", function(object,impactRunId){
  
  GetImpactStatus_url <- paste0("api/v1/impact/status/",impactRunId)
  
  status <- ThrowIfNull(extension,GetResponseContent(rest, url = GetImpactStatus_url, method_type = "GET"))
  
  return(status)
  
})


# Define the generic method
setGeneric("CancelImpact", function(object, impactRunId) standardGeneric("CancelImpact"))

# Implement the method for the ImpactEndpoints class
setMethod("CancelImpact", signature = "ImpactEndpoints", function(object, impactRunId) {
  
  CancelImpact_url <- paste0("api/v1/impact/cancel/",impactRunId)
  
  result <- ThrowIfNull(extension,GetResponseContent(rest, url = CancelImpact_url, method_type = "PUT"))
  
  # Check if the result matches the expected cancellation message
  is_cancelled <- tolower(result) == tolower("Analysis run cancelled.")
  
  if(is_cancelled){
    return("Analysis run cancelled.")
  }
  
  
})
