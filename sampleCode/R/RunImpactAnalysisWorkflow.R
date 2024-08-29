source(auth_env$ProjectEndpoints)
source(auth_env$ImpactEndpoints)
source(auth_env$ImpactResultEndpoints)
source(auth_env$Iworkflow)


setClass("RunImpactAnalysisWorkflow",
         contains = "Iworkflow",
         slots = list(
           ProjectId = "character"
         ),
         prototype = list(
           ProjectId = ""
         ))

# Create a generic function for Create
#setGeneric("Examples", function(object,ProjectId) standardGeneric("Examples"))

# Define a method for the Create function with the ProjectEndpoints class
setMethod("Examples", signature = "RunImpactAnalysisWorkflow", function(object,ProjectId){
  
  projects_instance <- new("ProjectEndpoints")
  
  projects = GetProjects(projects_instance)
  
  shared = GetSharedProjects(projects_instance)
  
  print(ProjectId)
  project = GetProject(projects_instance,ProjectId = ProjectId)
  
  print(project)
  
  impactRun_instance <- new("ImpactEndpoints")
  
  impactRunId <- RunImpact(impactRun_instance,ProjectId)
  
  print(paste0("impact id is",impactRunId))
  
  while (TRUE) {
    # Get the current status
    status <- GetImpactStatus(impactRun_instance,impactRunId)

    print(status)
    
    if(!is.null(status)){
      # If it is 'Complete', then results can be queried
      if (tolower(status) == tolower("Complete")) {
        break
      }
    }

    

    # If it has not yet completed, give it more time to process
    Sys.sleep(10)  # Sleep for 10 seconds
  }

  ImpactResults_instance <- new("CsvReports")
  
  detailedEconomicIndicators <- GetDetailedEconomicIndicators(ImpactResults_instance,impactRunId)
  print(detailedEconomicIndicators)
  
  summaryEconomicIndicators <- GetSummaryEconomicIndicators(ImpactResults_instance,impactRunId)
  print(summaryEconomicIndicators)
  
  detailedTaxes <- GetDetailedTaxes(ImpactResults_instance,impactRunId)
  print(detailedTaxes)
  
  summaryTaxes <- GetSummaryTaxes(ImpactResults_instance,impactRunId)
  print(summaryTaxes)
  
  estimatedGrowthPercentageFilter <- new("EstimatedGrowthPercentageFilter",
                                         DollarYear = as.integer(2024),
                                         Regions = list(),
                                         Impacts = list(),
                                         GroupNames = list(),
                                         EventNames = list(),
                                         EventTags = list()
                                         )

  estimatedGrowthPercentage <- GetEstimatedGrowthPercentage(estimatedGrowthPercentageFilter,impactRunId = impactRunId)
  print(estimatedGrowthPercentage)
  
})
