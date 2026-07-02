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



