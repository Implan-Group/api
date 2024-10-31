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

import time
import logging
from endpoints.ProjectEndpoints import Project, ProjectEndpoints
from endpoints.ImpactEndpoints import ImpactEndpoints
from endpoints.ImpactResultEndpoints import ImpactResultEndpoints,ImpactType
from workflows.authentication_workflow import AuthenticationWorkflow  # Import the AuthenticationWorkflow
from workflows.iworkflow import IWorkflow

class RunImpactAnalysisWorkflow(IWorkflow):
    ProjectId = ""

    @staticmethod
    def examples(bearer_token):
        # Initialize instances
        projects_instance = ProjectEndpoints()
        impacts_instance = ImpactEndpoints()
        impact_results_instance = ImpactResultEndpoints()

        # Get the details for a specific Project
        project = projects_instance.get_project(RunImpactAnalysisWorkflow.ProjectId, bearer_token)
        
        # Run an Analysis on the Project
        impact_run_id = impacts_instance.run_impact(RunImpactAnalysisWorkflow.ProjectId, bearer_token)
        logging.info(f"Impact Run ID: {impact_run_id}")
        
        # Polling loop to check the status every few minutes until it returns `Complete`
        while True:
            # Get the current status
            status = impacts_instance.get_impact_status(impact_run_id, bearer_token)
            logging.debug(f"Current status: {status}")

            # If it is 'Complete', then results can be queried
            if status and status.lower() == "complete":
                logging.info("Status is complete.")
                break

            # If it has not yet completed, give it more time to process
            time.sleep(10)
        
        # Reports about Economic Indicators
        detailed_economic_indicators = impact_results_instance.CsvReports.get_detailed_economic_indicators(impact_run_id, bearer_token)
        summary_economic_indicators = impact_results_instance.CsvReports.get_summary_economic_indicators(impact_run_id, bearer_token)
        
        # Reports about Taxes
        detailed_taxes = impact_results_instance.CsvReports.get_detailed_taxes(impact_run_id, bearer_token)
        summary_taxes = impact_results_instance.CsvReports.get_summary_taxes(impact_run_id, bearer_token)
        
        # For Estimated Growth Percentage, specify additional filters
        estimated_growth_percentage_filter = ImpactResultEndpoints.EstimatedGrowthPercentageFilter(dollar_year=2024)
        estimated_growth_percentage = impact_results_instance.get_estimated_growth_percentage(impact_run_id, estimated_growth_percentage_filter, bearer_token)

        # Print or save the results as needed
        print("Detailed Economic Indicators:", detailed_economic_indicators)
        print("Summary Economic Indicators:", summary_economic_indicators)
        print("Detailed Taxes:", detailed_taxes)
        print("Summary Taxes:", summary_taxes)
        print("Estimated Growth Percentage:", estimated_growth_percentage)

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
