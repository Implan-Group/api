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
