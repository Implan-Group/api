source(auth_env$Rest)

setClass("AggregationScheme",
         slots = list(
           Id = "integer",
           Description = "character",
           IndustrySetId = "integer",
           HouseholdSetIds = "list",
           MapCode = "character",
           Status = "character"
           
         ))

setClass("AggregationSchemeEndpoints",
         contains = "AggregationScheme")

setGeneric("GetAggregationSchemes", function(object,IndustrySetId) standardGeneric("GetAggregationSchemes"))

setMethod("GetAggregationSchemes", "AggregationSchemeEndpoints", function(object,IndustrySetId) {
  
  industrySetId <- NA
  
  if(is.na(industrySetId)){
    industrySetId <- IndustrySetId
  }
  
  aggregation_url <- "api/v1/aggregationSchemes"
  
  aggregationSchemes_url = paste0(aggregation_url,"?industrySetId=",
                                  industrySetId)
  
  title <- class(object)
  
  schemes <- GetResponseData(rest, url = aggregationSchemes_url, method_type = "GET", title_instances = title)
  return(schemes) 
  
})