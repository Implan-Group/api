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
