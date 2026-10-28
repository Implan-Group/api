namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Aggregation Scheme endpoints.
/// </summary>
/// <remarks>
/// An Aggregation Scheme decides how industries are grouped for a Project. It is
/// the first identifier you resolve and the one everything else hangs off: datasets,
/// regions, industry codes, and events are all scoped to it.
///
/// Wiki: Aggregation Schemes
/// https://github.com/Implan-Group/api/wiki/Aggregation-Schemes
/// </remarks>
public static class AggregationSchemes
{
    /// <summary>
    /// Lists the Aggregation Schemes the signed-in user can use.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)
    ///
    /// Returns both IMPLAN's standard schemes and any custom ones on the account.
    /// Supplying <paramref name="industrySetId"/> narrows the list to the schemes
    /// built on that set, which is how you get from "the current industry set" to
    /// "the scheme to use".
    ///
    /// Only schemes that have finished building are returned, so an entry here is
    /// ready to use.
    /// </remarks>
    public static List<AggregationScheme> GetAggregationSchemes(ApiClient client, int? industrySetId = null)
    {
        // The API spells this parameter with a lowercase `s`: `industrysetId`.
        var query = new Query().With("industrysetId", industrySetId);

        return client.GetJson<List<AggregationScheme>>("/api/v1/aggregationSchemes", query);
    }

    /// <summary>
    /// Reads one Aggregation Scheme by its id.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/aggregationSchemes/{aggregationSchemeId}
    /// (wiki: Aggregation Scheme by Id)
    ///
    /// Useful for checking status after creating a custom scheme: it is only usable
    /// once that reads <c>Complete</c>.
    /// </remarks>
    public static AggregationScheme GetAggregationScheme(ApiClient client, int aggregationSchemeId)
    {
        return client.GetJson<AggregationScheme>($"/api/v1/aggregationSchemes/{aggregationSchemeId}");
    }
}

