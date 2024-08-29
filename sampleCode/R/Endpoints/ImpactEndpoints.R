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