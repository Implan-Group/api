source(auth_env$Event)

setClass("IndustryImpactAnalysisEvent",
         contains = "Event",
         slots = list(
           IndustryCode = "integer",
           IntermediateInputs = "numeric",
           TotalEmployment = "numeric",
           EmployeeCompensation = "numeric",
           ProprietorIncome = "numeric",
           WageAndSalaryEmployment = "numeric",
           ProprietorEmployment = "numeric",
           TotalLaborIncome = "numeric",
           OtherPropertyIncome = "numeric",
           TaxOnProductionAndImports = "numeric",
           LocalPurchasePercentage = "numeric",
           TotalOutput = "numeric",
           IsSam = "logical",
           SpendingPatternDatasetId = "integer",
           SpendingPatternValueType = "character",
           SpendingPatternCommodities = "list",
           ImpactEventType = "character"
         ),
         ,
         prototype = list(
           LocalPurchasePercentage = 1, # Assigning default values as 100%
           SpendingPatternCommodities = list(),
           ImpactEventType = "IndustryImpactAnalysis",
           TotalOutput = NA_real_
         ))
