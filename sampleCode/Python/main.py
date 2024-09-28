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

import logging
from workflows.authentication_workflow import AuthenticationWorkflow
from workflows.create_project_workflow import CreateProjectWorkflow
from workflows.regional_workflow import RegionalWorkflow
from workflows.combined_region_workflow import CombinedRegionWorkflow
from workflows.MultiEventToMultiGroupWorkflow import MultiEventToMultiGroupWorkflow
from workflows.run_impact_analysis_workflow import RunImpactAnalysisWorkflow

def main():
    # Authenticate and get bearer token
    bearer_token = AuthenticationWorkflow.examples()
    logging.info(f"Bearer Token used: {bearer_token}")

    # Create Project Workflow
    # project_id = CreateProjectWorkflow.examples(bearer_token)
    # RunImpactAnalysisWorkflow.ProjectId = project_id
    # RunImpactAnalysisWorkflow.examples(bearer_token)

    # Regional Workflow
    # RegionalWorkflow.examples(bearer_token)

    MultiEventToMultiGroupWorkflow.examples(bearer_token)

    # Combined Region Workflow
    # CombinedRegionWorkflow.examples(bearer_token)

    # Run Impact Analysis Workflow
    # RunImpactAnalysisWorkflow.examples(bearer_token)

    logging.info("finished")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
