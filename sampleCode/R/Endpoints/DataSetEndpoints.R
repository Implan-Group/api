source(auth_env$Rest)
source(auth_env$Extensions)


setClass("DataSet",
         slots = list(
           Id = "integer",
           Description = "character",
           IsDefault = "logical"
         ))
setClass("DataSetEndpoints",
         contains = "DataSet")

# Create a generic function for Create
setGeneric("GetDataSets", function(object,aggregationSchemeId) standardGeneric("GetDataSets"))

# Define a method for the Create function with the DataSetEndpoints class
setMethod("GetDataSets", signature = "DataSetEndpoints", function(object,aggregationSchemeId){
  
  DataSets_url = paste0("api/v1/datasets/",aggregationSchemeId)
  
  print(DataSets_url)
  
  Data <- ThrowIfNull(extension,GetResponseData(rest, url = DataSets_url, method_type = "GET"))
  return(Data) 
  
})
