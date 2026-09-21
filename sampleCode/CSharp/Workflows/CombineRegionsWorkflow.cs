using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 4: CombineRegions.
/// </summary>
/// <remarks>
/// Goal: combine two counties into one region and wait for its model to build.
///
/// IMPLAN builds a model for every region it publishes, but a study area is often
/// not one of them: two counties either side of a state line, the six counties a
/// transit authority serves, a metro area plus its exurbs. Combining regions makes
/// one economic region out of several, and the result behaves like any other region
/// afterwards.
///
/// The important part of this workflow is the waiting. The build is asynchronous:
/// the POST returns immediately with the new region at status <c>New</c>, and the
/// model is not usable until that reads <c>Complete</c>. Poll the single-region
/// endpoint for that, and never poll a heavy data export to find out, because those
/// answer with an error until the model is ready and the error looks like a
/// different problem.
///
/// Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
/// Support: Combining Regions
/// https://support.implan.com/hc/en-us/articles/1260805784110
/// </remarks>
public static class CombineRegionsWorkflow
{
    /// <summary>
    /// Two adjacent Oregon counties. They must come from the same dataset, must not
    /// overlap, and must not nest inside one another, so a state and a county within
    /// it would be rejected.
    /// </summary>
    private static readonly string[] CountiesToCombine = ["Lane County, OR", "Douglas County, OR"];

    public static string Run()
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve the scheme and dataset the combined region will belong to.
        ConsoleLog.Heading("Step 1: resolve the Aggregation Scheme and Dataset");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. Find the counties by name and collect their HashIds.
        ConsoleLog.Heading("Step 2: find the regions to combine");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=County
        // (wiki: Regional Children)
        var allCounties = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: RegionType.County);
        ConsoleLog.Info("  {0} counties in this scheme and dataset", allCounties.Count);

        var chosen = CountiesToCombine
            .Select(name => Regions.FindByDescription(allCounties, name))
            .ToList();
        foreach (var county in chosen)
            ConsoleLog.Info("    {0}", county.Describe());

        // Step 3. Ask for the combination. The description has to be unique for your
        // account, so it carries a timestamp.
        ConsoleLog.Heading("Step 3: request the combined region");
        var description = Config.UniqueTitle("Combined Region");

        // Re-running this workflow should not fail on a name that already exists,
        // and should not build the same region twice.
        var existing = Regions.FindExistingUserRegion(
            client, ids.AggregationSchemeId, ids.DatasetId, description);

        Region combined;
        if (existing is not null)
        {
            ConsoleLog.Info("  a region named '{0}' already exists; reusing it", description);
            combined = existing;
        }
        else
        {
            var request = new CombineRegionRequest
            {
                Description = description,
                HashIds = chosen.Select(c => c.HashId).ToList(),
            };
            ConsoleLog.Info("  combining {0} regions as '{1}'", chosen.Count, description);

            // POST /api/v1/region/build/combined/{aggregationSchemeId}
            // (wiki: Combine Regions)
            combined = Regions.BuildCombinedRegion(client, ids.AggregationSchemeId, request);
            ConsoleLog.Info("  accepted: {0}", combined.Describe());
            ConsoleLog.Info("  status is '{0}'; the model builds in the background",
                combined.ModelBuildStatus);
        }

        // Step 4. Wait for the model. A combined region usually finishes inside a
        // minute; the helper gives up after ten and says so rather than looping.
        ConsoleLog.Heading("Step 4: wait for the model to build");

        // GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
        var built = Regions.WaitForRegionBuild(client, combined.HashId);
        ConsoleLog.Info("  built");
        ConsoleLog.Info("    {0}", built.Describe());
        ConsoleLog.Info("    employment {0:N0}    output {1:N0}", built.Employment ?? 0, built.Output ?? 0);

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Created region: {0}", built.Description);
        ConsoleLog.Info("  HashId:      {0}", built.HashId);
        ConsoleLog.Info("  userModelId: {0}", built.UserModelId);
        ConsoleLog.Info();
        ConsoleLog.Info("Use that HashId in a Group exactly as you would an IMPLAN region.");
        ConsoleLog.Info("Delete the region from Regions in IMPLAN Cloud when you are done.");
        return built.HashId;
    }
}
