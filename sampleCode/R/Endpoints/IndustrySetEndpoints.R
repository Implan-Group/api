source(auth_env$Rest)
source(auth_env$Extensions)

# Define the Project class
setClass("IndustrySet",
         slots = list(
           Id = "integer",
           Description = "character",
           DefaultAggregationSchemeId = "integer",
           ActiveStatus = "logical",
           IsDefault = "logical",
           MapTypeId = "integer",
           IsNaicsCompatible = "logical"
         ))

setClass("IndustrySetEndpoints",
         contains = "IndustrySet")


# Create a generic function for Create
setGeneric("GetIndustrySet", function(object,industrySetId) standardGeneric("GetIndustrySet"))

# Define a method for the Create function with the IndustrySetEndpoints class
setMethod("GetIndustrySet", signature = "IndustrySetEndpoints", function(object,industrySetId){
  
  industry_url = paste0("api/v1/industry-sets/",industrySetId)
  
  title <- class(object)
  
  industries <- ThrowIfNull(extension,GetResponseData(rest, url = industry_url, method_type = "GET", title_instances = title))
  
  return(industries) 
  
})

# Create a generic function for Create
setGeneric("GetIndustrySets", function(object) standardGeneric("GetIndustrySets"))

# Define a method for the Create function with the IndustrySetEndpoints class
setMethod("GetIndustrySets", signature = "IndustrySetEndpoints", function(object){
  
  industry_url = "api/v1/industry-sets"
  
  title <- class(object)
  
  industries <- ThrowIfNull(extension,GetResponseData(rest, url = industry_url, method_type = "GET", title_instances = title))
  
  return(industries) 
  
})



