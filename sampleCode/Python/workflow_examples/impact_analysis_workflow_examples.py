import logging
import os
import time
from uuid import UUID

from endpoints.endpoints_helper import EndpointsHelper
from models.project_models import Project
from models.report_models import ImpactResultsExportRequest
from workflow_examples.workflow_example import WorkflowExample
from pathvalidate import sanitize_filename

class ImpactAnalysisWorkflowExamples(WorkflowExample):

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def execute_example(self, project: Project | UUID | str):
        # A Project Id is required in order to reference the project
        # See the Simple + Complex Project Workflow Examples on how to automate the creation of Projects
        project_id: UUID

        if isinstance(project, Project):
            project_id = project.id
        elif isinstance(project, UUID):
            project_id = project
        elif isinstance(project, str):
            project_id = UUID(project)
        else:
            logging.error("You must pass a Project or UUID Project Id")
            return None

        # If you want, you can load the entire Project
        project: Project = self.endpoints.project_endpoints.get_project(project_id)
        if project is None:
            logging.error(f"Could not find Project #{project_id}")
            return None

        # We can run a standard Impact analysis on any Project with just its Project Id
        print(f"Running an impact for Project \"{project.title}\"...\n")
        impact_run_id: int = self.endpoints.impact_endpoints.run_impact(project_id)
        print(f"Impact Run Id is #{impact_run_id}\n")

        # As the Analysis may take some time to complete, we can use a polling loop to wait
        while True:
            print("Waiting 15 seconds to check analysis status...")
            time.sleep(15)

            # Get the status of the Analysis
            analysis_status: str = self.endpoints.impact_endpoints.get_impact_status(impact_run_id)
            print(f"Status is: {analysis_status}")

            # If Complete, exit this loop
            if analysis_status and analysis_status.lower() == "complete":
                break
            # Otherwise, go back to the while to wait again


        # These are some of the example reports that can be obtained from a successful Analysis
        # and how you can save their results to a local .csv file for further processing
        reports_path: str = os.path.join(os.getcwd(), "reports", sanitize_filename(project.title))
        if not os.path.exists(reports_path):
            os.makedirs(reports_path)
        print(f"Exporting all reports to \"{reports_path}\"...\n")

        detailed_economic_indicators_csv: str = self.endpoints.report_endpoints.detailed_economic_indicators(impact_run_id)
        file_path: str = os.path.join(reports_path, "Detailed Economic Indicators.csv")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(detailed_economic_indicators_csv)
        print("Exported Detailed Economic Indicators")

        summary_economic_indicators_csv: str = self.endpoints.report_endpoints.summary_economic_indicators(impact_run_id)
        file_path: str = os.path.join(reports_path, "Summary Economic Indicators.csv")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(summary_economic_indicators_csv)
        print("Exported Summary Economic Indicators")

        detailed_taxes_csv: str = self.endpoints.report_endpoints.detailed_taxes(impact_run_id)
        file_path: str = os.path.join(reports_path, "Detailed Taxes.csv")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(detailed_taxes_csv)
        print("Exported Detailed Taxes")

        summary_taxes_csv: str = self.endpoints.report_endpoints.summary_taxes(impact_run_id)
        file_path: str = os.path.join(reports_path, "Summary Taxes.csv")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(summary_taxes_csv)
        print("Exported Summary Taxes")

        # an Estimated Growth Percentage report requires a more complex request
        # (this is detailed in the Impact API Wiki)
        export_request = ImpactResultsExportRequest(dollar_year=2024)
        estimated_growth_percentage_csv: str = self.endpoints.report_endpoints.estimated_growth_percentage(impact_run_id, export_request)

        file_path: str = os.path.join(reports_path, "Estimated Growth Percentage.csv")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(estimated_growth_percentage_csv)
        print("Exported Estimated Growth Percentage")

        # fin
        return None
