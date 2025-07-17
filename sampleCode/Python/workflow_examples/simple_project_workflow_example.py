import datetime
import logging

from uuid import UUID
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import SpendingPatternValueType, RegionType
from models.event_models import IndustryOutputEvent, IndustryImpactAnalysisEvent
from models.group_models import Group, GroupEvent
from models.project_models import Project
from models.region import Region
from utilities.python_helper import uuid_empty
from workflow_examples.workflow_example import WorkflowExample


class SimpleProjectWorkflowExample(WorkflowExample):
    """
    This is a Simple Project Workflow Example,
    showing how one can configure and add Projects, Events, and Groups using the Impact API
    """

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def execute_example(self) -> Project | None:
        """
        Executes an example workflow
        """

        # Required identifiers: (see `data_endpoints` and `identifiers_example` for more information on finding these ids)
        aggregation_scheme_id: int = 14  # 528 Unaggregated
        household_set_id: int = 1  # Primary Household Set
        dataset_id: int = 98  # 2023 Default
        industry_set_id = 12  # 528 Industries
        industry_code = 3  # Vegetable and fruit farming

        # ----- Project -----

        # Define the Project with all required fields
        project_definition = Project(
            id = uuid_empty(),
            title=f"Example Project - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id,
            # There are additional fields, but are not required for this simple example
        )

        # Create the project
        project: Project = self.endpoints.project_endpoints.create_project(project_definition)
        if not project.id:
            raise Exception("Project Creation Failed: Project Id is None")
        logging.info(f"Created Project #{project.id} '{project.title}'")
        # Capture the ProjectId, it is used for subsequent endpoints
        project_id: UUID = project.id

        # Now that a project has been created, it can be filled with groups and events

        # ----- Events -----

        # For this example, we're going to create a simple Industry Output Event
        industry_output_event = IndustryOutputEvent(
            project_id=project_id,
            title=f"Example Industry Output Event - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            industry_code=industry_code,
            output=100_000.0,
        )

        # Add this Event to the Project
        # We assign the output back to the event as the returned event has all of its information filled out
        industry_output_event = self.endpoints.event_endpoints.add_event(project_id, industry_output_event)
        if industry_output_event.id is None or industry_output_event.id == uuid_empty():
            logging.error(f"Event returned with invalid Id: {industry_output_event.id}")
            raise "Invalid Event Response"

        temp = self.endpoints.event_endpoints.get_event(project_id, industry_output_event.id)
        print(temp)
        temp2 = self.endpoints.event_endpoints.get_event(project_id, industry_output_event.id, IndustryOutputEvent)
        print(temp2)

        # And a more complicated Industry Impact Analysis Event
        industry_impact_analysis_event = IndustryImpactAnalysisEvent(
            project_id=project_id,
            title=f"Example Industry Impact Analysis Event - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            industry_code=industry_code,
            intermediate_inputs=500_000.0,
            total_employment=5,
            employee_compensation=250_000.0,
            proprietor_income=50_000.0,
            wage_and_salary_employment=4,
            proprietor_employment=1,
            total_labor_income=300_000.0,
            other_property_income=100_000.0,
            tax_on_production_and_imports=100_000.0,
            local_purchase_percentage=1.0,
            is_sam=False,
            spending_pattern_dataset_id=dataset_id,
            spending_pattern_value_type=SpendingPatternValueType.INTERMEDIATE_EXPENDITURE,
        )

        # Add this Event and reassign
        industry_impact_analysis_event = self.endpoints.event_endpoints.add_event(project_id, industry_impact_analysis_event)
        if industry_impact_analysis_event.id is None or industry_impact_analysis_event.id == uuid_empty():
            logging.error(f"Event returned with invalid Id: {industry_impact_analysis_event.id}")
            raise "Invalid Event Response"

        # ----- Groups -----

        # Now that we've added Events to this Project, we can add some Groups
        # For more information on Regionality, see `regional_endpoints` and the `regional_workflow_examples`

        # Get a list of all the states in the US
        states: list[Region] = self.endpoints.regional_endpoints.get_region_children(aggregation_scheme_id, dataset_id, region_type=RegionType.STATE)
        # Filter the list to only Oregon
        oregon_state: Region = next(s for s in states if s.description == "Oregon")
        # We'll use its HashId for our Group
        oregon_state_hashid: str = oregon_state.hash_id

        # Define the Group's Events (one per Region/Event pairing)
        industry_output_event_group = GroupEvent(
            event_id=industry_output_event.id
        )
        industry_impact_analysis_event_group = GroupEvent(
            event_id=industry_impact_analysis_event.id
        )

        # Define the Group
        group = Group(
            title=f"Example Group - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            project_id=project_id,
            hash_id=oregon_state_hashid,
            dataset_id=dataset_id,
            dollar_year=2024,
            group_events=[
                industry_output_event_group,
                industry_impact_analysis_event_group,
            ]
        )

        # Add the Group to the Project
        group = self.endpoints.group_endpoints.add_group_to_project(project_id, group)
        if group.id is None or group.id == uuid_empty():
            logging.error(f"Group returned with invalid Id: {group.id}")
            raise "Invalid Group Response"

        # Now this Project has a Group with Two Events and is ready for processing
        # See the `impact_analysis_workflow_examples` for how to accomplish that
        return project
