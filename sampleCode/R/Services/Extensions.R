setClass("Extensions",
         slots = list(
           dummy = "character"
         ))

# Create a generic function for Create
setGeneric("ThrowIfNull", function(object,value,valueName = deparse(substitute(object))) standardGeneric("ThrowIfNull"))

# Define a method for the Create function with the Projects class
setMethod("ThrowIfNull", signature = "Extensions", function(object,value,valueName = deparse(substitute(object))){
  
  if (!is.null(value)) {
    return(value)
  }
  warning(paste("ArgumentNullException:", valueName))
  return(NULL)
  
})

extension <- new("Extensions")
