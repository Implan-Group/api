import logging

from unrefactored.logging_helper import LoggingHelper
from unrefactored.workflows.AuthenticationWorkflow import AuthenticationWorkflow
from unrefactored.workflows.CreateProjectWorkflow import CreateProjectWorkflow
from unrefactored.workflows.RegionalWorkflow import RegionalWorkflow
# from workflows.CombinedRegionWorkflow import CombinedRegionWorkflow
# from workflows.MultiEventToMultiGroupWorkflow import MultiEventToMultiGroupWorkflow
from unrefactored.workflows.RunImpactAnalysisWorkflow import RunImpactAnalysisWorkflow

################################################################################
# Setup console + file logging
logging_helper = LoggingHelper()



################################################################################




def main():
    # Authenticate and get bearer token
    bearer_token = AuthenticationWorkflow.get_bearer_token()
    logging.info(f"Bearer Token used: {bearer_token}")

    # Create Project Workflow
    project_id = CreateProjectWorkflow.examples(bearer_token)
    RunImpactAnalysisWorkflow.ProjectId = project_id
    RunImpactAnalysisWorkflow.examples(bearer_token)

    # Regional Workflow
    RegionalWorkflow.examples(bearer_token)

    # MultiEventToMultiGroupWorkflow.examples(bearer_token)

    # Combined Region Workflow
    # CombinedRegionWorkflow.examples(bearer_token)

    # Run Impact Analysis Workflow
    # RunImpactAnalysisWorkflow.examples(bearer_token)

    logging.info("finished")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
