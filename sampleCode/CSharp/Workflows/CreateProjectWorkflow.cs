using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 5: CreateProject.
/// </summary>
/// <remarks>
/// Goal: the shortest path from nothing to a project that can be run.
///
/// Four things have to exist, in this order, and each depends on the one before:
///
///   1. A Project, which fixes the Aggregation Scheme and Household Set.
///   2. Events, which say what changed.
///   3. A Region to apply them to.
///   4. A Group, which pairs that region and a dollar year with those events.
///
/// Run the RunImpactAnalysis workflow afterwards to analyze what this creates.
///
/// The workflow takes a map code, so the same code builds a United States,
/// Canadian, or international project. Only the resolved ids and the region differ.
///
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
/// Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
/// </remarks>
public static class CreateProjectWorkflow
{
    /// <summary>
    /// The industry the events use, by name rather than by code, because the code
    /// differs between Industry Sets.
    /// </summary>
    private const string IndustryName = "Oilseed farming";

    /// <summary>
    /// Which region to put the group in, per map code. International schemes have no
    /// state level, so a country is used there.
    /// </summary>
    private static readonly Dictionary<MapCode, (string Name, RegionType Type)> DefaultRegion = new()
    {
        [MapCode.US] = ("Oregon", RegionType.State),
        [MapCode.CAN] = ("Ontario", RegionType.State),
        [MapCode.INTL] = ("Canada", RegionType.Country),
    };

    public static Project Run(MapCode mapCode = MapCode.US)
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve the ids. The Household Set comes from the scheme rather
        // than being assumed to be 1, because it differs by country.
        ConsoleLog.Heading("Step 1: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, mapCode);

        // Step 2. Create the project. The scheme and household set are fixed here
        // and cannot be changed afterwards.
        ConsoleLog.Heading("Step 2: create the Project");

        // POST /api/v1/impact/project  (wiki: Create Project)
        var project = Projects.CreateProject(client, new Project
        {
            Title = Config.UniqueTitle("Create Project"),
            AggregationSchemeId = ids.AggregationSchemeId,
            HouseholdSetId = ids.HouseholdSetId,
        });
        ConsoleLog.Info("  {0}", project.Describe());

        var projectId = project.Id!.Value;

        // Step 3. Ask the project which event types it accepts. The answer depends
        // on the Aggregation Scheme, so asking beats assuming.
        ConsoleLog.Heading("Step 3: which event types this Project accepts");

        // GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
        var accepted = Events.GetEventTypes(client, projectId);
        ConsoleLog.Info("  {0}", string.Join(", ", accepted));

        // Step 4. Find the industry. By name, then confirm the code, which is the
        // habit that stops a sample from quietly analyzing the wrong industry.
        ConsoleLog.Heading("Step 4: find the industry");

        // GET /api/v1/IndustryCodes/{aggregationSchemeId}
        // (wiki: Industry Codes by Aggregation Scheme)
        var codes = Industries.GetIndustryCodesForScheme(client, ids.AggregationSchemeId);
        var industry = Industries.FindIndustryByDescription(codes, IndustryName);
        ConsoleLog.Info("  {0} is code {1} in this Industry Set", industry.Description, industry.Code);

        // Step 5. Add the events.
        ConsoleLog.Heading("Step 5: add the Events");

        // The simple case: one number and the industry that earned it. IMPLAN
        // estimates employment, compensation, and the rest from regional averages.
        // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        // Re-assign from the response: it comes back with the generated id and with
        // everything IMPLAN estimated.
        var outputEvent = Events.CreateEvent(client, projectId, new IndustryOutputEvent
        {
            Title = Config.UniqueTitle("Industry Output"),
            IndustryCode = industry.Code,
            Output = 1_000_000.00,
        });
        ConsoleLog.Info("  {0}", outputEvent.Describe());

        // The detailed case, when you have the operating statement rather than one
        // total. Only available in domestic schemes, so it is skipped elsewhere.
        ImpactEvent? detailedEvent = null;
        if (accepted.Contains(EventTypes.IndustryImpactAnalysis))
        {
            detailedEvent = Events.CreateEvent(client, projectId, new IndustryImpactAnalysisEvent
            {
                Title = Config.UniqueTitle("Industry Impact Analysis"),
                IndustryCode = industry.Code,
                IntermediateInputs = 500_000.00,
                EmployeeCompensation = 250_000.00,
                ProprietorIncome = 50_000.00,
                WageAndSalaryEmployment = 4,
                ProprietorEmployment = 1,
                TotalEmployment = 5,
                TotalLaborIncome = 300_000.00,
                OtherPropertyIncome = 100_000.00,
                TaxOnProductionAndImports = 100_000.00,
                LocalPurchasePercentage = 1.0,
                // Which data year's spending pattern the intermediate inputs flow
                // through. The resolved dataset keeps this consistent with the project.
                SpendingPatternDatasetId = ids.DatasetId,
                SpendingPatternValueType = SpendingPatternValueType.IntermediateExpenditure,
            });
            ConsoleLog.Info("  {0}", detailedEvent.Describe());
        }
        else
        {
            ConsoleLog.Info("  Industry Impact Analysis is not available in a {0} scheme; skipping it", mapCode);
        }

        // Step 6. Find the region the group will use.
        ConsoleLog.Heading("Step 6: find the Region");
        var (regionName, regionType) = DefaultRegion[mapCode];

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
        // (wiki: Regional Children)
        // Passing no parent means "children of the top-level region". That works for
        // international schemes too, which have no top-level region of their own:
        // ask for Country there and the countries come back.
        var candidates = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: regionType);
        var region = Regions.FindByDescription(candidates, regionName);
        ConsoleLog.Info("  {0}", region.Describe());

        // Step 7. Create the group. This is where the events, the region, and the
        // dollar year come together.
        ConsoleLog.Heading("Step 7: add the Group");
        var eventLinks = new List<GroupEvent> { new() { EventId = outputEvent.Id!.Value } };
        if (detailedEvent is not null)
            eventLinks.Add(new GroupEvent { EventId = detailedEvent.Id!.Value });

        // POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
        var group = Groups.CreateGroup(client, projectId, new Group
        {
            Title = Config.UniqueTitle("Group"),
            // Exactly one region identifier. HashId is the one to use.
            HashId = region.HashId,
            DatasetId = ids.DatasetId,
            // Always set this. There is no server-side default, and a group without
            // one produces a run that never attaches.
            DollarYear = Config.CurrentDollarYear,
            GroupEvents = eventLinks,
        });
        ConsoleLog.Info("  {0}", group.Describe());

        // Step 8. Read the project back, to confirm what was built.
        ConsoleLog.Heading("Step 8: read the Project back");

        // GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
        project = Projects.GetProject(client, projectId);
        ConsoleLog.Info("  {0}", project.Describe());
        ConsoleLog.Info("  Aggregation Scheme {0}, Household Set {1}",
            project.AggregationSchemeId, project.HouseholdSetId);

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Project id:  {0}", project.Id);
        ConsoleLog.Info("Event ids:   {0}", string.Join(", ",
            new[] { outputEvent, detailedEvent }.Where(e => e is not null).Select(e => e!.Id)));
        ConsoleLog.Info("Group id:    {0}", group.Id);
        ConsoleLog.Info();
        ConsoleLog.Info("Run it with the RunImpactAnalysis workflow:");
        ConsoleLog.Info("  dotnet run -- run-impact-analysis --project-id {0}", project.Id);
        ConsoleLog.Info();
        ConsoleLog.Info("Delete it from Projects in IMPLAN Cloud when you are done.");
        return project;
    }
}
