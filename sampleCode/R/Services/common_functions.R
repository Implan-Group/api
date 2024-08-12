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