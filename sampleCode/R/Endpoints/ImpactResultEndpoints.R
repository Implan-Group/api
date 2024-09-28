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
source(auth_env$CommonFunctions)


setClass("ImpactResultEndpoints",
         slots = list(
           dummy = "character"
         ))

setClass("CsvReports",
         contains = "ImpactResultEndpoints")

# Create a generic function for Create
setGeneric("GetDetailedEconomicIndicators", function(object,impactRunId) standardGeneric("GetDetailedEconomicIndicators"))

# Define a method for the Create function with the CsvReports class
setMethod("GetDetailedEconomicIndicators", signature = "CsvReports", function(object,impactRunId){
  
  url <- paste0("api/v1/impact/results/ExportDetailEconomicIndicators/",impactRunId)
  
  csv <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET"))
  
  return(csv)
  
  
})


# Create a generic function for Create
setGeneric("GetSummaryEconomicIndicators", function(object,impactRunId) standardGeneric("GetSummaryEconomicIndicators"))

# Define a method for the Create function with the CsvReports class
setMethod("GetSummaryEconomicIndicators", signature = "CsvReports", function(object,impactRunId){
  
  url <- paste0("api/v1/impact/results/SummaryEconomicIndicators/",impactRunId)
  
  csv <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET"))
  
  return(csv)
  
})


# Create a generic function for Create
setGeneric("GetDetailedTaxes", function(object,impactRunId) standardGeneric("GetDetailedTaxes"))

# Define a method for the Create function with the CsvReports class
setMethod("GetDetailedTaxes", signature = "CsvReports", function(object,impactRunId){
  
  url <- paste0("api/v1/impact/results/DetailedTaxes/",impactRunId)
  
  csv <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET"))
  
  return(csv)
  
})


# Create a generic function for Create
setGeneric("GetSummaryTaxes", function(object,impactRunId) standardGeneric("GetSummaryTaxes"))

# Define a method for the Create function with the CsvReports class
setMethod("GetSummaryTaxes", signature = "CsvReports", function(object,impactRunId){
  
  url <- paste0("api/v1/impact/results/SummaryTaxes/",impactRunId)
  
  csv <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET"))
  
  return(csv)
  
})

setClass("EstimatedGrowthPercentageFilter",
         slots = list(
           DollarYear = "integer",
           Regions = "list",
           Impacts = "list",
           GroupNames = "list",
           EventNames = "list",
           EventTags = "list"
         ), 
         prototype = list(
           Regions = list(),
           Impacts = list(),
           GroupNames = list(),
           EventNames = list(),
           EventTags = list()
         ))

# Create a generic function for Create
setGeneric("GetEstimatedGrowthPercentage", function(object,impactRunId) standardGeneric("GetEstimatedGrowthPercentage"))

# Define a method for the Create function with the CsvReports class
setMethod("GetEstimatedGrowthPercentage", signature = "EstimatedGrowthPercentageFilter", function(object,impactRunId){

  url <- paste0("api/v1/impact/results/EstimatedGrowthPercentage/",impactRunId)
  
  print(url)
  
  growth_list_body <- convert_slots_into_list(object)
  
  # Convert JSON body to JSON format
  json_body_str <- toJSON(growth_list_body, auto_unbox = TRUE)
  
  print(json_body_str)
  
  response <- ThrowIfNull(extension,GetResponseContent(rest, url = url, method_type = "GET_BODY", response_body = json_body_str))
  
  return(response)

})
