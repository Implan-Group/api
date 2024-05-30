using ConsoleApp.Endpoints;

namespace ConsoleApp.Workflows;

public class CreateProjectWorkflow : IWorkflow
{
    public static void Execute()
    {
        /*  PHX-11757 - Create Project Workflow  ***REMOVED***

        // The very first step in this process is to create the Project itself
        // A unique Title, Aggregation Scheme Id, and HouseholdSetId must be provided 

        // Get a list of all valid Aggregation Schemes
        var aggregationSchemes = AggregationSchemes.GetAggregationSchemes();
        // Choose the one you would like to use
        int aggregationSchemeId = 8; // The default
        // Select a HouseholdSetId from the valid options in the AggregationScheme
        int householdSetId = 1;

        // Create the Project object
        Project project = new Project
        {
            Title = $"PHX-11757 - Test - {Guid.NewGuid()}",
            AggregationSchemeId = aggregationSchemeId,
            HouseholdSetId = householdSetId,
        };
        
        // Call the CreateProject Endpoint to get the rest of the Project information (including the Project's Unique Guid Id)
        project = Projects.Create(project);
        
        // You can verify the Project's information at any point:
        var projectInfo = Projects.GetProject(project.Id);
        
        /* Once a Project has been created, it needs to be filled with Events ***REMOVED***
        
        // Industries are seperated into different Industry Sets
        var industrySets = IndustrySets.GetIndustrySets();
        
        // You need to get an Industry Code for the event (which can be further filtered by Industry Set)
        var industryCodes = IndustryCodes.GetIndustryCodes(aggregationSchemeId, industrySetId: null);
        
        // Now we can create an event. There are many types of event
        // PHX-11909
        
        // We're going to use a very simple one, Industry Output
        var industryOutputEvent = new IndustryOutputEvent()
        {
            Title = "Industry Output",
            Output = 100_000.00,
            IndustryCode = 1, // See IndustryCodes
            Employment = 20.25,
            EmployeeCompensation = 50_000.23,
            ProprietorIncome = 3_400.233,
        };
    }
}