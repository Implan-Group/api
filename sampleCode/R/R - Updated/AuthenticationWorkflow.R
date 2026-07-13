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

# This workflow logs into the IMPLAN API using your credentials and stores
# the resulting bearer token so all other API calls can use it automatically.

source(auth_env$Authentication)
source(auth_env$Rest)
source(auth_env$Iworkflow)

# Define the AuthenticationWorkflow class.
setClass("AuthenticationWorkflow",
         contains = "Iworkflow")

# Define what happens when Examples() is called on an AuthenticationWorkflow object.
setMethod("Examples", signature = "AuthenticationWorkflow", function(object) {

# !! REQUIRED: Replace the empty strings below with your IMPLAN credentials !!
# Do this before running anything else.
  auth_instance <- new("Authentication",
                       Username = username,  # Email address for your IMPLAN account
                       Password = password   # Password for your IMPLAN account
  )

 
  # Send the login request to the IMPLAN API.
  bearerToken <- GetBearerToken(auth_instance)

  # Create a Rest service object, which manages HTTP communication with the API.
  rest <- new("Rest")

  # Store the bearer token in the shared Rest service so all future API calls
   SetAuthentication(rest, bearerToken)

  # Confirm successful authentication to the console
  message("Authentication successful. Bearer token stored and ready to use.")
})
