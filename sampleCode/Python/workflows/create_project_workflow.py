import logging
import datetime
from endpoints.AggregationSchemeEndpoints import AggregationSchemeEndpoints,AggregationScheme
from endpoints.DataSetEndpoints import DataSetEndpoints,DataSet
from endpoints.ProjectEndpoints import Project, ProjectEndpoints
from endpoints.industry_sets import IndustrySet,IndustrySets
from endpoints.IndustryCodeEndpoints import IndustryCodeEndpoints,IndustryCode

from endpoints.Events.Event import Event
from endpoints.Events.EventEndpoints import EventEndpoints
# from endpoints.Events.IndustryOutputEvent import IndustryOutputEvent
from endpoints.Events import IndustryOutputEvent, IndustryImpactAnalysisEvent


from endpoints.GroupEndpoints import GroupEndpoints,Group,GroupEvent
from endpoints.Regions import CombineRegionRequest,Region
from endpoints.Regions.RegionEndpoints import RegionEndpoints

from workflows.iworkflow import IWorkflow

class CreateProjectWorkflow(IWorkflow):
    @staticmethod
    def examples(bearer_token):
        # Get a list of all valid Aggregation Schemes
        aggregation_schemes = AggregationSchemeEndpoints.get_aggregation_schemes(bearer_token)
        
        # Choose the one that you want to use
        implan546_agg_scheme = next(agg for agg in aggregation_schemes if agg.description == "546 Unaggregated")
        # You will need its Aggregation Scheme Id
        aggregation_scheme_id = implan546_agg_scheme.id  # 8
        # As well as a valid Household Set Id
        household_set_id = implan546_agg_scheme.household_set_ids[0]  # 1

        # Define the project with its required properties
        project = Project(
            id=None,  # Initially None since it's a new project
            title=f"ProjectWorkflow - {datetime.datetime.now():%Y-%m-%dT%H:%M:%S}",
            aggregation_scheme_id=aggregation_scheme_id,
            household_set_id=household_set_id
        )

        # This endpoint creates a Project and returns basic information about it
        project = ProjectEndpoints.create(project, bearer_token)
        logging.info(f"Created Project: {project.id}")

        # Verify the project creation
        if not project.id:
            raise ValueError("Project creation failed; project ID is None.")
        
        project_id = project.id

        # With a Project created, you will next need to determine an industry code to use for your event.
        # Get a list of industries that can be utilized for your analysis.
        industry_sets = IndustrySets.get_industry_sets(bearer_token)
        implan546_industries_set = next(s for s in industry_sets if s.description == "546 Industries")  # 8

        # You need to get an Industry Code for the Impact Event -- which can be further filtered by an Industry Set
        industry_codes = IndustryCodeEndpoints.get_industry_codes(aggregation_scheme_id, industry_set_id=implan546_industries_set.id, bearer_token=bearer_token)
        industry_code = next(c for c in industry_codes if c.description == "Oilseed farming")  # 1

        # This endpoint shows all valid Event Types for a given Project
        event_types = EventEndpoints.get_events_types(project.id, bearer_token)
        logging.info(f"Event Types: {event_types}")

        # Create an instance of `IndustryOutputEvent`
        industry_output_event = IndustryOutputEvent.IndustryOutputEvent(
            title="Industry Output Event",
            industry_code=industry_code.code,
            output=100000,
            id="00000000-0000-0000-0000-000000000000"
            # project_id="00000000-0000-0000-0000-000000000000"
        )
        # Set the project_id and impact_event_type attributes
        industry_output_event.project_id = project.id

        # Create an instance of `IndustryImpactAnalysisEvent`
        industry_impact_analysis_event = IndustryImpactAnalysisEvent.IndustryImpactAnalysisEvent(
            title="Industry Impact Analysis Event",
            industry_code=industry_code.code,
            intermediate_inputs=500000,
            total_employment=5,
            employee_compensation=250000,
            proprietor_income=50000,
            wage_and_salary_employment=4,
            proprietor_employment=1,
            total_labor_income=300000,
            other_property_income=100000,
            tax_on_production_and_imports=100000,
            local_purchase_percentage=1.0,
            is_sam=False,
            spending_pattern_dataset_id=87,
            spending_pattern_value_type="intermediateExpenditure",
            id="00000000-0000-0000-0000-000000000000"
            # project_id="00000000-0000-0000-0000-000000000000"
        )
        # Set the project_id and impact_event_type attributes
        industry_impact_analysis_event.project_id = project.id

        # Add the events to the Project we just created -- will return a new Event with information filled in
        industry_output_event = EventEndpoints.add_industry_output_event(project_id, industry_output_event, bearer_token)
        industry_impact_analysis_event = EventEndpoints.add_industry_impact_analysis_event(project_id, industry_impact_analysis_event, bearer_token)

        

        # Check if event creation was successful
        if industry_output_event.id == "00000000-0000-0000-0000-000000000000" or \
        industry_impact_analysis_event.id == "00000000-0000-0000-0000-000000000000":
            logging.error("Event IDs are not set correctly. Check event creation.")
            return

        logging.info(f"Created Industry Output Event with ID: {industry_output_event.id}")
        logging.info(f"Created Industry Impact Analysis Event with ID: {industry_impact_analysis_event.project_id}")
        

        # Now that Event(s) have been added, it is time to find the Region(s) that are to be used in the Impact
        # Regions must be associated with a Data Set
        datasets = DataSetEndpoints.get_datasets(aggregation_scheme_id, bearer_token)
        dataset = next(d for d in datasets if d.description == "2022")

        # For this example, we're going to search through the Child Regions of the US for a particular state
        state_regions = RegionEndpoints.get_region_children(bearer_token, aggregation_scheme_id, dataset.id, regionType="State")
        oregon_state_region = next(s for s in state_regions if s.description == "Oregon")
        oregon_state_hash_id = oregon_state_region.hash_id

        # Print the event details for debugging
        logging.info(f"Industry Output Event: {industry_output_event.to_dict()}")
        logging.info(f"Created Industry Output Event with ID: {industry_output_event.id}")

        logging.info(f"Industry Impact Analysis Event: {industry_impact_analysis_event.to_dict()}")

        industry_output_eventID = industry_output_event.id
        industry_impact_analysis_eventID = industry_impact_analysis_event.id

        # Define the group
        group = Group(
            title="Sample Group",
            id="00000000-0000-0000-0000-000000000000", 
            projectId=project.id,
            hashId=oregon_state_hash_id,
            datasetId=dataset.id,
            dollarYear=2024,
            groupEvents=[
                GroupEvent(eventId = industry_output_eventID, scalingFactor=1.0),
                GroupEvent(eventId = industry_impact_analysis_eventID, scalingFactor=1.0)
            ]
        )

        # Print the group details for debugging
        logging.info(f"Group to be added: {group.to_dict()}")

        # Add the group to the project
        group = GroupEndpoints.add_group_to_project(group.project_id, group, bearer_token)
        logging.info(f"Group created with ID: {group.id}")
        logging.info(f"Project created and fully defined with ID: {project.id}")

        return project.id

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
