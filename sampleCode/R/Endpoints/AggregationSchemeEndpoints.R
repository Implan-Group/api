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
