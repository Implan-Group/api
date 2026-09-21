namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Resolving the identifiers every other call needs.
/// </summary>
/// <remarks>
/// This class composes the lookup endpoints into the one answer a workflow actually
/// wants: which Aggregation Scheme, Dataset, and Household Set should I use right
/// now?
///
/// Resolving instead of hardcoding is the single most important habit when writing
/// against this API. IMPLAN publishes new data every year and new industry vintages
/// every few years, and a sample with <c>aggregationSchemeId = 8</c> frozen into it
/// quietly analyzes 2022 data in 2030. Nothing here is expensive: three GETs,
/// cached for the life of the run.
///
/// Wiki: Getting Started
/// https://github.com/Implan-Group/api/wiki/Getting-Started
/// </remarks>
public static class Identifiers
{
    /// <summary>
    /// Works out the current Aggregation Scheme, Dataset, and Household Set.
    /// </summary>
    /// <remarks>
    /// The chain is always the same:
    ///
    /// 1. Find the Industry Set. For the United States that is the one flagged
    ///    <c>isDefault</c>; for Canada and International it is the newest one in use.
    /// 2. Take its <c>defaultAggregationSchemeId</c>, which is the Unaggregated
    ///    scheme for that set. Falling back to a description search covers a set
    ///    that does not name one.
    /// 3. Read that scheme's Datasets and take the one flagged <c>isDefault</c>.
    /// 4. Take the first of the scheme's <c>householdSetIds</c>.
    ///
    /// Every workflow starts here, so the console prints what was chosen.
    /// </remarks>
    public static Models.Identifiers Resolve(ApiClient client, MapCode mapCode = MapCode.US)
    {
        // GET /api/v1/industry-sets  (wiki: Get Industry Sets)
        var allSets = Industries.GetIndustrySets(client);

        var industrySet = mapCode == MapCode.US
            ? DefaultUsIndustrySet(allSets)
            : LatestSetForMapCode(client, allSets, mapCode);

        // GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)
        // Narrowing by Industry Set keeps custom schemes on the account out of the way.
        var schemes = AggregationSchemes.GetAggregationSchemes(client, industrySet.Id);
        if (schemes.Count == 0)
        {
            throw new KeyNotFoundException(
                $"Industry Set {industrySet.Id} has no Aggregation Schemes available to this account.");
        }

        var scheme = schemes.FirstOrDefault(s => s.Id == industrySet.DefaultAggregationSchemeId)
                     // No default named, so take the Unaggregated scheme, which keeps
                     // every industry separate and is the right start for a sample.
                     ?? schemes.FirstOrDefault(s =>
                         s.Description.Contains("Unaggregated", StringComparison.OrdinalIgnoreCase))
                     ?? schemes[0];

        // GET /api/v1/datasets/{aggregationSchemeId}  (wiki: Dataset by Aggregation Scheme)
        var dataset = Datasets.DefaultDataset(Datasets.GetDatasetsForScheme(client, scheme.Id));

        if (scheme.HouseholdSetIds.Count == 0)
        {
            throw new KeyNotFoundException(
                $"Aggregation Scheme {scheme.Id} lists no Household Sets, so a Project "
                + "cannot be created against it.");
        }

        var identifiers = new Models.Identifiers
        {
            MapCode = mapCode,
            IndustrySet = industrySet,
            AggregationScheme = scheme,
            Dataset = dataset,
            HouseholdSetId = scheme.HouseholdSetIds[0],
        };

        ConsoleLog.Info("Resolved identifiers from the API:");
        ConsoleLog.Info(identifiers.Describe());
        return identifiers;
    }

    /// <summary>
    /// Picks the current United States Industry Set.
    /// </summary>
    /// <remarks>
    /// Exactly one set carries <c>isDefault</c>. That flag moves when IMPLAN
    /// publishes a new vintage, which is precisely why the samples read it instead
    /// of naming a set.
    /// </remarks>
    private static IndustrySet DefaultUsIndustrySet(IEnumerable<IndustrySet> sets)
    {
        return sets.FirstOrDefault(s => s.IsDefault == true)
               ?? throw new KeyNotFoundException(
                   "No Industry Set is flagged as the default. Pick one by description "
                   + "from GET /api/v1/industry-sets.");
    }

    /// <summary>
    /// Picks the newest Industry Set for Canada or International.
    /// </summary>
    /// <remarks>
    /// Only the United States set carries <c>isDefault</c>, so for the other two the
    /// newest active set is found by looking at which sets the Aggregation Schemes
    /// for that map code are built on, and taking the highest.
    /// </remarks>
    private static IndustrySet LatestSetForMapCode(
        ApiClient client,
        IEnumerable<IndustrySet> sets,
        MapCode mapCode)
    {
        var schemes = AggregationSchemes.GetAggregationSchemes(client)
            .Where(s => string.Equals(s.MapCode, mapCode.ToString(), StringComparison.OrdinalIgnoreCase)
                        && s.Description.Contains("Unaggregated", StringComparison.OrdinalIgnoreCase))
            .ToList();

        if (schemes.Count == 0)
            throw new KeyNotFoundException($"No Unaggregated Aggregation Scheme for map code {mapCode}.");

        // Industry Set ids increase with each vintage, so the highest is the newest.
        var newest = schemes.MaxBy(s => s.IndustrySetId)!;

        return sets.FirstOrDefault(s => s.Id == newest.IndustrySetId)
               ?? throw new KeyNotFoundException(
                   $"Aggregation Scheme {newest.Id} refers to Industry Set "
                   + $"{newest.IndustrySetId}, which is not in the Industry Set list.");
    }
}
