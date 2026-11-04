using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 12: AdvancedEvents.
/// </summary>
/// <remarks>
/// Goal: the two event types analysts reach for after Industry Output, plus tags and
/// tag-filtered results.
///
/// Industry Output answers "what if this new activity arrived?". Two other types
/// answer different questions:
///
///   - Industry Contribution Analysis asks how much of the economy already rests on
///     an industry that is there now. It constrains the industry from buying from
///     itself, so its own output is not counted twice. Use it for "the hotel
///     industry contributes X to this county", never for a new hotel.
///
///   - Industry Spending Pattern models a buyer rather than a producer. It spends
///     money through an industry's supply chain without adding any direct output,
///     which is what you want for an organization whose own output is not the thing
///     being measured. Its commodity list can be read, edited, and sent back, which
///     this workflow demonstrates.
///
/// Tags tie it together. Both events are tagged, and the results are read once per
/// tag, so a single run answers two questions separately.
///
/// Support: ICA: Introduction to Industry Contribution Analysis
/// https://support.implan.com/hc/en-us/articles/360025854654
/// Support: Industry Spending Pattern Events
/// https://support.implan.com/hc/en-us/articles/360052212933
/// Support: Event Tags
/// https://support.implan.com/hc/en-us/articles/4407853242139
/// </remarks>
public static class AdvancedEventsWorkflow
{
    private const string RegionName = "Oregon";
    private const string ContributionIndustry = "Full-service restaurants";
    private const string SpendingIndustry = "Oilseed farming";

    // The tags each event carries. Results are filtered by these at the end.
    private const string ContributionTag = "contribution";
    private const string SpendingTag = "spending";

    private const double EventValue = 1_000_000.00;

    public static long Run()
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve identifiers.
        ConsoleLog.Heading("Step 1: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. Create the project and confirm both event types are available.
        ConsoleLog.Heading("Step 2: create the Project");

        // POST /api/v1/impact/project  (wiki: Create Project)
        var project = Projects.CreateProject(client, new Project
        {
            Title = Config.UniqueTitle("Advanced Events"),
            AggregationSchemeId = ids.AggregationSchemeId,
            HouseholdSetId = ids.HouseholdSetId,
        });
        ConsoleLog.Info("  {0}", project.Describe());

        var projectId = project.Id!.Value;

        // GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
        var accepted = Events.GetEventTypes(client, projectId);
        foreach (var required in new[] { EventTypes.IndustryContributionAnalysis, EventTypes.IndustrySpendingPattern })
        {
            if (!accepted.Contains(required))
            {
                throw new InvalidOperationException(
                    $"{required} is not available in this Project's Aggregation Scheme. "
                    + $"Available types: {string.Join(", ", accepted)}");
            }
        }

        ConsoleLog.Info("  both event types are available here");

        // GET /api/v1/IndustryCodes/{aggregationSchemeId}
        // (wiki: Industry Codes by Aggregation Scheme)
        var codes = Industries.GetIndustryCodesForScheme(client, ids.AggregationSchemeId);

        // Step 3. The contribution event. The value is a dollar figure, and it must
        // not exceed the industry's total output in the region; setting
        // IsOutputPercentage instead lets you give a share from 0 to 1, which avoids
        // having to know that total.
        ConsoleLog.Heading("Step 3: an Industry Contribution Analysis event");
        var contributionIndustry = Industries.FindIndustryByDescription(codes, ContributionIndustry);
        ConsoleLog.Info("  {0} is code {1} here",
            contributionIndustry.Description, contributionIndustry.Code);

        // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        var contributionEvent = Events.CreateEvent(client, projectId, new IndustryContributionAnalysisEvent
        {
            Title = Config.UniqueTitle("Restaurant contribution"),
            IndustryCode = contributionIndustry.Code,
            Output = EventValue,
            IsOutputPercentage = false,
            Tags = [ContributionTag],
        });
        ConsoleLog.Info("  {0}", contributionEvent.Describe());
        ConsoleLog.Info("  tagged '{0}'", ContributionTag);

        // Step 4. Read a default spending pattern, so it can be edited rather than
        // invented. The pattern is a list of commodities and the share of each
        // dollar that goes to them, summing to 1.
        ConsoleLog.Heading("Step 4: read a default spending pattern");
        var spendingIndustry = Industries.FindIndustryByDescription(codes, SpendingIndustry);

        // GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/Industry/{industryCode}
        // (wiki: Spending Pattern by Id)
        var commodities = Events.GetSpendingPattern(
            client,
            ids.AggregationSchemeId,
            spendingIndustry.Code,
            SpendingPatternType.Industry,
            ids.DatasetId);

        ConsoleLog.Info("  {0} buys {1} commodities", spendingIndustry.Description, commodities.Count);

        if (commodities.Count == 0)
        {
            throw new InvalidOperationException(
                $"No default spending pattern for industry {spendingIndustry.Code} in Dataset {ids.DatasetId}.");
        }

