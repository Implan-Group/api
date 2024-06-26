namespace ConsoleApp.Workflows;

public class CreateProjectWorkflow : IWorkflow
{
    /// <summary>
    /// This Example Workflow follows along with `api\impact\workflows\CreateProject.md`
    /// </summary>
    public static void Examples()
    {
        /* Projects are the top level of organization for an analysis and contain the specifics of the Aggregation Scheme, Household Set, MRIO status, and folder placement.
         * This example shows off the most basic of Project Creation workflows
         * Please see the main Impact Readme at `api\impact\readme.md` and `support.implan.com` for more information.
         */
        
        
        /* The first step to create a Project is to find the Aggregation Scheme */

        // Get a list of all valid Aggregation Schemes
        AggregationScheme[] aggregationSchemes = AggregationSchemes.GetAggregationSchemes();

        // Choose the one that you want to use
        AggregationScheme implan546AggScheme = aggregationSchemes.First(agg => agg.Description == "546 Unaggregated");
        // You will need its Aggregation Scheme Id
        int aggregationSchemeId = implan546AggScheme.Id;    // 8
        // As well as a valid Household Set Id
        int householdSetId = implan546AggScheme.HouseholdSetIds.First();    // 1

        
        /* Once you have chosen your Aggregation Scheme Id and one of its Household Set Ids, you can create your Project */
        
        // Define the project with its required properties
        Project project = new Project
        {
            // The title must be unique, so we're using the timestamp here
            Title = $"ProjectWorkflow - {DateTime.Now:s}",
            AggregationSchemeId = aggregationSchemeId,
            HouseholdSetId = householdSetId,
        };
        
        // This endpoint creates a Project and returns basic information about it, including a unique identifier `projectId` (guid) to be used in other API requests.
        // Note: Calling this endpoint returns a fully-hydrated Project, so we re-assign it here
        project = Projects.Create(project);
        
      
        // With a Project created, you will next need to determine an industry code to use for your event.
        // A list of industries that can be utilized for your analysis.
        // Events created later will require reference to one of the industry codes (`code`) returned here.
        
        // Industries are seperated into different Industry Sets
        IndustrySet[] industrySets = IndustrySets.GetIndustrySets();
        // Choose the one that describes your industry
        IndustrySet implan546IndustriesSet = industrySets.First(s => s.Description == "546 Industries");     // 8
        
        // You need to get an Industry Code for the Impact Event -- which can be further filtered by an Industry Set
        IndustryCode[] industryCodes = IndustryCodes.GetIndustryCodes(aggregationSchemeId, 
            industrySetId: implan546IndustriesSet.Id);
        // Choose the one that best fits
        IndustryCode industryCode = industryCodes.First(c => c.Description == "Oilseed farming");   // 1
        
        
        /* There are many types of Industry Event, each requires a different Payload to be sent to the AddEvent endpoint */
        
        // This endpoint shows all valid Event Types for a given Project
        string[] eventTypes = Events.GetEventsTypes(project.Id);
        // See the main Impact Readme or support for more details on different event types
        
        
        // An Industry Output Event
        IndustryOutputEvent industryOutputEvent = new IndustryOutputEvent()
        {
            Title = "Industry Output Event",
            IndustryCode = industryCode.Code,
            Output = 100_000.00,
        };
        
        // An Industry Impact Analysis
        IndustryImpactAnalysisEvent industryImpactAnalysisEvent = new IndustryImpactAnalysisEvent()
        {
            Title = "Industry Impact Analysis Event",
            IndustryCode = industryCode.Code,
            IntermediateInputs = 500_000,
            EmployeeCompensation = 250_000,
            ProprietorIncome = 50_000,
            WageAndSalaryEmployment = 4,
            ProprietorEmployment = 1,
            TotalEmployment = 5,
            TotalLaborIncome = 300_000,
            OtherPropertyIncome = 100_000,
            TaxOnProductionAndImports = 100_000,
            SpendingPatternDatasetId = 87,
            SpendingPatternValueType = SpendingPatternValueType.IntermediateExpenditure,
        };

        // Add the events to the Project we just created -- will return a new Event with information filled in
        industryOutputEvent = Events.AddEvent(project.Id, industryOutputEvent);
        industryImpactAnalysisEvent = Events.AddEvent(project.Id, industryImpactAnalysisEvent);
        
        
        /* Now that Event(s) have been added, it is time to find the Region(s) that are to be used in the Impact */
        // See Regions.cs, CombinedRegionWorkflow.cs, and RegionalWorkflow.cs for more examples on searching regions
        
        // Regions must be associated with a Data Set
        // Get a list of all valid Data Sets for the Aggregation Scheme
        DataSet[] datasets = DataSets.GetDataSets(aggregationSchemeId);
        // Choose the one you would like to use -- must be compatible with your chosen HouseholdSetId!
        DataSet dataset = datasets.First(d => d.Description == "2022");
        
        // For this example, we're going to search through the Child Regions of the US for a particular state
        Region[] stateRegions = Regions.GetRegionChildren(aggregationSchemeId, dataset.Id, regionType: "State");
        Region oregonStateRegion = stateRegions.First(s => s.Description == "Oregon");
        // We need the HashId specifically
        string oregonStateHashId = oregonStateRegion.HashId;    // 15b869ZOxy
        
        
        /* Adding Groups
         * Groups represent the Region and timeframe in which an Event takes place.
         * Use the following endpoints to arrange Groups in your project.
         * Reference the `ProjectId` and `EventId`s from the created Project and Events where required.
         */
        
        // Define the group
        Group group = new Group()
        {
            ProjectId = project.Id,
            Title = "Sample Group",
            DatasetId = dataset.Id,
            DollarYear = 2024,
            // Must specify at least one regional identifier
            HashId = oregonStateHashId,
            // Must add at least one Event
            GroupEvents = [
                new GroupEvent(eventId: industryOutputEvent.Id),
                new GroupEvent(eventId: industryImpactAnalysisEvent.Id),
            ],
        };

        // Note: Calling this endpoint returns a fully-hydrated Group, so we re-assign it here
        group = Groups.AddGroupToProject(project.Id, group);
        
        
        // Now that the Project has been fully defined, see
        RunImpactAnalysisWorkflow.ProjectId = project.Id;
        RunImpactAnalysisWorkflow.Examples();
        // for ways to run an Analysis and view the Results
    }
}