setGeneric("Examples", function(object, ProjectId = NULL) {
  standardGeneric("Examples")
})

setClass(
  "Iworkflow",
  slots = list(
    dummy = "character"
  )
)

setMethod(
  "Examples", "Iworkflow",
  function(object, ProjectId = NULL) {
    #cat("This is the BaseClass method.\n")
  }
)
