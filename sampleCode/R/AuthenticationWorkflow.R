source(auth_env$Authentication)
source(auth_env$Rest)
source(auth_env$Iworkflow)

setClass("AuthenticationWorkflow",
         contains = "Iworkflow")

#setGeneric("Examples", function(object) standardGeneric("Examples"))

setMethod("Examples", signature = "AuthenticationWorkflow", function(object){
  
  # Create an instance of the Authentication class
  # !!! You must enter in your own username + password here !!!
  auth_instance <- new("Authentication",
                       Username = "",
                       Password = ""
  )
  
  # Call the GetBearerToken method on the auth_instance
  bearerToken <- GetBearerToken(auth_instance)
  
  #bearerToken <- auth_env$validated_token
  rest <- new("Rest")
  
  SetAuthentication(rest,bearerToken)
  
})
# auth_flow_instance <- new("AuthenticationWorkflow")
# Examples(auth_flow_instance)
