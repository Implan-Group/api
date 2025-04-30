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

convert_slots_into_list <- function(x){
  
  # Accessing slots of event1 as a list
  slot_names <- slotNames(x)
  slot_values <- lapply(slot_names, function(slot) slot(x, slot))
  
  # Convert to named list for easier viewing
  event_list_body <- as.list(setNames(slot_values, slot_names))
  
  # Print the event1_list
  print(event_list_body)
  
}

# Function to convert NA to NULL
convert_na_to_null <- function(x) {
  if (length(x) == 1 && is.na(x)) {
    return(NULL)
  } else {
    return(x)
  }
}


# handle_response <- function(response) {
#   # Check if the response is a JSON array or single string
#   if (startsWith(response, "[")) {
#     # Convert JSON array to R object (list)
#     response_list <- fromJSON(response)
#     
#     # Prettify JSON for display
#     pretty_json <- toJSON(response_list, pretty = TRUE)
#     
#   } else {
#     # # If not an array, assume it's a single string and wrap it in a JSON structure
#     # response_json <- toJSON(list(status = response), auto_unbox = TRUE)
#     # #pretty_json <- response_json
#     # pretty_json <- prettify(response_json)
#     
#     response_obj <- fromJSON(response)
#     response_json <- toJSON(response_obj, auto_unbox = TRUE,, pretty = TRUE)
#     pretty_json <- response_json
#   }
#   
#   return(pretty_json)
# }


handle_response <- function(response) {
  # Check if the response is a JSON array or a valid JSON object
  if (startsWith(response, "[") || startsWith(response, "{")) {
    # Convert JSON to R object (list or data frame)
    response_obj <- fromJSON(response)
    
    # Prettify JSON for display
    pretty_json <- toJSON(response_obj,auto_unbox = TRUE, pretty = TRUE)
    
  } else {
    # If not a valid JSON, assume it's a single string and log it as is
    pretty_json <- response
  }
  
  return(pretty_json)
}


AddGroupEvent_function <- function(x){
  GroupEvent <- GroupEvent(new("Event", eventId = x$id))
  return(GroupEvent)
}
