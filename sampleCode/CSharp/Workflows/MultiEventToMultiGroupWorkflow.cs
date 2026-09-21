using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 6: MultiEventToMultiGroup.
/// </summary>
/// <remarks>
/// Goal: apply the same set of events to several regions at once.
///
/// This is the shape most real analyses take. A mixed-use development has
/// restaurants on the ground floor and two bands of apartments above it, and the
/// question is which of three states to build it in. That is three events and three
/// groups, with every event in every group, and the answer falls out of the results
/// filtered by region.
///
/// The pattern is a nested loop: create each event once, then create one group per
/// region holding all of them. Events are owned by the project, not by a group, so
/// they are created once and referenced many times.
///
/// Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
/// </remarks>
public static class MultiEventToMultiGroupWorkflow
{
    /// <summary>The states to compare. Change this list to compare different ones.</summary>
    private static readonly string[] TargetStates = ["Oregon", "Wisconsin", "North Carolina"];

    /// <summary>The restaurants on the ground floor, by name rather than by code.</summary>
    private const string RestaurantIndustry = "Full-service restaurants";

    /// <summary>
    /// The two household income brackets, by specification code. These are checked
    /// against the project's own specification list in step 4 rather than trusted.
    /// </summary>
    private static readonly (int Code, string Label, double Value)[] HouseholdBrackets =
    [
        (10002, "Households 15-30k", 25_000.00),
        (10005, "Households 50-70k", 125_000.00),
    ];

    public static Project Run(Guid? projectId = null)
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve the identifiers.
        ConsoleLog.Heading("Step 1: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. Get a project to work in. An existing empty one can be passed in;
        // otherwise one is created here.
        ConsoleLog.Heading("Step 2: the Project");
        Project project;
        if (projectId is null)
        {
            // POST /api/v1/impact/project  (wiki: Create Project)
            project = Projects.CreateProject(client, new Project
            {
                Title = Config.UniqueTitle("Multi Event Multi Group"),
                AggregationSchemeId = ids.AggregationSchemeId,
                HouseholdSetId = ids.HouseholdSetId,
            });
            ConsoleLog.Info("  created {0}", project.Describe());
        }
        else
        {
            // GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
            project = Projects.GetProject(client, projectId.Value);
            ConsoleLog.Info("  using existing {0}", project.Describe());
        }

        var id = project.Id!.Value;

        // Step 3. The restaurant event needs an industry code.
        ConsoleLog.Heading("Step 3: find the restaurant industry");

        // GET /api/v1/IndustryCodes/{aggregationSchemeId}
        // (wiki: Industry Codes by Aggregation Scheme)
        var codes = Industries.GetIndustryCodesForScheme(client, ids.AggregationSchemeId);
        var restaurants = Industries.FindIndustryByDescription(codes, RestaurantIndustry);
        ConsoleLog.Info("  {0} is code {1} here", restaurants.Description, restaurants.Code);
        ConsoleLog.Info("  (it is a different code in other Industry Sets, which is why this");
        ConsoleLog.Info("   sample looks it up by name)");

        // Step 4. Household Income events take a specification code rather than an
        // industry code, so read the valid ones for this project first.
        ConsoleLog.Heading("Step 4: read the Household Income specification codes");

        // GET /api/v1/impact/project/{projectId}/eventtype/HouseholdIncome/specification
        // (wiki: Get Event Specifications)
        var specifications = Events.GetEventSpecifications(client, id, EventTypes.HouseholdIncome);
        var available = specifications.ToDictionary(s => s.Code, s => s.Name);
        ConsoleLog.Info("  {0} income brackets available:", specifications.Count);
        foreach (var specification in specifications)
            ConsoleLog.Info("    {0}", specification.Name);

        foreach (var (code, label, _) in HouseholdBrackets)
        {
            if (!available.ContainsKey(code.ToString()))
            {
                throw new KeyNotFoundException(
                    $"Household income code {code} ({label}) is not valid for this Project. "
                    + $"Available codes: {string.Join(", ", available.Keys.Order())}.");
            }
        }

        // Step 5. Create the events. Each one is created once and will be referenced
        // by all three groups.
        ConsoleLog.Heading("Step 5: add the Events");
        var created = new List<ImpactEvent>();

        // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        var restaurantEvent = Events.CreateEvent(client, id, new IndustryOutputEvent
        {
            Title = Config.UniqueTitle("Restaurants"),
            IndustryCode = restaurants.Code,
            Output = 1_000_000.00,
        });
        created.Add(restaurantEvent);
        ConsoleLog.Info("  {0}", restaurantEvent.Describe());

        foreach (var (code, label, value) in HouseholdBrackets)
        {
            var householdEvent = Events.CreateEvent(client, id, new HouseholdIncomeEvent
            {
                Title = Config.UniqueTitle(label),
                HouseholdIncomeCode = code,
                Value = value,
            });
            created.Add(householdEvent);
            ConsoleLog.Info("  {0}", householdEvent.Describe());
        }

        // Step 6. Find the states.
        ConsoleLog.Heading("Step 6: find the Regions");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
        // (wiki: Regional Children)
        var states = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: RegionType.State);
        var chosen = TargetStates.Select(name => Regions.FindByDescription(states, name)).ToList();
        foreach (var state in chosen)
            ConsoleLog.Info("  {0}", state.Describe());

        // Step 7. One group per region, each holding every event. This is the nested
        // loop the workflow exists to show: events on the inside, regions on the
        // outside, and the group titles distinct.
        ConsoleLog.Heading("Step 7: one Group per Region, each holding every Event");
        var dollarYear = Config.CurrentDollarYear;
        var eventLinks = created.Select(e => new GroupEvent { EventId = e.Id!.Value }).ToList();

        foreach (var state in chosen)
        {
            // POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
            var group = Groups.CreateGroup(client, id, new Group
            {
                // Group titles have to be distinct within a project.
                Title = Config.UniqueTitle(state.Description),
                HashId = state.HashId,
                DatasetId = ids.DatasetId,
                DollarYear = dollarYear,
                GroupEvents = eventLinks,
            });
            ConsoleLog.Info("  {0}", group.Describe());
        }

        // Step 8. Read it back.
        ConsoleLog.Heading("Step 8: read the Groups back");

        // GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
        var allGroups = Groups.GetGroups(client, id);
        ConsoleLog.Info("  {0} groups, each with {1} events", allGroups.Count, created.Count);

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Project id: {0}", id);
        ConsoleLog.Info("{0} events across {1} groups", created.Count, allGroups.Count);
        ConsoleLog.Info();
        ConsoleLog.Info("Run it, then filter the results by region to compare the states:");
        ConsoleLog.Info("  dotnet run -- run-impact-analysis --project-id {0}", id);
        return project;
    }
}
