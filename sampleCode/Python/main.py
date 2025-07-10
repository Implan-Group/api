import logging
import os

from endpoints.endpoints_root import EndpointsHelper
from services.auth_helper import AuthHelper
from services.rest_helper import RestHelper
from services.logging_helper import LoggingHelper
from workflow_examples.identifiers_example import IdentifiersExample
from workflow_examples.regional_examples import RegionalWorkflowExamples
from workflow_examples.simple_project_example import SimpleProjectExample
from dotenv import load_dotenv

# from unrefactored.workflows.CreateProjectWorkflow import CreateProjectWorkflow
# from unrefactored.workflows.RegionalWorkflow import RegionalWorkflow
# # from workflows.CombinedRegionWorkflow import CombinedRegionWorkflow
# # from workflows.MultiEventToMultiGroupWorkflow import MultiEventToMultiGroupWorkflow
# from unrefactored.workflows.RunImpactAnalysisWorkflow import RunImpactAnalysisWorkflow

################################################################################
# Setup console + file logging
logging_helper = LoggingHelper()

# Load information from the secret `.env` file (see `readme.md` for more information)
load_dotenv()

################################################################################




def main():
    """

    """

    # First, we must authenticate to the Implan Impact API
    logging.info("Authenticating to Implan Impact API...")

    # Send in our required username and password
    username = os.getenv("IMPLAN_USERNAME")
    password = os.getenv("IMPLAN_PASSWORD")
    auth = AuthHelper(username, password)
    # Retrieve the bearer token
    token = auth.get_bearer_token()

    # Now we can create our rest helper
    rest_helper = RestHelper(token, logging_helper)

    # Here is where you can freely modify the rest of this method for your particular workflow!

    # # Simple Project Example
    # # Creates a new Project, adds Events, then adds Groups
    # workflow = SimpleProjectExample(rest_helper, logging_helper)
    # workflow.execute_example()
    #
    # # Identifiers Example
    # # All the ways that various IDs can be looked up
    # workflow = IdentifiersExample(rest_helper, logging_helper)
    # workflow.execute_example()

    # Regional Workflow Examples
    workflow = RegionalWorkflowExamples(rest_helper, logging_helper)

    # Search through Regions to find several to combine, combine them, and wait for the new Combined Region to be available
    #workflow.combine_regions()

    # Different ways to explore regional relationships
    workflow.explore_implan_regions()
    #workflow.explore_user_regions()


    print('break')






    # Create a new Project, add a Regional Group, an Event, and then run the Impact



    # # Create Project Workflow
    # project_id = CreateProjectWorkflow.examples(bearer_token)
    # RunImpactAnalysisWorkflow.ProjectId = project_id
    # RunImpactAnalysisWorkflow.examples(bearer_token)
    #
    # # Regional Workflow
    # RegionalWorkflow.examples(bearer_token)
    #
    # # MultiEventToMultiGroupWorkflow.examples(bearer_token)
    #
    # # Combined Region Workflow
    # # CombinedRegionWorkflow.examples(bearer_token)
    #
    # # Run Impact Analysis Workflow
    # # RunImpactAnalysisWorkflow.examples(bearer_token)
    #
    # logging.info("finished")

# If we execute this file as a script, this will redirect to calling `main()`
if __name__ == "__main__":
    main()
