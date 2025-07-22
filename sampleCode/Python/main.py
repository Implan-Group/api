from dotenv import load_dotenv
from endpoints.endpoints_helper import EndpointsHelper
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

    # Any of the workflows in the `workflow_examples` folder can be accessed at this point, as they
    # only require a valid `EndpointsHelper` instance

    # Just uncomment a particular section and this script will automatically execute the workflow


    # --- Identifiers + Data Workflow Examples ---
    #workflow = IdentifiersWorkflowExample(endpoints_helper)
    #workflow.execute_example()

    # --- Regional Workflow Examples ---
    #workflow = RegionalWorkflowExamples(endpoints_helper)
    #workflow.combine_regions()
    #workflow.explore_implan_regions()
    #workflow.explore_user_regions()

    # --- A Simple Project Creation Workflow Example ---
    #workflow = SimpleProjectWorkflowExample(endpoints_helper)
    #workflow.execute_example()

    # --- A more complex Project Creation Workflow Example ---
    #workflow = ComplexProjectExample(endpoints_helper)
    #workflow.execute_example()

    # -- Impact Analysis Workflow Examples ---
    #workflows = ImpactAnalysisWorkflowExamples(endpoints_helper)
    #workflows.execute_example()

    print('Workflow Example(s) Have Completed')


# If we execute this file as a script, this will redirect to calling `main()`
if __name__ == "__main__":
    main()
