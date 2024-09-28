# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
