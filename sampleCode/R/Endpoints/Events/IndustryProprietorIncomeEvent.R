source(auth_env$Event)

setClass("IndustryProprietorIncomeEvent",
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
           ImpactEventType = "IndustryProprietorIncome" # Assigning default values
         ))
