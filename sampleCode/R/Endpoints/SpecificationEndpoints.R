source(auth_env$Rest)
source(auth_env$Extensions)

setClass("Specification",
         slots = list(
           Name = "character",
           Code = "character"
         ))

setClass("SpecificationEndpoints",
         contains = "Specification")

# Create a generic function for Create
setGeneric("GetSpecifications", function(object, projectGuid, eventType) standardGeneric("GetSpecifications"))

# Define a method for the Create function with the SpecificationEndpoints class
setMethod("GetSpecifications", signature = "SpecificationEndpoints", function(object, projectGuid, eventType){
  
  url <- paste0("api/v1/impact/project/",projectGuid,"/eventtype/",eventType,"/specification")
  
  specifications <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET"))
  
  return(specifications)
  
})


householdIncomeSpecifications <- new("SpecificationEndpoints")

# !!! You will need your own Project's GUID to enter here !!!
print(GetSpecifications(householdIncomeSpecifications, as.character("4bc01909-BEEF-BEEF-af8a-2ad16d1dd50b"), "HouseholdIncome"))
