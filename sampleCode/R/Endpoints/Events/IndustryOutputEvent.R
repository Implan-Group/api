source(auth_env$Event)

# Define the IndustryOutputEvent class inheriting from Event
setClass(
  "IndustryOutputEvent",
  contains = "Event",
  slots = list(
    Output = "numeric",
    Employment = "numeric",
    EmployeeCompensation = "numeric",
    ProprietorIncome = "numeric",
    IndustryCode = "integer",
    DatasetId = "integer",
    MarginType = "character",
    Percentage = "numeric"
  ),
  prototype = list(
    ImpactEventType = "IndustryOutput", # Default value for inherited slot
    Output = NA_real_,
    Employment = NA_real_,  # Assuming these can be NA until assigned
    EmployeeCompensation = NA_real_,
    ProprietorIncome = NA_real_,
    IndustryCode = NA_integer_,
    DatasetId = NA_integer_,
    MarginType = NA_character_,
    Percentage = NA_real_
  )
)