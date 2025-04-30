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
