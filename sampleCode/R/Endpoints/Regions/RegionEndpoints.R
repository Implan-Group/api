source(auth_env$Rest)
source(auth_env$Extensions)
source(auth_env$CommonFunctions)
source(auth_env$Region)
source(auth_env$CombineRegionRequest)


setClass("RegionEndpoints",
         contains = "Region" )

# Create a generic function for Create
setGeneric("GetRegionTypes", function(object) standardGeneric("GetRegionTypes"))

# Define a method for the Create function with the RegionEndpoints class
setMethod("GetRegionTypes", signature = "RegionEndpoints", function(object){
  
  regions_url <- "api/v1/region/RegionTypes"
  
  regions <- ThrowIfNull(extension,GetResponseData(rest, url = regions_url, method_type = "GET"))
  
  return(regions) 
})


# Create a generic function for Create
setGeneric("GetTopLevelRegion", function(object,aggregationSchemeId,dataSetId) standardGeneric("GetTopLevelRegion"))

# Define a method for the Create function with the RegionEndpoints class
setMethod("GetTopLevelRegion", signature = "RegionEndpoints", function(object,aggregationSchemeId,dataSetId){
  
  TopLevelRegion_url <- paste0("api/v1/region/",aggregationSchemeId,"/",dataSetId)
  
  print(TopLevelRegion_url)
  
  TopLevelRegion <- ThrowIfNull(extension,GetResponseData(rest, url = TopLevelRegion_url, method_type = "GET"))
  
  return(TopLevelRegion) 
  
})


# Create a generic function for Create
setGeneric("GetRegion", function(object,aggregationSchemeId,dataSetId,hashIdOrUrid) standardGeneric("GetRegion"))

# Define a method for the Create function with the RegionEndpoints class
setMethod("GetRegion", signature = "RegionEndpoints", function(object,aggregationSchemeId,dataSetId,hashIdOrUrid){
  
  TopLevelRegion_url <- paste0("api/v1/region/",aggregationSchemeId,"/",dataSetId,"/",hashIdOrUrid)
  
  print(TopLevelRegion_url)
  
  TopLevelRegion <- ThrowIfNull(extension,GetResponseData(rest, url = TopLevelRegion_url, method_type = "GET"))
  
  return(TopLevelRegion) 
  
})


# Create a generic function for Create
setGeneric("GetRegionChildren", function(object,aggregationSchemeId,dataSetId,hashIdOrUrid = NULL,regionType = NULL) standardGeneric("GetRegionChildren"))

# Define a method for the Create function with the RegionEndpoints class
setMethod("GetRegionChildren", signature = "RegionEndpoints", function(object,aggregationSchemeId,dataSetId,hashIdOrUrid = NULL,regionType = NULL){
  
  if(!is.null(hashIdOrUrid)){
    
    RegionChildren_url <- paste0("api/v1/region/",aggregationSchemeId,"/",dataSetId,"/",hashIdOrUrid,"/children")
    print(RegionChildren_url)
      
  }else{
    
    RegionChildren_url <- paste0("api/v1/region/",aggregationSchemeId,"/",dataSetId,"/children")
    print(RegionChildren_url)
    
  }
  
  if(!is.null(regionType)){
    
    RegionChildren_url <-  paste0(RegionChildren_url,"?regionTypeFilter=",
                                  regionType)
  }
  
  title <- class(object)
  
  RegionChildren <- ThrowIfNull(extension,GetResponseData(rest, url = RegionChildren_url, method_type = "GET", title_instances = title))
  
  return(RegionChildren) 
})

# Create a generic function for Create
setGeneric("GetUserRegions", function(object,aggregationSchemeId,dataSetId) standardGeneric("GetUserRegions"))

# Define a method for the Create function with the RegionEndpoints class
setMethod("GetUserRegions", signature = "RegionEndpoints", function(object,aggregationSchemeId,dataSetId){
  
  UserRegions_url <- paste0("api/v1/region/",aggregationSchemeId,"/",dataSetId,"/user")
  
  print(UserRegions_url)
  
  UserRegions <- ThrowIfNull(extension,GetResponseData(rest, url = UserRegions_url, method_type = "GET"))
  
  return(UserRegions) 
  
})


# Create a generic function for Create
setGeneric("CombineRegions", function(object,aggregationSchemeId) standardGeneric("CombineRegions"))

# Define a method for the Create function with the CombineRegionRequest class
setMethod("CombineRegions", signature = "CombineRegionRequest", function(object,aggregationSchemeId){
  
  CombineRegions_url <- paste0("api/v1/region/build/combined/",aggregationSchemeId)
  
  print(CombineRegions_url)
  
  regions_list_body <- convert_slots_into_list(object)
  
  # Convert NA to NULL in event1_list
  regions_list_body <- lapply(regions_list_body, convert_na_to_null)
  
  # Print the updated event1_list
  print(regions_list_body)
  
  regions <- ThrowIfNull(extension,GetResponseData(rest, url = CombineRegions_url, method_type = "POST",response_body = regions_list_body))
  
  
  regions <- toJSON(regions)
  
  print(paste0("length of the regions is",regions))
  
  print(length(regions))
  
  if(length(regions) != 1){
    stop("Unreachable code reached: The length of regions is not equal to 1.")
  }
  
  region <- regions[1]
  
  return(region) 
  
})

  