source(auth_env$Rest)
source(auth_env$Extensions)

setClass("IndustryCode",
         slots = list(
           Id = "integer",
           Code = "integer",
           Description ="character"
         ))

setClass("IndustryCodeEndpoints",
         contains = "IndustryCode")

# Create a generic function for Create
setGeneric("GetIndustryCodes", function(object,aggregationSchemeId = NULL, industrySetId = NULL) standardGeneric("GetIndustryCodes"))

# Define a method for the Create function with the IndustryCodeEndpoints class
setMethod("GetIndustryCodes", signature = "IndustryCodeEndpoints", function(object,aggregationSchemeId = NULL, industrySetId = NULL){
  
  if(is.null(aggregationSchemeId)){
    IndustryCodesUrl <- "api/v1/IndustryCodes"
  }else{
    IndustryCodesUrl <- paste0("api/v1/IndustryCodes/",aggregationSchemeId)
  }
  
  if(!is.null(industrySetId)){
    IndustryCodesUrl <-  paste0(IndustryCodesUrl,"?industrySetId=",
                                industrySetId)
  }
  
  title <- class(object)
  
  industries <- ThrowIfNull(extension,GetResponseData(rest, url = IndustryCodesUrl, method_type = "GET", title_instances = title))
  return(industries)
  
  
})

