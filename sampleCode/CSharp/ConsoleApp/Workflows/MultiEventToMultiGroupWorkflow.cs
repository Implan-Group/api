using ConsoleApp.Endpoints.Events;
using ConsoleApp.Regions;

namespace ConsoleApp.Workflows;

/// <summary>
/// Example workflow for taking multiple Events and assigning each to multiple Groups
/// </summary>
public class MultiEventToMultiGroupWorkflow : IWorkflow
{
    /// <summary>
    /// This example Workflow follows along with `api\impact\workflows\MultiEventToMultiGroup.md`
    /// and expands upon <see cref="CreateProjectWorkflow"/>
    /// </summary>
    public static void Examples()
    {
        /* For an analysis that contains multiple Events, each of which needs to be assigned to multiple Groups,
         * a simple nested loop is the easiest solution.
         *
         * Our hypothetical example here is a Mixed-Use Housing Development
         * Apartments for `Households 15-30k` will be built in the basement, several restaurants on the first floor,
         * and accommodations for `Households 50-70k` above 
         *
         * More details about creating a project and looking up the Ids below can be found in the CreateProjectWorkflow example
         *
         * For this particular example, we will be using some defaults:
         */
        int aggregationSchemeId = 8;    // 546 Un-Aggregated
        int industrySetId = 8;          // 546 Industries
        int dataSetId = 96;             // 2022
        // You will also need the GUID Project Id for the project you're adding the Events/Groups to
        // See the CreateProjectWorkflow for examples on how to create the initial Project
        Guid projectGuid = Guid.Empty;
        
        
        /* Create the Events */
        
        
        // We need the industry code for restaurants first
        IndustryCode[] industryCodes = IndustryCodeEndpoints.GetIndustryCodes(aggregationSchemeId, industrySetId);
        IndustryCode industryCode = industryCodes.First(c => c.Description == "Full-service restaurants");
        // This will be industry code `509 - Full-service restaurants`
         
        // Create our Restaurant output event
        IndustryOutputEvent restaurantOutput = new IndustryOutputEvent
        {
            Title = "Restaurants",
            IndustryCode = industryCode.Code,
            Output = 1_000_000.00,
            DatasetId = dataSetId,
        };
        
        
        // Now we need to create the housing events
        // You need to lookup all the specification codes for Household Income Events
        var householdIncomeSpecifications = SpecificationEndpoints.GetSpecifications(projectGuid, "HouseholdIncome");
        
        // Create the 15-30k Household Event
        HouseholdIncomeEvent firstHouseholdIncomeEvent = new HouseholdIncomeEvent
        {
            Title = "Households 15-30k",
            HouseholdIncomeCode = 10002, // Households 15-30k (spec code from above)
            Value = 25_000.00,
        };
        // Create the 50-70k Household Event
        HouseholdIncomeEvent secondHouseholdIncomeEvent = new HouseholdIncomeEvent
        {
            Title = "Households 50-70k",
            HouseholdIncomeCode = 10005, // Households 50-70k (spec code from above)
            Value = 125_000.00,
        };
        
        
        /* We have created all the Events.
         * By calling the `AddEvent` endpoint, the fully-hydrated Event is returned (including its Id, which will be required)
         * We'll store them to an Array for future processing
         */
        restaurantOutput = EventEndpoints.AddEvent(projectGuid, restaurantOutput);
        firstHouseholdIncomeEvent = EventEndpoints.AddEvent(projectGuid, firstHouseholdIncomeEvent);
        secondHouseholdIncomeEvent = EventEndpoints.AddEvent(projectGuid, secondHouseholdIncomeEvent);
        
        Event[] events = [restaurantOutput, firstHouseholdIncomeEvent, secondHouseholdIncomeEvent];
        
        
        /* Now we need to create our Groups.
         * For this example, we're comparing the impacts of these Events on several different states
         */
        var states = RegionEndpoints.GetRegionChildren(aggregationSchemeId, dataSetId, regionType: "State");
        var oregon = states.First(s => s.Description == "Oregon");
        var wisconsin = states.First(s => s.Description == "Wisconsin");
        var northCarolina = states.First(s => s.Description == "North Carolina");
        // We'll store these in an array for later use
        Region[] regions = [oregon, wisconsin, northCarolina];
        
        
        // Now, for each Region
        foreach (Region region in regions)
        {
            // Create a Group for that Region
            Group stateGroup = new Group
            {
                ProjectId = projectGuid,
                Title = $"{region.Description} State",  // each Group has to have a different Title
                DatasetId = dataSetId,
                DollarYear = 2024,                      // latest year
                HashId = region.HashId,                 // associate this Region with this Group
            };
            
            // Add all of our Events to this Group
            stateGroup.GroupEvents = events.Select(e => new GroupEvent(e.Id)).ToArray();
            
            // Save the Group to the Project
            stateGroup = GroupEndpoints.AddGroupToProject(projectGuid, stateGroup);
        }

        
        // Now that the Events and Groups have been added, see below
        RunImpactAnalysisWorkflow.ProjectId = projectGuid;
        RunImpactAnalysisWorkflow.Examples();
        // for ways to run an Analysis and view the Results
    }
}