namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Dataset endpoints.
/// </summary>
/// <remarks>
/// A Dataset is one data year within one Aggregation Scheme. IMPLAN publishes data
/// annually and flags the newest complete year as the default.
///
/// Dataset ids are scheme-specific and are not ordered by year, so never carry an
/// id from one scheme to another and never assume the newest is last in the list.
/// Read the list for your scheme and take the entry flagged <c>isDefault</c>.
///
/// Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets
/// </remarks>
public static class Datasets
{
    /// <summary>
    /// Lists the data years available for one Aggregation Scheme.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/datasets/{aggregationSchemeId}
    /// (wiki: Dataset by Aggregation Scheme)
    /// </remarks>
    public static List<Dataset> GetDatasetsForScheme(ApiClient client, int aggregationSchemeId)
    {
        return client.GetJson<List<Dataset>>($"/api/v1/datasets/{aggregationSchemeId}");
    }

    /// <summary>
    /// Lists the data years for the current default Aggregation Scheme.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/datasets  (wiki: Datasets)
    ///
    /// The scheme-scoped call above is almost always the one you want, because it
    /// makes the scheme the ids belong to explicit.
    /// </remarks>
    public static List<Dataset> GetDatasets(ApiClient client)
    {
        return client.GetJson<List<Dataset>>("/api/v1/datasets");
    }

    /// <summary>
    /// Picks the default data year out of a list.
    /// </summary>
    /// <remarks>
    /// The default is flagged rather than ordered: it is often the last entry, so
    /// taking the first would quietly select 2001. Exactly one entry carries the
    /// flag.
    /// </remarks>
    public static Dataset DefaultDataset(IEnumerable<Dataset> datasets)
    {
        return datasets.FirstOrDefault(d => d.IsDefault)
               ?? throw new KeyNotFoundException(
                   "No Dataset in this Aggregation Scheme is flagged as the default. "
                   + "Choose one explicitly by description.");
    }
}
