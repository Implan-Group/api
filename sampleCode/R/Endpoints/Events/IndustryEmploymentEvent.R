source(auth_env$Event)

setClass("IndustryEmploymentEvent",
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
           ImpactEventType = "IndustryEmployment" # Assigning default values
         ))