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
source(auth_env$Logging)

setClass("Rest",
         slots = list(lastSet = "POSIXct")
)

# Define a generic function for Rest
setGeneric("Rest", function(object) standardGeneric("Rest"))

# Define a method for the Rest function with the Rest class
setMethod("Rest", signature(object = "Rest"), function(object){
  BaseUrl <- "https://api.implan.com/"
  return(BaseUrl)
})


setGeneric("buildUri", function(object, request) standardGeneric("buildUri"))

setMethod("buildUri", signature(object = "Rest"), function(object, request){
  # Assuming request contains the relative URL path
  return(paste0(auth_env$baseurl, request$url))
})



# Define a generic function for ThrowOnError
setGeneric("ThrowOnError", function(object, response) standardGeneric("ThrowOnError"))

# Define a method for the ThrowOnError function with the Rest class
setMethod("ThrowOnError", signature(object = "Rest"), function(object, response){
  
  if (response$status_code >= 200 && response$status_code < 300 &&
      is.null(response$error_exception) &&
      is.null(response$error_message)) {
    return(invisible(NULL))
  }
  
  ex <- if (!is.null(response$error_exception)) {
    response$error_exception
  } else {
    simpleError("Rest Request Failed")
  }
  
  stop(ex)
  
})

setGeneric("SetAuthentication", function(object, token) standardGeneric("SetAuthentication"))

setMethod("SetAuthentication", signature = "Rest", function(object, token){
  
  tryCatch({
    # Validating a bearer token by ensuring it's not empty and starts with the word "Bearer"
    if (nzchar(token) && startsWith(token, "Bearer")) {
      print("Token Validation Success")
      auth_env$validated_token <- token
      # Set the lastSet time to the current time
      object@lastSet <- Sys.time()
    } else {
      stop("Token Validation Failed")
    }
  },
  error = function(e) {
    print(paste("Error:", e$message))
  })
  
  return(auth_env$validated_token)
})

# Create a Logging instance and initialize it
logDir <- auth_env$logDir
logging <- new("Logging")
logging <- initializeLogging(logging, logDir)

setGeneric("GetResponseContent", function(object, url, method_type, response_body = NULL) standardGeneric("GetResponseContent"))

setMethod("GetResponseContent", signature = "Rest", function(object, url, method_type, response_body = NULL){
  
  rest <- new("Rest")
  validation <- auth_env$validated_token
  
  validated_token <- SetAuthentication(rest, validation)
  print(validated_token) 
  
  urls <- url
  url <- paste0(auth_env$baseurl, urls)
  print(url)
  
  start_time <- Sys.time()
  
  response <- tryCatch({
    switch(method_type,
           GET = GET(
             url,
             add_headers(Authorization = validated_token),
             timeout(90)
           ),
           POST = POST(
             url,
             add_headers(Authorization = validated_token),
             body = response_body,
             encode = "json"
           ),
           PUT = PUT(
             url,
             add_headers(Authorization = validated_token)
           ),
           GET_BODY = 
             #Send the GET request with headers and JSON body
             response <- request(url) %>%
               req_method("GET") %>%
               req_headers(
                 Authorization = validated_token,
                 `Content-Type` = "application/json"
               ) %>%
               req_body_raw(response_body) %>%
               req_perform()
           ,
           stop("Invalid Request Method type: ", method_type)
    )
  }, error = function(e) {
    list(status_code = 500, error_exception = e, error_message = e$message)
    
  })
  
  end_time <- Sys.time()
  elapsed_time <- as.numeric(difftime(end_time, start_time, units = "secs"))
  
  # Log the request and response
  request <- list(method = method_type, url = urls)  # Adjust request structure as needed
  logRequestResponse(logging, client = rest, request = request, response = response, responseData = response_body, elapsedTime = elapsed_time)
  
  # if (is.list(response) && response$status_code == 500) {
  #   stop("Request failed with error: ", response$error_message)
  # }
  
  if (!is.null(response$error_exception)) {
    warning("Request failed with error: ", response$error_message)
    return(NULL)
  }
  
  if(class(response) == "httr2_response"){
    
    if(resp_status(response)== 200){
      
      data <- response %>% resp_body_string()
      return(data)
      
    }else {
      warning("Request failed with status code: ", status_code(response))
      return(NULL)
    }
    
  }else{
    
    if (status_code(response) == 200) {
      
      data <- content(response, as = "text", encoding = "UTF-8")
      return(data)
    } else {
      warning("Request failed with status code: ", status_code(response))
      return(NULL)
    }
    
  }
  
  
})

setGeneric("GetResponseData", function(object, url, method_type, title_instances = NULL, response_body = NULL) standardGeneric("GetResponseData"))

setMethod("GetResponseData", signature = "Rest", function(object, url, method_type, title_instances = NULL, response_body = NULL){
  
  rest <- new("Rest")
  validation <- auth_env$validated_token
  
  validated_token <- SetAuthentication(rest, validation)
  print(validated_token) 
  
  urls <- url
  url <- paste0(auth_env$baseurl, urls)
  print(url)
  
  start_time <- Sys.time()
  
  response <- tryCatch({
    switch(method_type,
           GET = GET(
             url,
             add_headers(Authorization = validated_token),
             timeout(90)
           ),
           POST = POST(
             url,
             add_headers(Authorization = validated_token),
             body = response_body,
             encode = "json"
           ),
           stop("Invalid Request Method type: ", method_type)
    )
  }, error = function(e) {
    list(status_code = 500, error_exception = e, error_message = e$message)
    
  })
  
  end_time <- Sys.time()
  elapsed_time <- as.numeric(difftime(end_time, start_time, units = "secs"))
  
  # Log the request and response
  request <- list(method = method_type, url = urls)  # Adjust request structure as needed
  logRequestResponse(logging, client = rest, request = request, response = response, responseData = response_body, elapsedTime = elapsed_time, instance = title_instances)
  
  # if (is.list(response) && response$status_code == 500) {
  #   stop("Request failed with error: ", response$error_message)
  # }
  
  if (!is.null(response$error_exception)) {
    warning("Request failed with error: ", response$error_message)
    return(NULL)
  }
  
  if (status_code(response) == 200) {
    data <- fromJSON(content(response, as = "text", encoding = "UTF-8"))
    return(data)
  } else {
    warning("Request failed with status code: ", status_code(response))
    return(NULL)
  }
})

rest <- new("Rest")
