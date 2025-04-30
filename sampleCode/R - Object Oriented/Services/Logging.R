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

source(auth_env$CommonFunctions)

# Define the Logging class
setClass(
  "Logging",
  slots = list(
    stringBuilder = "character",
    logFilePath = "character"
  ),
  prototype = list(
    stringBuilder = "",
    logFilePath = ""
  )
)

# Method to initialize the Logging object
setGeneric("initializeLogging", function(.Object, logDir) standardGeneric("initializeLogging"))

setMethod("initializeLogging", "Logging", function(.Object, logDir) {
  .Object@stringBuilder <- ""
  
  if (!dir.exists(logDir)) {
    dir.create(logDir, recursive = TRUE)
  }
  
  fileName <- paste0("Log_", format(Sys.time(), "%d-%m-%Y %H-%M-%S"), ".txt")
  .Object@logFilePath <- file.path(logDir, fileName)
  
  return(.Object)
})

setGeneric("logRequestResponse", function(.Object, client, request, response, responseData, elapsedTime, instance = NULL, responseDataType = NULL) standardGeneric("logRequestResponse"))

setMethod("logRequestResponse", "Logging", function(.Object, client, request, response, responseData, elapsedTime, instance = NULL, responseDataType = NULL) {
  log <- .Object@stringBuilder
  
  log <- paste(log, "-------------", sep = "\n")
  log <- paste(log, sprintf("[%s]", format(Sys.time(), "%Y-%m-%d %H:%M:%S")), sep = "\n")
  
  method <- toupper(request$method)
  log <- paste(log, sprintf("Request: %s '%s'", method, buildUri(client, request)), sep = "\n")
  
  # Handle request parameters logging here if necessary
  if(class(response) == "httr2_response"){
    log <- paste(log, sprintf("Response: '%s' in %.1fms", resp_status(response),  as.numeric(elapsedTime)), sep = "\n")
    
    log <- paste(log, "", sep = "\n")
    
    log <- paste(log,"-Content: ", resp_headers(response)$`content-type`, "as", instance )
    
    log <- paste(log, "", sep = "\n")
    log <- paste(log, "", sep = "\n")
   
    
    # Check the response content type
    content <- response %>% resp_body_string()
    
    log <- paste(log,content)
    
    log <- paste(log, "", sep = "\n")
    
    
    
  }else{
    log <- paste(log, sprintf("Response: '%d %s' in %.1fms", status_code(response), response$status_code, as.numeric(elapsedTime)), sep = "\n")
    
    log <- paste(log, "", sep = "\n")
    
    content_type <- headers(response)$`content-type`
    
    # Split the string by the semicolon and take the first part
    content_type <- strsplit(content_type, ";")[[1]][1]
    
    
    log <- paste(log,"-Content: ", content_type , "as", instance)
    
    log <- paste(log, "", sep = "\n")
    log <- paste(log, "", sep = "\n")
    
    print(paste("my test response :  ", response))
    
    responses <- content(response, as = "text", encoding = "UTF-8")
    
    log <- paste(log,handle_response(responses))
    
    # Handle response logging here if necessary
    
    log <- paste(log, "", sep = "\n")
  }
  
  cat(log)
  
  write(log, file = .Object@logFilePath, append = TRUE)
  
  .Object@stringBuilder <- ""
  
  return(.Object)
})
