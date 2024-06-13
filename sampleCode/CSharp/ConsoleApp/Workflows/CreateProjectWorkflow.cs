namespace ConsoleApp.Workflows;

/// <summary>
/// A workflow that describes the process to create and fill a Project
/// </summary>
public class CreateProjectWorkflow : IWorkflow
{
    public static void Examples()
    {
        /* The first step is to create the Project itself
         * Aa unique Title, Aggregation Scheme Id, and HouseholdSetId are all required to define a Project
         */

        // Get a list of all valid Aggregation Schemes
        var aggregationSchemes = AggregationSchemes.GetAggregationSchemes();
        // Choose the one you would like to use
        int aggregationSchemeId = 8; // The default
        
        
        // Select a HouseholdSetId from among the valid options in the AggregationScheme
        int householdSetId = 1;

        
        // Get a list of all valid Data Sets for the Aggregation Scheme
        var datasets = DataSets.GetDataSets(aggregationSchemeId);
        // Choose the one you would like to use -- must be compatible with your chosen HouseholdSetId
        int dataSetId = 96;

        
        // Now we can define the project with its required properties
        Project project = new Project
        {
            // The title must be unique, so we're using the timestamp here
            Title = $"PROJECT NAME - {DateTime.Now:s}",
            AggregationSchemeId = aggregationSchemeId,
            HouseholdSetId = householdSetId,
        };
        
        // Call the CreateProject Endpoint to retrieve the rest of the Project information (including the Project's Unique Id)
        project = Projects.Create(project);
        
      
        /* Once a Project has been created, it needs to be filled with Impact Events */
        
        // Industries are seperated into different Industry Sets
        var industrySets = IndustrySets.GetIndustrySets();
        
        // You need to get an Industry Code for the Impact Event -- which can be further filtered by an Industry Set
        var industryCodes = IndustryCodes.GetIndustryCodes(aggregationSchemeId, industrySetId: null);
        
        // Now we can create an event. There are many types of event
        // TODO: PHX-11909 - Get Event Types
        
        // Once you have all the details, you can define the Event
        var industryOutputEvent = new IndustryOutputEvent()
        {
            Title = "Industry Output",
            IndustryCode = 1,
            Output = 100_000.00,
        };

        // Add the event to the Project we just created -- will return a new Event with information filled in
        industryOutputEvent = Events.AddEvent(project.Id, industryOutputEvent);
        
        /*  With events added, it is time to define Group(s) to contain the Event(s) in Region(s)  */
    
        // Start by defining your Group
        Group group = new Group()
        {
            ProjectId = project.Id,
            Title = "Sample Group 1",
            DatasetId = dataSetId,
            DollarYear = 2024,
        };

        // Every Group requires a Single Region
        RegionalWorkflow.Examples(); // <- Use these endpoints to explore Regional Information
        
        // A HashId, Urid, ModelId, _or_ UserModelId must be defined
        // Including excess Regional information can cause mismatch failures        
        group.HashId = "15b869ZOxy";      // Agg Scheme Id #8, DataSet Id #96: The State of Oregon
        
        // The Group starts off with Zero events (group.GroupEvents) and can have any number added
        GroupEvent groupEvent = new GroupEvent { EventId = industryOutputEvent.Id };
        group.GroupEvents = [groupEvent];

        // Then you can add the fully-defined Group to the Project -- will return a new Group with additional information
        group = Groups.AddGroup(project.Id, group);
        
        
        // Now that the Project has been fully defined, see:
        ImpactResultsWorkflow.Examples();
    }
}