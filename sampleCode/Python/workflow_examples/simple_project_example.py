import datetime
import logging

from endpoints.api_endpoints import EndpointsHelper
from models.project_models import Project
from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class SimpleProjectExample:
    """
    This is an example workflow use as inspiration


    """

    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper

    def complete_workflow(self):
        # Required:
        aggregation_scheme_id: int = 14
        household_set_id: int = 1

        endpoints = EndpointsHelper(self.rest_helper, self.logging_helper)


        # Define the Project with required fields
        project_definition = Project(
            id=None, # The Id will be created by the API
            title=f"ProjectWorkflow - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id
        )

        # Create the project
        project: Project = endpoints.projects.create(project_definition)
        if not project.id:
            raise Exception("Project Creation Failed: Project Id is None")
        logging.info(f"Created Project #{project.id} '{project.title}'")



