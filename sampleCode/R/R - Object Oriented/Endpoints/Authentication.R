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

source(auth_env$AuthVariable)
source(auth_env$Rest)

# Define the ImplanAuthentication class
setClass("ImplanAuthentication",
         slots = list(
           Username = "character",
           Password = "character"
         ))


# Define the Authentication class containing ImplanAuthentication
setClass("Authentication",
         contains = "ImplanAuthentication")


# Create a generic function for GetBearerToken
setGeneric("GetBearerToken", function(object) standardGeneric("GetBearerToken"))

# Define a method for the GetBearerToken function with the Authentication class
setMethod("GetBearerToken", signature(object = "Authentication"), function(object){
  auth <- "auth"
  
  rest <- new("Rest")
  
  base_rest_url <- Rest(rest)
  
  auth_url <- paste0(base_rest_url,auth)
  
  response <- httr::POST(
    auth_url,
    body = list(
      Username = object@Username,
      Password = object@Password
    ),
    encode = "json"
  )
  
  print(response)
  
  if (httr::status_code(response) == 200) {
    token <- httr::content(response, "parsed", encoding = "UTF-8")  # Adjust based on actual response structure
    
    # Check whether the token value is null IsNullOrWhiteSpace()
    if (nzchar(token) == FALSE) {
      stop("Cannot currently Authenticate to Impact Api")
    }
    
    return(token)
  } else {
    # Stops if status_code is not success
    stop("Cannot currently Authenticate to Impact Api: ", httr::status_code(response))
  }
})
