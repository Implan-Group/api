import datetime
import logging
from uuid import UUID

from endpoints.endpoints_root import EndpointsHelper
from models.enums import SpendingPatternValueType, RegionType
from models.event_models import IndustryOutputEvent, IndustryImpactAnalysisEvent
from models.group_models import Group, GroupEvent
from models.project_models import Project
from models.region import Region
from services.logging_helper import LoggingHelper
from utilities.python_helper import uuid_empty
from services.rest_helper import RestHelper


class SimpleProjectExample:
    """
    This is an example workflow use as inspiration


    """

    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper

    def execute_example(self):
        # Required:
        aggregation_scheme_id: int = 14     # 528 Unaggregated
        household_set_id: int = 1           #
        dataset_id: int = 98                # 2023 Default

        endpoints = EndpointsHelper(self.rest_helper, self.logging_helper)

        # Define the Project with required fields
        project_definition = Project(
            id=uuid_empty(), # The Id will be created by the API
            title=f"ProjectWorkflow - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id
        )

        # Create the project
        project: Project = endpoints.project_endpoints.create_project(project_definition)
        if not project.id:
            raise Exception("Project Creation Failed: Project Id is None")
        logging.info(f"Created Project #{project.id} '{project.title}'")

        # Capture the ProjectId, it is used for future calls
        project_id: UUID = project.id

        # Now that a project has been created, it can be filled with groups and events

        # Events
        # We'll need an Industry Set Code and an Industry Code in order to specify events
        # See `IdentifiersExample` for ways to retrieve those ids
        industry_set_id = 12    # 528 Industries
        industry_code = 3       # Vegetable and fruit farming

        # Since we have a valid Project Id, we can query for all Event Types that are valid for this Project
        event_types = endpoints.event_endpoints.get_event_types(project_id)

        # For this example, we're going to create a simple Industry Output Event
        industry_output_event = IndustryOutputEvent(
            project_id=project_id,
            title="Example Industry Output Event",
            industry_code=industry_code,
            output=100_000
        )

        # Add this Event to the Project
        # We re-assign here as the returned Event is fully hydrated
        industry_output_event = endpoints.event_endpoints.add_event(project_id, industry_output_event)

        # Validate
        if industry_output_event.id == uuid_empty():
            logging.error(f"Event returned with invalid Id: {industry_output_event.id}")
            raise "Invalid Event Response"

        print(industry_output_event)

        # And a much more complicated Industry Impact Analysis Event
        industry_impact_analysis_event = IndustryImpactAnalysisEvent(
            id = uuid_empty(),
            project_id=project_id,
            title="Example Industry Impact Analysis Event",
            industry_code=industry_code,
            intermediate_inputs=500_000,
            total_employment=5,
            employee_compensation=250_000,
            proprietor_income=50_000,
            wage_and_salary_employment=4,
            proprietor_employment=1,
            total_labor_income=300_000,
            other_property_income=100_000,
            tax_on_production_and_imports=100_000,
            local_purchase_percentage=1.0,
            is_sam=False,
            spending_pattern_dataset_id=87,
            spending_pattern_value_type=SpendingPatternValueType.INTERMEDIATE_EXPENDITURE
        )

        industry_impact_analysis_event = endpoints.event_endpoints.add_event(project_id, industry_impact_analysis_event)

        # Validate
        if industry_impact_analysis_event.id == uuid_empty():
            logging.error(f"Event returned with invalid Id: {industry_impact_analysis_event.id}")
            raise "Invalid Event Response"



        # Now that we've added Events to this Project, we can add some Groups
        # As Groups are associated with Regions, see the RegionalWorkflow Examples for more information

        # Get a list of all the states in the US
        states: list[Region] = endpoints.regional_endpoints.get_region_children(aggregation_scheme_id, dataset_id, region_type=RegionType.STATE)
        # Filter the list to only Oregon
        oregon_state: Region = next(s for s in states if s.description == "Oregon")
        # We'll use its HashId for our Group
        oregon_state_hashid: str = oregon_state.hash_id


        # Define the Group's Events (one per Region/Event pairing)
        industry_output_event_group: GroupEvent = GroupEvent(
            event_id=industry_output_event.id
        )
        industry_impact_analysis_event_group: GroupEvent = GroupEvent(
            event_id=industry_impact_analysis_event.id
        )

        # Define the Group
        group = Group(
            id = uuid_empty(),
            title="Example Group",
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
        # We re-assign back to Group as the return class is fully hydrated
        group = endpoints.group_endpoints.add_group_to_project(project_id, group)

        print(group)


        # Now this Project has a Group with Two Events and is ready for processing
        # See the `Running Impact Analysis` workflows for examples on how to do so
        return


