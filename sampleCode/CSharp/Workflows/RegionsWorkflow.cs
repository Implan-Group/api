using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 3: Regions.
/// </summary>
/// <remarks>
/// Goal: navigate the region hierarchy and find the regions an analysis will use.
///
/// Regions nest. For a United States scheme the top-level region is the country,
/// its children are the states, and a state's children are its counties, MSAs, and
/// congressional districts. The filter reaches down through that hierarchy, so
/// asking a state for ZIP codes works even though ZIP codes are children of
/// counties.
///
/// A region is identified by its HashId, and that identifier is specific to one
/// Aggregation Scheme and one Dataset. The same county has a different HashId in a
/// different scheme or data year, so never carry one between them.
///
/// Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
/// </remarks>
public static class RegionsWorkflow
{
    /// <summary>
    /// The states the later workflows use. Looked up by description so the sample
    /// does not depend on a HashId that changes with the data year.
    /// </summary>
    public static readonly string[] TargetStates = ["Oregon", "Wisconsin", "North Carolina"];

    public static void Run()
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve the scheme and dataset. Region identifiers only mean
        // something inside these two, so they come first.
        ConsoleLog.Heading("Step 1: resolve the Aggregation Scheme and Dataset");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. The top of the hierarchy. For a US scheme this is the country.
        ConsoleLog.Heading("Step 2: the top-level region");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}
        // (wiki: Regions - Top Level)
        var country = Regions.GetTopLevelRegion(client, ids.AggregationSchemeId, ids.DatasetId);
        ConsoleLog.Info("  {0}", country.Describe());
        ConsoleLog.Info("  employment {0:N0}    output {1:N0}", country.Employment ?? 0, country.Output ?? 0);
        ConsoleLog.Info("  International schemes have no top-level region and answer 422 here;");
        ConsoleLog.Info("  start from the country children instead.");

        // Step 3. The states. No parent region means "children of the top-level
        // region", so this is every state in the country.
        ConsoleLog.Heading("Step 3: the states");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
        // (wiki: Regional Children)
        var states = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: RegionType.State);
        ConsoleLog.Info("  {0} states and equivalents", states.Count);

        // Find the three the other workflows use. Matching on description rather
        // than on a HashId is what keeps these samples working across data years.
        foreach (var name in TargetStates)
            ConsoleLog.Info("    {0}", Regions.FindByDescription(states, name).Describe());

        // Step 4. One level further down. Counties are children of a state.
        ConsoleLog.Heading("Step 4: the counties inside one state");
        var oregon = Regions.FindByDescription(states, "Oregon");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children?regionTypeFilter=County
        // (wiki: Regional Children)
        var counties = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, oregon.HashId, RegionType.County);
        ConsoleLog.Info("  {0} counties in {1}", counties.Count, oregon.Description);
        foreach (var county in counties.Take(5))
            ConsoleLog.Info("    {0}", county.Describe());
        if (counties.Count > 5)
            ConsoleLog.Info("    ... and {0} more", counties.Count - 5);

        ConsoleLog.Info();
        ConsoleLog.Info("  Every region above carries its own model build status, so this one");
        ConsoleLog.Info("  call tells you both which regions exist and which are ready to use.");
        ConsoleLog.Info("  {0} of {1} counties are built", counties.Count(c => c.IsBuilt), counties.Count);

        // Step 5. Read one region on its own, by HashId.
        ConsoleLog.Heading("Step 5: read one region by HashId");
        var lane = Regions.FindByDescription(counties, "Lane County, OR");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}
        // (wiki: Get Region by Id)
        var laneAgain = Regions.GetRegion(client, ids.AggregationSchemeId, ids.DatasetId, lane.HashId);
        ConsoleLog.Info("  {0}", laneAgain.Describe());
        ConsoleLog.Info("  MRIO allowed: {0}", laneAgain.IsMrioAllowed);

        // Step 6. Your own regions: the ones you combined or customized. A fresh
        // account has none, and that is a normal result rather than an error.
        ConsoleLog.Heading("Step 6: your combined and customized regions");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
        // (wiki: Get User Regions by Aggregation Scheme)
        var userRegions = Regions.GetUserRegionsForScheme(client, ids.AggregationSchemeId, ids.DatasetId);
        if (userRegions.Count > 0)
        {
            ConsoleLog.Info("  {0} of your own regions in this scheme and dataset:", userRegions.Count);
            foreach (var region in userRegions.Take(10))
                ConsoleLog.Info("    {0}", region.Describe());
            if (userRegions.Count > 10)
                ConsoleLog.Info("    ... and {0} more", userRegions.Count - 10);

            // GET /api/v1/region/user/{hashId}  (wiki: Get User Region)
            // Reading one is faster than the list and is what to poll while a region
            // builds.
            var one = Regions.GetUserRegion(client, userRegions[0].HashId);
            if (one is not null)
                ConsoleLog.Info("  read back one by HashId: {0}", one.Describe());
        }
        else
        {
            ConsoleLog.Info("  none yet. The CombineRegions workflow creates one.");
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("HashIds from this run are good for Aggregation Scheme {0} and",
            ids.AggregationSchemeId);
        ConsoleLog.Info("Dataset {0} only. Look them up again for any other combination.", ids.DatasetId);
    }
}
