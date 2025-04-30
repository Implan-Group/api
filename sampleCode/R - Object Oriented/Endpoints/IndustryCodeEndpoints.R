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

