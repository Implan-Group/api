using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 11: MrioProject.
/// </summary>
/// <remarks>
/// Goal: multi-regional input-output analysis, where activity in one region shows up
/// as effects in another.
///
/// An ordinary project treats each of its regions in isolation. Build a factory in
/// Oregon and the results show Oregon's supply chain; anything the factory buys from
/// Wisconsin leaks out of the model and is never counted. That is usually the wrong
/// answer when the regions are economically linked.
///
/// MRIO keeps the link. With <c>isMrio</c> set on the project, IMPLAN traces demand
/// from one region into the others in the same project, so Wisconsin shows indirect
/// and induced effects from an event that only happened in Oregon.
///
/// The shape is:
///
///   - One project, with <c>IsMrio</c> set to true.
///   - One event, in one region.
///   - A group per region, including the region with no activity of its own. That
///     group exists so there is somewhere for the spillover to be reported.
///
/// Reading the results filtered by region is what makes the point: Wisconsin's
/// numbers are non-zero although nothing was built there.
///
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// Support: MRIO: Introduction to Multi-Regional Input-Output Analysis
/// https://support.implan.com/hc/en-us/articles/115009713448
/// </remarks>
public static class MrioProjectWorkflow
{
    /// <summary>The region the event happens in.</summary>
    private const string SourceRegion = "Oregon";

    /// <summary>The region that should show spillover.</summary>
    private const string LinkedRegion = "Wisconsin";

    /// <summary>An industry with a wide supply chain, so the cross-region effect is visible.</summary>
    private const string IndustryName = "Full-service restaurants";

    private const double EventOutput = 10_000_000.00;

    public static long Run()
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve identifiers.
        ConsoleLog.Heading("Step 1: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. Find both regions, and check each allows MRIO. Not every region
        // does, and finding out here is better than after a run produces nothing.
        ConsoleLog.Heading("Step 2: find the regions and check they allow MRIO");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
        // (wiki: Regional Children)
        var states = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: RegionType.State);

        var source = Regions.FindByDescription(states, SourceRegion);
        var linked = Regions.FindByDescription(states, LinkedRegion);

        foreach (var region in new[] { source, linked })
        {
            ConsoleLog.Info("  {0}  MRIO allowed: {1}", region.Describe(), region.IsMrioAllowed);
            if (!region.IsMrioAllowed)
            {
                throw new InvalidOperationException(
                    $"{region.Description} cannot take part in an MRIO analysis. Pick a different region.");
            }
        }

        // Step 3. Create the project with MRIO switched on. This is the one flag
        // that separates this workflow from CreateProject, and it cannot be changed
        // later.
        ConsoleLog.Heading("Step 3: create the Project with MRIO enabled");

        // POST /api/v1/impact/project  (wiki: Create Project)
        var project = Projects.CreateProject(client, new Project
        {
            Title = Config.UniqueTitle("MRIO"),
            AggregationSchemeId = ids.AggregationSchemeId,
            HouseholdSetId = ids.HouseholdSetId,
            IsMrio = true,
        });
        ConsoleLog.Info("  {0}", project.Describe());
        ConsoleLog.Info("  isMrio: {0}", project.IsMrio);

        var projectId = project.Id!.Value;

        // Step 4. One event, in the source region only.
        ConsoleLog.Heading("Step 4: add one Event");

        // GET /api/v1/IndustryCodes/{aggregationSchemeId}
        // (wiki: Industry Codes by Aggregation Scheme)
        var codes = Industries.GetIndustryCodesForScheme(client, ids.AggregationSchemeId);
        var industry = Industries.FindIndustryByDescription(codes, IndustryName);

        // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        var impactEvent = Events.CreateEvent(client, projectId, new IndustryOutputEvent
        {
            Title = Config.UniqueTitle($"Restaurants in {SourceRegion}"),
            IndustryCode = industry.Code,
            Output = EventOutput,
        });
        ConsoleLog.Info("  {0}", impactEvent.Describe());
        ConsoleLog.Info("  {0:C0} output in {1}", EventOutput, SourceRegion);

        // Step 5. Two groups. The source group holds the event. The linked group
        // holds the same event too, scaled to almost nothing.
        //
        // On that scaling: a group with no events at all is the cleaner
        // illustration, but the API requires a group to carry at least one event, so
        // the linked region gets the event at a negligible scaling factor. Its own
        // direct effect is therefore near zero, and essentially everything reported
        // for it is spillover from the source region, which is the effect this
        // workflow exists to show.
        ConsoleLog.Heading("Step 5: a Group for each region");
        var dollarYear = Config.CurrentDollarYear;

        // POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
        var sourceGroup = Groups.CreateGroup(client, projectId, new Group
        {
            Title = Config.UniqueTitle(SourceRegion),
            HashId = source.HashId,
            DatasetId = ids.DatasetId,
            DollarYear = dollarYear,
            GroupEvents = [new GroupEvent { EventId = impactEvent.Id!.Value }],
        });
        ConsoleLog.Info("  {0}", sourceGroup.Describe());

        var linkedGroup = Groups.CreateGroup(client, projectId, new Group
        {
            Title = Config.UniqueTitle(LinkedRegion),
            HashId = linked.HashId,
            DatasetId = ids.DatasetId,
            DollarYear = dollarYear,
            GroupEvents = [new GroupEvent { EventId = impactEvent.Id!.Value, ScalingFactor = 0.01 }],
        });
        ConsoleLog.Info("  {0}  (event scaled to 0.01)", linkedGroup.Describe());

        // Step 6. Run it.
        ConsoleLog.Heading("Step 6: run the impact");

        // POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
        var runId = Impacts.RunImpact(client, projectId);
        ConsoleLog.Info("  run id {0}", runId);

        // GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
        Impacts.WaitForImpact(client, runId);
        ConsoleLog.Info("  complete");

        // Step 7. Read the results once per region. The filter is what separates the
        // two, and comparing them is the point of the workflow.
        ConsoleLog.Heading("Step 7: read the results region by region");
        var destination = Path.Combine(Config.ReportsDirectory, $"MRIO-{runId}");

        foreach (var region in new[] { source, linked })
        {
            var filters = new ResultFilters
            {
                Year = dollarYear,
                Regions = [region.Description],
            };

            // GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?regions=...
            // (wiki: Results - Summary Economic Indicators)
            var csv = ImpactResults.GetSummaryEconomicIndicators(client, runId, filters);
            var path = ImpactResults.SaveCsv(csv,
                Path.Combine(destination, $"Summary Economic Indicators - {region.Description}.csv"));

            // Count the data rows so the console says something useful without
            // trying to parse a report whose columns vary by account.
            var rows = csv.Split('\n').Count(line => line.Trim().Length > 0);
            ConsoleLog.Info("  {0}: {1} rows in {2}",
                region.Description, Math.Max(rows - 1, 0), Path.GetFileName(path));
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Project id: {0}", projectId);
        ConsoleLog.Info("Run id:     {0}", runId);
        ConsoleLog.Info("Reports:    {0}", destination);
        ConsoleLog.Info();
        ConsoleLog.Info("Compare the two files. {0} carries indirect and induced", LinkedRegion);
        ConsoleLog.Info("effects from activity that only happened in {0}. In a project", SourceRegion);
        ConsoleLog.Info("without MRIO those effects leak out of the model and are lost.");
        return runId;
    }
}
