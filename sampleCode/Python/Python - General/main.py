from dotenv import load_dotenv
from endpoints.endpoints_helper import EndpointsHelper
from models.project_models import Project
from utilities.rest_helper import RestHelper
from utilities.logging_helper import LoggingHelper
from workflow_examples.complex_project_example import ComplexProjectExample
from workflow_examples.identifiers_workflow_example import IdentifiersWorkflowExample
from workflow_examples.impact_analysis_workflow_examples import ImpactAnalysisWorkflowExamples
from workflow_examples.regional_workflow_examples import RegionalWorkflowExamples
from workflow_examples.simple_project_workflow_example import SimpleProjectWorkflowExample



# Setup console + file logging
logging_helper = LoggingHelper()

# Load information from the secret `.env` file (see `readme.md` for more information)
load_dotenv()


def main():
    """
    The main entry point into the example scripts.
    This method sets up all required information needed to access the Impact API and demonstrates several common workflows
    """

    # Set up our REST Request Helper
    # This also manages our IMPLAN Impact API Authentication and Authorization
    rest_helper = RestHelper(logging_helper)
    # Set up the EndpointsHelper, which groups Impact API endpoints together by how they are used
    endpoints_helper = EndpointsHelper(rest_helper, logging_helper)

    # Any of the workflows in the `workflow_examples` folder can be accessed at this point,
    # as they only require a valid `EndpointsHelper` instance.

    # To view examples of these workflows in action, uncomment all the lines in a particular section below,
    # and this script will automatically execute the workflow.

    # --- Identifiers + Data Workflow Examples ---
    #workflow = IdentifiersWorkflowExample(endpoints_helper)
    #workflow.execute_example()

    # ----- Regional Workflow Examples -----
    workflow = RegionalWorkflowExamples(endpoints_helper)
    #workflow.combine_regions()          # search through all regions and find several to Combine
    #workflow.explore_implan_regions()   # explore all of Implan's Regional data
    #workflow.explore_user_regions()     # explore all of Your Regional data

    project: Project | None = None

    # --- A Simple Project Creation Workflow Example ---
    #simple_project_workflow_example = SimpleProjectWorkflowExample(endpoints_helper)
    #project = simple_project_workflow_example.execute_example()

    # --- A more complex Project Creation Workflow Example ---
    #complex_project_workflow_example = ComplexProjectExample(endpoints_helper)
    #project = complex_project_workflow_example.execute_example()

    # -- Impact Analysis Workflow Examples ---
    #impact_workflow_example = ImpactAnalysisWorkflowExamples(endpoints_helper)
    #impact_workflow_example.execute_example(project.id) # you can also just pass a UUID or str value directly

    print('Workflow Example(s) Have Completed')


# If we execute this file as a script, this will redirect to calling `main()`
if __name__ == "__main__":
    main()
