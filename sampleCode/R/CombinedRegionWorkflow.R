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

source(auth_env$AggregationSchemeEndpoints)
source(auth_env$DataSetEndpoints)
source(auth_env$Iworkflow)

setClass("CombinedRegionWorkflow",
         contains = "Iworkflow",
         slots = list(
           dummy = "character"
         ))

# Create a generic function for Create
#setGeneric("Examples", function(object) standardGeneric("Examples"))

# Define a method for the Create function with the Projects class
setMethod("Examples", signature = "CombinedRegionWorkflow", function(object){
  
  AllSchemes <- new("AggregationSchemeEndpoints")
  aggregationSchemes <- GetAggregationSchemes(AllSchemes,IndustrySetId=8)
  
  aggregationSchemeId = 8  # 8 = Implan 546 Unaggregated
  
  datasets_instance <- new("DataSetEndpoints")
  
  datasets <- GetDataSets(datasets_instance,aggregationSchemeId)
  
  dataSetId = 96; # 96 = 2022 Data
  
  #Call RegionalWorkflow
  source(auth_env$RegionalWorkflow)
  
  regionTypes_instance <- new("RegionEndpoints")
  
  regions <- GetRegionChildren(regionTypes_instance,aggregationSchemeId, dataSetId, regionType = "County")
  
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
  
  print(descriptionToRegionDict[[tolower("Autauga County, AL")]])
  # Access and print a value to demonstrate retrieval
  hashId1 = descriptionToRegionDict[[tolower("Autauga County, AL")]]$hashId
  
  hashId2 = descriptionToRegionDict[[tolower("Baldwin County, AL")]]$hashId
  
  print(paste0("my Hash_id is",hashId1 , hashId2))
  
  combineRegionPayload_instance <- new("CombineRegionRequest",
                                       Description = paste0("Combined Region -",format(Sys.time(), "%Y%m%d_%H%M%S")),
                                       HashIds = list(hashId1,hashId2)
                                       #Urids = list()
                                       )
  
  combinedRegion <- CombineRegions(combineRegionPayload_instance,aggregationSchemeId = aggregationSchemeId)
  
  combinedRegion <- fromJSON(combinedRegion)
  
  print(paste0("combinedRegion_aggid is",combinedRegion$aggregationSchemeId, "and ", "datasetid", combinedRegion$datasetId ))
  
  
  # Simulating do-while(TRUE)
  repeat {
    
    userRegions = GetUserRegions(regionTypes_instance,combinedRegion$aggregationSchemeId, combinedRegion$datasetId)
    
    region <- userRegions[userRegions$hashId == combinedRegion$hashId,]
    
    print(region)
    print(region$modelBuildStatus)
    
    if(!is.null(region$modelBuildStatus)){
      
      if (tolower(region$modelBuildStatus) == tolower("Complete")) {
        print("ModelBuildStatus is Completed")
        break
      }
      
    }
    
    
    Sys.sleep(30)
  }
  
  
})

combined_instance <- new("CombinedRegionWorkflow")
print(Examples(combined_instance))
