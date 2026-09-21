using System.Diagnostics;

namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Region endpoints: finding, combining, and building regions.
/// </summary>
/// <remarks>
/// Regions form a hierarchy. The top-level region for a United States scheme is the
/// country; its children are the states; a state's children are its counties, MSAs,
/// and congressional districts; a county's children are its ZIP codes.
/// International schemes have no top-level region, so start from the country
/// children instead.
///
/// Alongside IMPLAN's regions sit your own: combined regions you built from several
/// others, and customized regions where you edited the underlying economic data.
///
/// Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
/// Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
/// </remarks>
public static class Regions
{
    /// <summary>
    /// Lists the values accepted by the <c>regionTypeFilter</c> parameter.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
    ///
    /// Also the cheapest authenticated call in the API, which is why
    /// <see cref="Auth"/> uses it to test a cached token.
    /// </remarks>
    public static List<string> GetRegionTypes(ApiClient client)
    {
        return client.GetJson<List<string>>("/api/v1/region/RegionTypes");
    }

    /// <summary>
    /// Reads the region at the top of the hierarchy, usually a country.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/{aggregationSchemeId}/{datasetId}
    /// (wiki: Regions - Top Level)
    ///
    /// International schemes have no top-level region and answer 422 here; use
    /// <see cref="GetRegionChildren"/> with <c>Country</c> for those.
    /// </remarks>
    public static Region GetTopLevelRegion(ApiClient client, int aggregationSchemeId, int datasetId)
    {
        return client.GetJson<Region>($"/api/v1/region/{aggregationSchemeId}/{datasetId}");
    }

    /// <summary>
    /// Reads one region by HashId or URID.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}
    /// (wiki: Get Region by Id)
    /// </remarks>
    public static Region GetRegion(
        ApiClient client,
        int aggregationSchemeId,
        int datasetId,
        string hashIdOrUrid)
    {
        return client.GetJson<Region>(
            $"/api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}");
    }

    /// <summary>
    /// Lists the regions inside a region, optionally filtered to one type.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children
    /// GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}/children
    /// (wiki: Regional Children)
    ///
    /// Omitting the parent starts from the top-level region, so asking for
    /// <c>State</c> with no parent gives every state in the country.
    ///
    /// The filter reaches through the hierarchy: asking a state for <c>Zipcode</c>
    /// returns the ZIP codes of its counties, not nothing.
    ///
    /// Worth knowing for bulk work: every region in this response carries its own
    /// <c>modelBuildStatus</c>, so one call tells you both which regions exist and
    /// which of them are already built. There is no separate endpoint for that, and
    /// asking region by region is what makes a bulk script trip the rate limit.
    /// </remarks>
    public static List<Region> GetRegionChildren(
        ApiClient client,
        int aggregationSchemeId,
        int datasetId,
        string? parentHashIdOrUrid = null,
        RegionType? regionType = null)
    {
        var path = parentHashIdOrUrid is null
            ? $"/api/v1/region/{aggregationSchemeId}/{datasetId}/children"
            : $"/api/v1/region/{aggregationSchemeId}/{datasetId}/{parentHashIdOrUrid}/children";

        var query = new Query().With("regionTypeFilter", regionType?.ToString());

        return client.GetJson<List<Region>>(path, query);
    }

    /// <summary>
    /// Lists your combined and customized regions for one scheme and dataset.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
    /// (wiki: Get User Regions by Aggregation Scheme)
    /// </remarks>
    public static List<Region> GetUserRegionsForScheme(
        ApiClient client,
        int aggregationSchemeId,
        int datasetId)
    {
        return client.GetJson<List<Region>>(
            $"/api/v1/region/{aggregationSchemeId}/{datasetId}/user");
    }

    /// <summary>
    /// Reads one of your regions by HashId.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/region/user/{hashId}  (wiki: Get User Region)
    ///
    /// This is the endpoint to poll while a combined region builds. It reads one
    /// region rather than the whole list, so it stays fast and avoids the 503 the
    /// list can return on an account with many custom schemes.
    ///
    /// An unknown HashId comes back as an empty body rather than a 404, so null here
    /// means "no such region of yours".
    /// </remarks>
    public static Region? GetUserRegion(ApiClient client, string hashId)
    {
        var text = client.GetText($"/api/v1/region/user/{hashId}");
        if (string.IsNullOrWhiteSpace(text) || text.Trim() == "null")
            return null;

        return Json.Deserialize<Region>(text);
    }

    /// <summary>
    /// Combines two or more regions into one and starts building its model.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/region/build/combined/{aggregationSchemeId}
    /// (wiki: Combine Regions)
    ///
    /// Returns immediately with the new region at <c>modelBuildStatus</c> of
    /// <c>New</c>. The model is not usable until that reads <c>Complete</c>, which
    /// is what <see cref="WaitForRegionBuild"/> waits for.
    ///
    /// The regions being combined must come from the same dataset, must not overlap,
    /// and must not nest: a state and a county inside it cannot be combined. The
    /// description has to be unique for your account.
    ///
    /// The endpoint answers with an array holding the single new region.
    /// </remarks>
    public static Region BuildCombinedRegion(
        ApiClient client,
        int aggregationSchemeId,
        CombineRegionRequest request)
    {
        var regions = client.PostJson<List<Region>>(
            $"/api/v1/region/build/combined/{aggregationSchemeId}", request);

        if (regions.Count != 1)
            throw new InvalidOperationException($"Expected one combined region back, got {regions.Count}.");

        return regions[0];
    }

