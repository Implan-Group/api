source(auth_env$RegionEndpoints)

setClass("RegionalWorkflow",
         contains = "Iworkflow",
          slots = list(
            dummy = "character"
            ))
  
# Create a generic function for Create
#setGeneric("Examples", function(object) standardGeneric("Examples"))

# Define a method for the Create function with the Projects class
setMethod("Examples", signature = "RegionalWorkflow", function(object){
  
  aggregationSchemeId = 8;    # Implan 546 Unaggregated
  dataSetId = 96;             # 2022
  
  regionTypes_instance <- new("RegionEndpoints")
  
  regionTypes <- GetRegionTypes(regionTypes_instance)
  
  print(regionTypes)
  
  topLevelRegion <- GetTopLevelRegion(regionTypes_instance,aggregationSchemeId, dataSetId)
  
  print(topLevelRegion)
  
  childRegions <- GetRegionChildren(regionTypes_instance,aggregationSchemeId, dataSetId)
  
  print(childRegions)
  
  #Note user region url is throwing 503 response
  userRegions <- GetUserRegions(regionTypes_instance,aggregationSchemeId, dataSetId)
  
  print(userRegions)
  
  regions <- GetRegionChildren(regionTypes_instance,aggregationSchemeId, dataSetId, regionType = "State")
  
  regions
  
  #Convert to dictionary-----------------------

  regions <- as.list(as.data.frame(regions))
  
  # Initialize an empty named list
  descriptionToRegionDict <- list()
  
  # Iterate over each item in the parsed data list
  for (i in seq_along(regions$description)) {
    # Create a temporary list for each region's data
    item <- list(
      hashId = regions$hashId[i],
      urid = regions$urid[i],
      description = regions$description[i],
      modelId = regions$modelId[i],
      modelBuildStatus = regions$modelBuildStatus[i],
      employment = regions$employment[i],
      output = regions$output[i],
      valueAdded = regions$valueAdded[i],
      aggregationSchemeId = regions$aggregationSchemeId[i],
      datasetId = regions$datasetId[i],
      datasetDescription = regions$datasetDescription[i],
      fipsCode = regions$fipsCode[i],
      regionType = regions$regionType[i],
      hasAccessibleChildren = regions$hasAccessibleChildren[i],
      regionTypeDescription = regions$regionTypeDescription[i],
      geoId = regions$geoId[i],
      isMrioAllowed = regions$isMrioAllowed[i]
    )
    
    # Use the description (converted to lowercase) as the key
    descriptionToRegionDict[[tolower(item$description)]] <- item
  }
  
  # Access and print a value to demonstrate retrieval
  ohio = descriptionToRegionDict[[tolower("Ohio")]]
  
  northCarolina = descriptionToRegionDict[[tolower("North Carolina")]]
  
  northCarolina
  
})

region_instcance <- new("RegionalWorkflow")

Examples(region_instcance)