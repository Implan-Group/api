setClass("SpendingPatternCommodity",
         slots = list(
           Coefficient = "numeric",
           CommodityCode = "integer",
           CommodityDescription = "character",
           IsSamValue = "logical",
           IsUserCoefficient = "logical",
           LocalPurchasePercentage = "character"
         ),
         prototype = list(
           LocalPurchasePercentage = label_percent()(1) # Assigning default values as 100%
         ))