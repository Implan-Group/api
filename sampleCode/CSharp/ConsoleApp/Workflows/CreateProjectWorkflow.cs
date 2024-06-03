namespace ConsoleApp.Workflows;

public class CreateProjectWorkflow : IWorkflow
{
    public static void Execute()
    {
        /*  PHX-11757 - Create Project Workflow  */

        // The very first step in this process is to create the Project itself
        // A unique Title, Aggregation Scheme Id, and HouseholdSetId must be provided 

        // Get a list of all valid Aggregation Schemes
        var aggregationSchemes = AggregationSchemes.GetAggregationSchemes();
        // Choose the one you would like to use
        int aggregationSchemeId = 8; // The default
        // Select a HouseholdSetId from the valid options in the AggregationScheme
        int householdSetId = 1;
        
        // TODO: Lookup dataset
        int dataSetId = 96;

        /* Just like the Create a New Project window in the Cloud app, we require certain information to create a new
         * project.
         */
        Project project = new Project
        {
            Title = $"PHX-11757 - Test - {Guid.NewGuid()}",
            AggregationSchemeId = aggregationSchemeId,
            HouseholdSetId = householdSetId,
        };
        
        // Call the CreateProject Endpoint to get the rest of the Project information (including the Project's Unique Guid Id)
        project = Projects.Create(project);
        
        // You can see the Project's information at any point:
        var projectInfo = Projects.GetProject(project.Id);
        
/* Once a Project has been created, it needs to be filled with Events */
        
        // Industries are seperated into different Industry Sets
        var industrySets = IndustrySets.GetIndustrySets();
        
        // You need to get an Industry Code for the event (which can be further filtered by Industry Set)
        var industryCodes = IndustryCodes.GetIndustryCodes(aggregationSchemeId, industrySetId: null);
        
        // Now we can create an event. There are many types of event
        // PHX-11909 - Get Event Types
        
        // We're going to use a very simple one, Industry Output
        var industryOutputEvent = new IndustryOutputEvent()
        {
            Title = "Industry Output",
            Output = 100_000.00,
            IndustryCode = 1,
            Employment = 20.25,
            EmployeeCompensation = 50_000.00,
            ProprietorIncome = 3_333.3333,
            Tags = ["testing"],
        };

        // Add the event to the Project we just created -- will return the event with information filled in
        industryOutputEvent = Events.AddEvent(project.Id, industryOutputEvent);
        
        // Can always retrieve the Event's information
        var industryOutputEvent2 = Events.GetEvent<IndustryOutputEvent>(project.Id, industryOutputEvent.Id);
        
        // We can always pull a list of all Project Events to see what we've added
        var projectEvents = Events.GetEvents(project.Id);
        
/*  With events added, it is time to define Group(s) to contain the Event(s) in Region(s)  */
    
        // See this Workflow for Regional Information
        RegionalWorkflow.Execute();

        // Start by defining your Group
        Group group = new Group()
        {
            ProjectId = project.Id,
            Title = "Sample Group 1",
            DatasetId = dataSetId,
            DollarYear = 2024,
        };

        // Every Group is attached to a single Region; indicate HashId, Urid, ModelId, _or_ UserModelId
        // Including excess Regional information can cause mismatch failures        
        group.HashId = "15b869ZOxy";      // Agg 8, DataSet 96, Oregon State
        
        // The Group starts off with Zero events (group.GroupEvents) and can have any number added
        GroupEvent groupEvent = new GroupEvent { EventId = industryOutputEvent.Id };
        group.GroupEvents = [groupEvent];

        // Then you can add the fully-defined Group to the Project, which will fill in other information
        group = Groups.AddGroup(project.Id, group);
        
/*  Now that we have at least one group defined, we can Run the Impact  */

        long impactRunId = Impacts.RunImpact(project.Id);

        // The impact can take a while to run depending on the number of regions, number of events,
        // and whether it is MRIO
        
        // If you need to know when the Impact completes, a small polling loop can be implemented
        bool completed = false;
        while (true)
        {
            // Give the impact 30 more seconds to process
            Thread.Sleep(TimeSpan.FromSeconds(30));
            
            // Check the current status
            string status = Impacts.GetImpactStatus(impactRunId);

            if (string.Equals(status, "Complete", StringComparison.OrdinalIgnoreCase))
                break;
        }

    }
}