    /// <summary>
    /// Builds several IMPLAN regions at once, without combining them.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/region/build-and-return/{aggregationSchemeId}
    /// (wiki: Build and Return Regions)
    ///
    /// The body is a plain array of HashIds. Use this when a bulk job needs regions
    /// whose models have not been built yet: one call queues all of them instead of
    /// one call each.
    ///
    /// Like the combined build, this returns before the models are ready.
    /// </remarks>
    public static List<Region> BuildAndReturnRegions(
        ApiClient client,
        int aggregationSchemeId,
        List<string> hashIds)
    {
        return client.PostJson<List<Region>>(
            $"/api/v1/region/build-and-return/{aggregationSchemeId}", hashIds);
    }

    /// <summary>
    /// Polls until a combined or customized region has finished building.
    /// </summary>
    /// <remarks>
    /// Polls <c>GET /api/v1/region/user/{hashId}</c> rather than the user-regions
    /// list: it is one region instead of all of them, and it does not hit the 503
    /// the list can return on a busy account.
    ///
    /// Throws on a build that reports <c>Error</c>, and on one that has not finished
    /// inside the timeout. Never poll a heavy data endpoint to find out whether a
    /// model is ready; those answer with an error until it is, which is slow and
    /// reads like a different problem.
    /// </remarks>
    public static Region WaitForRegionBuild(
        ApiClient client,
        string hashId,
        TimeSpan? timeout = null,
        TimeSpan? pollInterval = null)
    {
        var limit = timeout ?? Config.RegionBuildTimeout;
        var interval = pollInterval ?? Config.RegionBuildPollInterval;
        var deadline = Stopwatch.StartNew();
        var lastStatus = string.Empty;

        while (true)
        {
            var region = GetUserRegion(client, hashId);

            if (region is not null)
            {
                if (region.ModelBuildStatus != lastStatus)
                {
                    lastStatus = region.ModelBuildStatus;
                    ConsoleLog.Info("  region {0}: {1}", hashId,
                        string.IsNullOrWhiteSpace(lastStatus) ? "(no status)" : lastStatus);
                }

                if (region.IsBuilt)
                    return region;

                if (region.ModelBuildStatus == Models.ModelBuildStatus.Error)
                {
                    throw new InvalidOperationException(
                        $"The model for region {hashId} failed to build. Try the request "
                        + "again, or contact support@implan.com if it repeats.");
                }
            }

            if (deadline.Elapsed >= limit)
            {
                throw new TimeoutException(
                    $"Region {hashId} was still building after {limit.TotalSeconds:F0} seconds, "
                    + $"last status '{(lastStatus.Length == 0 ? "unknown" : lastStatus)}'. It may "
                    + "still finish; check your regions in IMPLAN Cloud.");
            }

            Thread.Sleep(interval);
        }
    }

    /// <summary>
    /// Finds one region by its exact description, matched case-insensitively.
    /// </summary>
    /// <remarks>
    /// Region descriptions carry their state, as in <c>Lane County, OR</c>, so they
    /// are unique within a region type.
    /// </remarks>
    public static Region FindByDescription(IReadOnlyCollection<Region> regions, string description)
    {
        return regions.FirstOrDefault(r =>
                   string.Equals(r.Description, description, StringComparison.OrdinalIgnoreCase))
               ?? throw new KeyNotFoundException(
                   $"No region named '{description}' in this list of {regions.Count} regions. "
                   + "Check the spelling, including the state abbreviation.");
    }

    /// <summary>
    /// Returns one of your regions by name, or null if you have not built it.
    /// </summary>
    /// <remarks>
    /// Bulk workflows call this first so that re-running them reuses the regions
    /// they built last time instead of failing on a duplicate name.
    /// </remarks>
    public static Region? FindExistingUserRegion(
        ApiClient client,
        int aggregationSchemeId,
        int datasetId,
        string description)
    {
        List<Region> existing;
        try
        {
            existing = GetUserRegionsForScheme(client, aggregationSchemeId, datasetId);
        }
        catch (ImplanApiException error) when (error.StatusCode == 503)
        {
            // The region cache is rebuilding. Treat it as "cannot tell", and let the
            // caller try the build, which reports a duplicate name clearly.
            ConsoleLog.Info(
                "  the user-regions list is temporarily unavailable (503); "
                + "continuing without checking for an existing region");
            return null;
        }

        return existing.FirstOrDefault(r =>
            string.Equals(r.Description, description, StringComparison.OrdinalIgnoreCase));
    }
}

