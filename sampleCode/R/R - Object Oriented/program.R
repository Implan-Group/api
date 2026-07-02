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
