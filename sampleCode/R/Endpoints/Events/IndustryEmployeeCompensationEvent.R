source(auth_env$Event)

setClass("IndustryEmployeeCompensationEvent",
         contains = "Event",
         slots = list(
           Output = "numeric",
           Employment = "numeric",
           EmployeeCompensation = "numeric",
           ProprietorIncome = "numeric",
           IndustryCode = "integer",
           ImpactEventType = "character"
         ),
         prototype = list(
           ImpactEventType = "IndustryEmployeeCompensation" # Assigning default values
         ))