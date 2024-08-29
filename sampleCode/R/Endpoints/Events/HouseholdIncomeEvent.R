source(auth_env$Event)

# Define the HouseholdIncomeEvent class inheriting from Event

setClass("HouseholdIncomeEvent",
         contains = "Event",
         slots = list(
           HouseholdIncomeCode = "integer",
           Value = "numeric",
           ImpactEventType = "character"
         ),
         prototype = list(
           ImpactEventType = "HouseholdIncome"
         ))