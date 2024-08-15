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
