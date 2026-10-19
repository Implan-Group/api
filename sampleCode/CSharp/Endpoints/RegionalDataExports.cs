namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Regional data exports: the data behind a region, rather than an impact result.
/// </summary>
/// <remarks>
/// These endpoints describe a region's economy as it already is: what its
/// industries produce, what they buy, who they employ. They need no Project and no
/// impact run, only a built region.
///
/// They all take the region the same way, through <c>hashId</c> on the query
/// string, and they all answer with CSV. That regularity is why
/// <see cref="GetExport"/> takes the report name as a parameter instead of there
/// being one method per report; the wiki's Regional Data Exports section lists the
/// rest.
///
/// Wiki: Regional Data Exports
/// https://github.com/Implan-Group/api/wiki/Regional-Data-Exports
/// </remarks>
public static class RegionalDataExports
{
    /// <summary>Every industry in a region, with employment, output, and value added.</summary>
    public const string RegionOverviewIndustries = "RegionOverviewIndustries";

    /// <summary>A region's model as one GAMS input file.</summary>
    /// <remarks>
    /// Wiki: Region Data - GAMS. For taking an IMPLAN region into the General
    /// Algebraic Modeling System, which is why it saves as <c>.gms</c>.
    ///
    /// Support: Exporting Data from IMPLAN to GAMS
    /// https://support.implan.com/hc/en-us/articles/360033706954
    /// </remarks>
    public const string GamsSingleFile = "region-general-algebraic-modeling-single-file";

    /// <summary>Reports whose natural file extension is not <c>.csv</c>.</summary>
    private static readonly Dictionary<string, string> FileExtensions = new(StringComparer.OrdinalIgnoreCase)
    {
        [GamsSingleFile] = ".gms",
    };

    /// <summary>The extension a given export should be saved with.</summary>
    public static string FileExtensionFor(string exportName)
    {
        return FileExtensions.TryGetValue(exportName, out var extension) ? extension : ".csv";
    }

    /// <summary>
    /// Downloads one regional data export for one region, as text.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/regions/export/{aggregationSchemeId}/{exportName}?hashId=...
    /// (wiki: Regional Data Exports)
    ///
    /// A 409 titled "Model not built" means the region's model has not finished
    /// building, or was never requested, rather than that the request was malformed.
    /// Build the region and ask again.
    ///
    /// <paramref name="exportName"/> is the segment from the wiki page for the
    /// report you want, for example <c>RegionOverviewIndustries</c> or
    /// <c>study_area_data_industry_summary</c>.
    /// </remarks>
    public static string GetExport(
        ApiClient client,
        int aggregationSchemeId,
        string exportName,
        string hashId)
    {
        return client.GetText(
            $"/api/v1/regions/export/{aggregationSchemeId}/{exportName}",
            new Query().With("hashId", hashId));
    }
}
