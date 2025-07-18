import logging
import time
from uuid import UUID

from endpoints.endpoints_helper import EndpointsHelper
from models.project_models import Project
from models.report_models import ImpactResultsExportRequest
from workflow_examples.workflow_example import WorkflowExample


class ImpactAnalysisWorkflowExamples(WorkflowExample):

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def execute_example(self):
        # A Project Id is required in order to reference the project
        # See the Simple + Complex Project Workflow Examples on how to automate the creation of Projects

        # This example ID will not work, it must be replaced with a real Project Id
        project_id: UUID = UUID('affc3579-76f4-4bfa-8056-c9520acc8201')

        # If you want, you can load the entire Project
        project: Project = self.endpoints.project_endpoints.get_project(project_id)
        if project is None:
            logging.error(f"Could not find Project #{project_id}")
            return None

        # We can run a standard Impact analysis on any Project with just its Project Id
        impact_run_id: int = self.endpoints.impact_endpoints.run_impact(project_id)
        print(impact_run_id)

        # As the Analysis may take some time to complete, we can use a polling loop to wait
        while True:
            # Get the status of the Analysis
            analysis_status = self.endpoints.impact_endpoints.get_impact_status(impact_run_id)
            # If Complete, exit this loop
            if analysis_status and analysis_status.lower() == "complete":
                break
            # Otherwise, wait a bit and check again
            time.sleep(30)

        # These are some of the example reports that can be obtained from a successful Analysis:

        detailed_economic_indicators_csv: str = self.endpoints.report_endpoints.detailed_economic_indicators(impact_run_id)
        summary_economic_indicators_csv: str = self.endpoints.report_endpoints.summary_economic_indicators(impact_run_id)
        detailed_taxes_csv: str = self.endpoints.report_endpoints.detailed_taxes(impact_run_id)
        summary_taxes_csv: str = self.endpoints.report_endpoints.summary_taxes(impact_run_id)

        export_request = ImpactResultsExportRequest(dollar_year=2024)
        estimated_growth_percentage_csv = self.endpoints.report_endpoints.estimated_growth_percentage(impact_run_id, export_request)

        # If you want to save the report as a csv file (to be opened by another application):
        file_path: str = f"Project #{project.id} - Detailed Economic Indicators.csv"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(detailed_economic_indicators_csv)

        return None
