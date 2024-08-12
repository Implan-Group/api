# !!! Just like in 'auth_variables.R', replace this pathwith the location where these files are stored on your local machine !!!
path <- "C:\\git\\api\\sampleCode\\R"

#Load the required Packages
source(file.path(path, "LoadPackages.R"))

#Load the required file Paths and base url
source(file.path(path, "auth_variables.R"))

##Authentication Workflow
source(auth_env$AuthenticationWorkflow)
auth_flow_instance <- new("AuthenticationWorkflow")
Examples(auth_flow_instance)

# ##CreateProject Workflow
# source(auth_env$CreateProjectWorkflow)
# CreateProject_instance <- new("CreateProjectWorkflow")
# Examples(CreateProject_instance)


##MultiEventToMultiGroup Workflow
source(auth_env$MultiEventToMultiGroupWorkflow)
MultiEventToMultiGroupWorkflow_instance <- new("MultiEventToMultiGroupWorkflow")
Examples(MultiEventToMultiGroupWorkflow_instance)


# ##CombinedRegions Workflow
# source(auth_env$CombinedRegionWorkflow)

# ##RunImpactAnalysis Workflow
# !!! You need to replace this GUID with one for an existing Project you wish to analyze !!!
# project_id <- "4bc01909-BEEF-BEEF-af8a-2ad16d1dd50b"
# 
# source(auth_env$RunImpactAnalysisWorkflow)
# RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")
# Examples(RunImpactAnalysisWorkflow_instance,ProjectId = project_id)