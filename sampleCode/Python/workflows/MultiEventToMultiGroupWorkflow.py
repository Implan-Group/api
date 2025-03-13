import datetime

from endpoints.Events import IndustryOutputEvent, HouseholdIncomeEvent
from endpoints.Events.event_endpoints import EventEndpoints
from endpoints.group_endpoints import Group, GroupEvent, GroupEndpoints
from endpoints.industry_code_endpoints import IndustryCodeEndpoints
from endpoints.specification_endpoints import SpecificationEndpoints
from workflows.RunImpactAnalysisWorkflow import RunImpactAnalysisWorkflow
from workflows.iworkflow import IWorkflow
from endpoints.project_endpoints import Project, ProjectEndpoints
from endpoints.aggregation_scheme_endpoints import AggregationSchemeEndpoints
from endpoints.Regions.region_endpoints import RegionEndpoints

class MultiEventToMultiGroupWorkflow(IWorkflow):
    @staticmethod
    def examples(bearer_token):
        # For an analysis that contains multiple Events, each of which needs to be assigned to multiple Groups,
        # a simple nested loop is the easiest solution.
        #
        # Our hypothetical example here is a Mixed-Use Housing Development
        # Apartments for `Households 15-30k` will be built in the basement, several restaurants on the first floor,
        # and accommodations for `Households 50-70k` above
        #
        # More details about creating a project and looking up the Ids below can be found in the CreateProjectWorkflow example
        #
        # For this particular example, we will be using some defaults:
        aggregation_schemes = AggregationSchemeEndpoints.get_aggregation_schemes(bearer_token)
        implan546_agg_scheme = next(agg for agg in aggregation_schemes if agg.description == "546 Unaggregated")
        aggregation_scheme_id = implan546_agg_scheme.id  # 8
        household_set_id = implan546_agg_scheme.household_set_ids[0]  # 1
        industry_set_id = 8          # 546 Industries
        dataset_id = 96              # 2022
        # You will also need the UUID Project Id for the project you're adding the Events/Groups to
        # See the CreateProjectWorkflow for examples on how to create the initial Project
        # For the workflow , We have created  an empty project. You may also pass any pre-existing valid Project Id
        project = Project(
            id_=None,  # Initially None since it's a new project
            title=f"ProjectWorkflow - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id
        )

        # This endpoint creates a Project and returns basic information about it
        project = ProjectEndpoints.create(project, bearer_token)
        project_uuid = project.id

        # Create the Events

        # We need the industry code for restaurants first
        industry_codes = IndustryCodeEndpoints.get_industry_codes(aggregation_scheme_id, industry_set_id, bearer_token)
        industry_code = next(c for c in industry_codes if c.description == "Full-service restaurants")
        # This will be industry code `509 - Full-service restaurants`

        # Create our Restaurant output event        
        restaurant_output = IndustryOutputEvent.IndustryOutputEvent(
            title="Restaurants",
            industry_code=industry_code.code,  # Fixed value as specified
            output=1000000.0,
            employment=None,  # Set to None as specified
            employee_compensation=None,  # Set to None as specified
            proprietor_income=None,  # Set to None as specified
            dataset_id=dataset_id,  # Fixed value as specified
            margin_type=None,  # Set to None as specified
            percentage=None,  # Set to None as specified
            id_="00000000-0000-0000-0000-000000000000",  # Placeholder ID as specified
            project_id="00000000-0000-0000-0000-000000000000",  # Placeholder project ID as specified
            tags=[]  # Empty tags list as specified
        )


        # Now we need to create the housing events
        # You need to lookup all the specification codes for Household Income Events
        household_income_specifications = SpecificationEndpoints.get_specifications(project_uuid, "HouseholdIncome", bearer_token)

        # Create the 15-30k Household Event
        first_household_income_event = HouseholdIncomeEvent.HouseholdIncomeEvent(
            title="Households 15-30k",
            household_income_code=10002,  # Households 15-30k (spec code from above)
            value=25000.00,
            id_="00000000-0000-0000-0000-000000000000",  # Placeholder ID, replace with actual if needed
            project_id="00000000-0000-0000-0000-000000000000",  # Placeholder Project ID
            tags=[]
        )
        # Create the 50-70k Household Event
        second_household_income_event = HouseholdIncomeEvent.HouseholdIncomeEvent(
            title="Households 50-70k",
            household_income_code=10005,  # Households 15-30k (spec code from above)
            value=125000.00,
            id_="00000000-0000-0000-0000-000000000000",  # Placeholder ID, replace with actual if needed
            project_id="00000000-0000-0000-0000-000000000000",  # Placeholder Project ID
            tags=[]
        )

        # We have created all the Events.
        # By calling the `add_event` endpoint, the fully-hydrated Event is returned (including its Id, which will be required)
        # We'll store them to a list for future processing
        restaurant_output = EventEndpoints.add_industry_output_event(project_uuid, restaurant_output, bearer_token)
        first_household_income_event = EventEndpoints.add_household_income_event(project_uuid, first_household_income_event, bearer_token)
        second_household_income_event = EventEndpoints.add_household_income_event(project_uuid, second_household_income_event, bearer_token)

        events = [restaurant_output, first_household_income_event, second_household_income_event]

        # Now we need to create our Groups.
        # For this example, we're comparing the impacts of these Events on several different states
        states = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, dataset_id, region_type="State")
        oregon = next(s for s in states if s.description == "Oregon")
        wisconsin = next(s for s in states if s.description == "Wisconsin")
        north_carolina = next(s for s in states if s.description == "North Carolina")
        # We'll store these in a list for later use
        regions = [oregon, wisconsin, north_carolina]

        # Now, for each Region
        for region in regions:
            # Create a Group for that Region
            state_group = Group(
                project_id=project_uuid,
                title=f"{region.description} State",  # each Group has to have a different Title
                dataset_id=dataset_id,
                dollar_year=2024,  # latest year
                hash_id=region.hash_id,  # associate this Region with this Group
            )
            # Add all of our Events to this Group   
            state_group.group_events = [
            GroupEvent(event_id=e['id'] if isinstance(e, dict) else e.id) for e in events
        ]
            # Save the Group to the Project
            state_group = GroupEndpoints.add_group_to_project(project_uuid, state_group, bearer_token)

        # Now that the Events and Groups have been added, see below
        RunImpactAnalysisWorkflow.ProjectId = project_uuid
        RunImpactAnalysisWorkflow.examples(bearer_token)
