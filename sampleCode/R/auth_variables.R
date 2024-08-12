# Creates a new R environment if it doesn't exist already
# File Paths will be stored and accessed via this environment.

if (!exists("auth_env")){
  
  # !!! Be sure to change this Path to the location where these files are stored on your local machine !!!
  path <- "C:\\git\\api\\sampleCode\\R"
  
  auth_env <- new.env()
  auth_env$baseurl <- "https://api.implan.com/beta/"
  auth_env$lastset <- Sys.time()
  auth_env$token <- NA
  auth_env$validated_token <- NA
  auth_env$AuthVariable <- file.path(path, "auth_variables.R")
  auth_env$logDir <- file.path(path, "Final_Code\\Logs")
  auth_env$AuthenticationWorkflow <- file.path(path, "AuthenticationWorkflow.R")
  auth_env$CreateProjectWorkflow <- file.path(path, "CreateProjectWorkflow.R")
  auth_env$CombinedRegionWorkflow <- file.path(path, "CombinedRegionWorkflow.R")
  auth_env$RunImpactAnalysisWorkflow <- file.path(path, "RunImpactAnalysisWorkflow.R")
  auth_env$Authentication <- file.path(path, "Endpoints\\Authentication.R")
  auth_env$Rest <- file.path(path, "Services\\Rest.R")
  auth_env$AggregationSchemeEndpoints <- file.path(path, "Endpoints\\AggregationSchemeEndpoints.R")
  auth_env$DataSetEndpoints <- file.path(path, "Endpoints\\DataSetEndpoints.R")
  auth_env$RegionalWorkflow <- file.path(path, "RegionalWorkflow.R")
  auth_env$ProjectEndpoints <- file.path(path, "Endpoints\\ProjectEndpoints.R")
  auth_env$IndustrySetEndpoints <- file.path(path, "Endpoints\\IndustrySetEndpoints.R")
  auth_env$IndustryCodeEndpoints <- file.path(path, "Endpoints\\IndustryCodeEndpoints.R")
  auth_env$EventEndpoints <- file.path(path, "Endpoints\\Events\\EventEndpoints.R")
  auth_env$RegionEndpoints <- file.path(path, "Endpoints\\Regions\\RegionEndpoints.R")
  auth_env$GroupEndpoints <- file.path(path, "Endpoints\\GroupEndpoints.R")
  auth_env$ImpactEndpoints <- file.path(path, "Endpoints\\ImpactEndpoints.R")
  auth_env$ImpactResultEndpoints <- file.path(path, "Endpoints\\ImpactResultEndpoints.R")
  auth_env$CommonFunctions <- file.path(path, "Services\\common_functions.R")
  auth_env$Logging <- file.path(path, "Services\\Logging.R")
  auth_env$Extensions <- file.path(path, "Services\\Extensions.R")
  auth_env$Iworkflow <- file.path(path, "IWorkflow.R")
  auth_env$Event <- file.path(path, "Endpoints\\Events\\Event.R")
  auth_env$IndustryOutputEvent <- file.path(path, "Endpoints\\Events\\IndustryOutputEvent.R")
  auth_env$IndustryImpactAnalysisEvent <- file.path(path, "Endpoints\\Events\\IndustryImpactAnalysisEvent.R")
  auth_env$SpendingPatternValueType <- file.path(path, "Endpoints\\Events\\SpendingPatternValueType.R")
  auth_env$HouseholdIncomeEvent <- file.path(path, "Endpoints\\Events\\HouseholdIncomeEvent.R")
  auth_env$Region <- file.path(path, "Endpoints\\Regions\\Region.R")
  auth_env$CombineRegionRequest <- file.path(path, "Endpoints\\Regions\\CombineRegionRequest.R")
  auth_env$SpecificationEndpoints <- file.path(path, "Endpoints\\SpecificationEndpoints.R")
  auth_env$MultiEventToMultiGroupWorkflow <- file.path(path, "MultiEventToMultiGroupWorkflow.R")
}