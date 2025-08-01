﻿from datetime import datetime
from endpoints.endpoints_helper import EndpointsHelper
from models.enums import RegionType
from models.event_models import IndustryOutputEvent, HouseholdIncomeEvent, Event
from models.group_models import Group, GroupEvent
from models.project_models import Project
from models.region import Region
from workflow_examples.workflow_example import WorkflowExample


class ComplexProjectExample(WorkflowExample):

    def __init__(self, endpoints_helper: EndpointsHelper):
        super().__init__(endpoints_helper)

    def execute_example(self):
        """
        This Project contains multiple Events, each assigned to multiple Groups

        Our hypothetical is a Mixed-Use Housing Development,
        where there will be restaurants, small apartments for `Households 15-30k`, and larger apartments for `Households 50-70k`.

        This example builds upon the SimpleProjectExample

        """

        # These identifiers were chosen specifically for this Project
        # Please see IdentifierExamples for more details on how to find them
        aggregation_scheme_id: int = 14  # 528 Unaggregated US
        household_set_id: int = 1
        dataset_id: int = 98  # 2023

        # Set up the initial Project
        project = Project(
            title=f"Complex Project Workflow Example- {datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id,
        )
        project = self.endpoints.project_endpoints.create_project(project)
        print(project)

        # Create and Add all the Events

        # Restaurant Output Event
        restaurant_output_event = IndustryOutputEvent(
            title="Restaurants",
            industry_code=509,  # `491 - Full-Service Restaurants`
            output=1_000_000.0,
            dataset_id=dataset_id,
            project_id=project.id,
        )
        restaurant_output_event = self.endpoints.event_endpoints.add_event(project.id, restaurant_output_event)
        print(restaurant_output_event)

        # 15-30k Household Income Event
        lo_household_income_event = HouseholdIncomeEvent(
            title="Households 15-30k",
            household_income_code=10002,  # Households 15-30k, see Specifications
            value=25_000.0,
            project_id=project.id,
        )
        lo_household_income_event = self.endpoints.event_endpoints.add_event(project.id, lo_household_income_event)
        print(lo_household_income_event)

        # 50-70k Household Income Event
        hi_household_income_event = HouseholdIncomeEvent(
            title="Households 50-75k",
            household_income_code=10005,  # Households 50-75k,
            value=125_000.0,
            project_id=project.id,
        )
        hi_household_income_event = self.endpoints.event_endpoints.add_event(project.id, hi_household_income_event)
        print(hi_household_income_event)

        # Create and add all the Groups

        # For this example, the developer is narrowing down which state might be best for this project
        # There are three states under consideration:
        us_states: list[Region] = self.endpoints.regional_endpoints.get_region_children(aggregation_scheme_id, dataset_id, region_type=RegionType.STATE)
        oregon: Region = next(state for state in us_states if state.description == "Oregon")
        wisconsin: Region = next(state for state in us_states if state.description == "Wisconsin")
        north_carolina: Region = next(state for state in us_states if state.description == "North Carolina")

        # For each state, we want to add all three events
        # The best way to accomplish this is by storing the Events and Regions in a list so we can iterate over them
        events: list[Event] = [restaurant_output_event, lo_household_income_event, hi_household_income_event]
        print(events)
        regions: list[Region] = [oregon, wisconsin, north_carolina]
        print(regions)
        # We'll need to link the events to the groups using a GroupEvent, which we can prepare now
        group_events: list[GroupEvent] = [GroupEvent(event_id=e.id) for e in events]
        print(group_events)

        for region in regions:
            # Create the Group for this Region
            group = Group(
                project_id=project.id,
                title=f"{region.description} State",  # Each Group must have a different description
                dataset_id=dataset_id,
                dollar_year=2024,
                hash_id=region.hash_id,  # Associate this Region with this Group
                group_events=group_events,  # Add all three events
            )
            print(group)
            # Save this Group to the Project
            self.endpoints.group_endpoints.add_group_to_project(project.id, group)

        # Now the Project exists with three Events, three Groups, and each Group will have all three Events associated
        # You can proceed to process that Project how you please (see other workflows for Running an Impact and Viewing the Output)