        var ranked = commodities.OrderByDescending(c => c.Coefficient ?? 0).ToList();
        ConsoleLog.Info("  the five largest:");
        foreach (var commodity in ranked.Take(5))
            ConsoleLog.Info("    {0}", commodity.Describe());

        // Step 5. Edit one coefficient. Marking it IsUserCoefficient tells IMPLAN the
        // number is yours and not its own, which is what makes the change visible in
        // the project and in the results.
        ConsoleLog.Heading("Step 5: change one coefficient");
        var target = ranked[0];
        var original = target.Coefficient ?? 0.0;
        target.Coefficient = Math.Round(original * 1.10, 6);
        target.IsUserCoefficient = true;
        ConsoleLog.Info("  {0}: {1:F6} -> {2:F6}",
            target.CommodityDescription, original, target.Coefficient);
        ConsoleLog.Info("  (the rest of the pattern is sent back unchanged)");

        // Step 6. The spending-pattern event, carrying the edited list.
        ConsoleLog.Heading("Step 6: an Industry Spending Pattern event");

        // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
        var spendingEvent = Events.CreateEvent(client, projectId, new IndustrySpendingPatternEvent
        {
            Title = Config.UniqueTitle("Supplier spending"),
            IndustryCode = spendingIndustry.Code,
            Output = EventValue,
            // Spend the whole value across the pattern rather than taking a share of
            // it as gross absorption first.
            SpendingPatternValueType = SpendingPatternValueType.IntermediateExpenditure,
            SpendingPatternDatasetId = ids.DatasetId,
            SpendingPatternCommodities = commodities,
            Tags = [SpendingTag],
        });
        ConsoleLog.Info("  {0}", spendingEvent.Describe());
        ConsoleLog.Info("  tagged '{0}'", SpendingTag);

        // Step 7. One group holding both events.
        ConsoleLog.Heading("Step 7: one Group holding both events");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
        // (wiki: Regional Children)
        var states = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: RegionType.State);
        var region = Regions.FindByDescription(states, RegionName);

        // POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
        var group = Groups.CreateGroup(client, projectId, new Group
        {
            Title = Config.UniqueTitle(RegionName),
            HashId = region.HashId,
            DatasetId = ids.DatasetId,
            DollarYear = Config.CurrentDollarYear,
            GroupEvents =
            [
                new GroupEvent { EventId = contributionEvent.Id!.Value },
                new GroupEvent { EventId = spendingEvent.Id!.Value },
            ],
        });
        ConsoleLog.Info("  {0}", group.Describe());

        // Step 8. Run it.
        ConsoleLog.Heading("Step 8: run the impact");

        // POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
        var runId = Impacts.RunImpact(client, projectId);
        ConsoleLog.Info("  run id {0}", runId);

        // GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
        Impacts.WaitForImpact(client, runId);
        ConsoleLog.Info("  complete");

        // Step 9. Read the results once per tag. This is what tags are for: two
        // questions answered from one run, each read separately.
        ConsoleLog.Heading("Step 9: read the results, filtered by tag");
        var destination = Path.Combine(Config.ReportsDirectory, $"Advanced Events-{runId}");
        var dollarYear = Config.CurrentDollarYear;

        foreach (var tag in new[] { ContributionTag, SpendingTag })
        {
            var filters = new ResultFilters { Year = dollarYear, EventTags = [tag] };

            // GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?eventTags=...
            // (wiki: Results - Summary Economic Indicators)
            var csv = ImpactResults.GetSummaryEconomicIndicators(client, runId, filters);
            ImpactResults.SaveCsv(csv,
                Path.Combine(destination, $"Summary Economic Indicators - {tag}.csv"));

            var rows = csv.Split('\n').Count(line => line.Trim().Length > 0);
            ConsoleLog.Info("  tag '{0}': {1} data rows", tag, Math.Max(rows - 1, 0));
        }

        // The same filter, in the shape the growth report wants: a JSON body on a
        // GET, with every list present.
        var growthRequest = new ImpactResultsExportRequest
        {
            DollarYear = dollarYear,
            EventTags = [SpendingTag],
        };

        // GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
        // (wiki: Results - Estimated Growth Percentage)
        var growthCsv = ImpactResults.GetEstimatedGrowthPercentage(client, runId, growthRequest);
        ImpactResults.SaveCsv(growthCsv,
            Path.Combine(destination, $"Estimated Growth Percentage - {SpendingTag}.csv"));

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Project id: {0}", projectId);
        ConsoleLog.Info("Run id:     {0}", runId);
        ConsoleLog.Info("Reports:    {0}", destination);
        ConsoleLog.Info();
        ConsoleLog.Info("Each tagged report holds only its own event, from one run. Tag");
        ConsoleLog.Info("events by what they represent, for example capital against");
        ConsoleLog.Info("operations, and one project answers several questions.");
        return runId;
    }
}
