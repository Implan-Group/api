# Define the Event class
setClass(
  "Event",
  slots = list(
    ImpactEventType = "character",
    Title = "character",
    Id = "character",
    ProjectId = "character",
    Tags = "list"
  ),
  prototype = list(
    ImpactEventType = "Empty", # Default values
    Id = "00000000-0000-0000-0000-000000000000",
    ProjectId = "00000000-0000-0000-0000-000000000000",
    Tags = list()
  )
)