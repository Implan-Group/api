import logging

from services.auth_helper import AuthHelper
from services.rest_helper import RestHelper
from services.logging_helper import LoggingHelper
from unrefactored.workflows.CreateProjectWorkflow import CreateProjectWorkflow
from unrefactored.workflows.RegionalWorkflow import RegionalWorkflow
# from workflows.CombinedRegionWorkflow import CombinedRegionWorkflow
# from workflows.MultiEventToMultiGroupWorkflow import MultiEventToMultiGroupWorkflow
from unrefactored.workflows.RunImpactAnalysisWorkflow import RunImpactAnalysisWorkflow

################################################################################
# Setup console + file logging
logging_helper = LoggingHelper()

# Required:
username: str = ""
password: str = ""


################################################################################




def main():
    """

    """

    # First, we must authenticate
    logging.info("Authenticating to Implan Impact API...")

    auth = AuthHelper(username, password)
    token = auth.get_bearer_token()

    # Now we can create our rest helper
    rest_helper = RestHelper(token, logging_helper)

    # Here is where you can freely modify the rest of this method for your particular workflow!

    # Example #1
    # Create a new Project, add a Regional Group, an Event, and then run the Impact



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
