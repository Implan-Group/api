using System.Text;

namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Reading the results of a completed impact run.
/// </summary>
/// <remarks>
/// Every endpoint here returns CSV as text. Save it with a <c>.csv</c> extension and
/// it opens in Excel or Sheets. All of them take the same optional filters, so the
/// same run can be read whole or sliced by region, impact type, group, event, or
/// tag.
///
/// Only read these once the run reports <c>Complete</c>.
///
/// Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results
/// </remarks>
public static class ImpactResults
{
    private const string Results = "/api/v1/impact/results";

    /// <summary>
    /// Employment, Labor Income, Value Added, and Output by impact type.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}
    /// (wiki: Results - Summary Economic Indicators)
    ///
    /// The headline report, and the one to start with. Rows are split Direct,
    /// Indirect, and Induced for each Group, Event, and Region.
    /// </remarks>
    public static string GetSummaryEconomicIndicators(
        ApiClient client, long runId, ResultFilters? filters = null)
    {
        return client.GetText($"{Results}/SummaryEconomicIndicators/{runId}", ToQuery(filters));
    }

    /// <summary>
    /// The same indicators, broken out by industry.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/ExportDetailEconomicIndicators/{runId}
    /// (wiki: Results - Detailed Economic Indicators)
    ///
    /// Note the year in parentheses after a Group or Model name in this report: that
    /// is the Data Year of the underlying dataset, not the Dollar Year the figures
    /// are expressed in. They differ whenever you analyze an older data year in
    /// today's dollars.
    /// </remarks>
    public static string GetDetailedEconomicIndicators(
        ApiClient client, long runId, ResultFilters? filters = null)
    {
        return client.GetText($"{Results}/ExportDetailEconomicIndicators/{runId}", ToQuery(filters));
    }

    /// <summary>
    /// Tax revenue by level of government.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/SummaryTaxes/{runId}
    /// (wiki: Results - Summary Taxes)
    /// </remarks>
    public static string GetSummaryTaxes(ApiClient client, long runId, ResultFilters? filters = null)
    {
        return client.GetText($"{Results}/SummaryTaxes/{runId}", ToQuery(filters));
    }

    /// <summary>
    /// Tax revenue by tax type and level of government.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/DetailedTaxes/{runId}
    /// (wiki: Results - Detailed Taxes)
    /// </remarks>
    public static string GetDetailedTaxes(ApiClient client, long runId, ResultFilters? filters = null)
    {
        return client.GetText($"{Results}/DetailedTaxes/{runId}", ToQuery(filters));
    }

    /// <summary>
    /// How large the impact is relative to each industry already in the region.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}
    /// (wiki: Results - Estimated Growth Percentage)
    ///
    /// This one is different from its neighbours in two ways, and both matter.
    ///
    /// First, it takes its filters as a JSON body rather than as query parameters,
    /// on a GET. That is unusual, it is what the endpoint requires, and IMPLAN's API
    /// Gateway passes the body through, so do not rewrite it as a POST or move the
    /// filters to the query string.
    ///
    /// Second, all five filter lists have to be present even when empty. Send an
    /// empty array for any dimension you are not filtering on; omitting one is an
    /// error rather than a default. <see cref="ImpactResultsExportRequest"/>
    /// initializes them to empty lists for exactly this reason.
    ///
    /// A 409 means the run has not finished, or that its project has no completed
    /// run to compare against.
    /// </remarks>
    public static string GetEstimatedGrowthPercentage(
        ApiClient client, long runId, ImpactResultsExportRequest request)
    {
        return client.GetText($"{Results}/EstimatedGrowthPercentage/{runId}", query: null, body: request);
    }

    /// <summary>
    /// Writes a CSV report to disk, creating the folder if it is not there.
    /// </summary>
    /// <remarks>
    /// Written as UTF-8 without a byte-order mark, so the line endings the API sent
    /// survive intact rather than being rewritten.
    /// </remarks>
    public static string SaveCsv(string csvText, string destination)
    {
        var folder = Path.GetDirectoryName(destination);
        if (!string.IsNullOrEmpty(folder))
            Directory.CreateDirectory(folder);

        File.WriteAllText(destination, csvText, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
        ConsoleLog.Info("  saved {0}", destination);
        return destination;
    }

    /// <summary>
    /// Turns a file name into something valid on Windows.
    /// </summary>
    public static string SafeFileName(string text)
    {
        var cleaned = new string(text
            .Select(c => Path.GetInvalidFileNameChars().Contains(c) ? '_' : c)
            .ToArray())
            .Trim()
            .TrimEnd('.');

        if (cleaned.Length > 120)
            cleaned = cleaned[..120];

        return cleaned.Length == 0 ? "results" : cleaned;
    }

    /// <summary>
    /// Turns the filters into query parameters.
    /// </summary>
    /// <remarks>
    /// <see cref="Query"/> rather than a dictionary, because these filters repeat:
    /// two regions means <c>regions=Oregon&amp;regions=Wisconsin</c>, and a
    /// dictionary keyed by name would silently keep only the last.
    /// </remarks>
    private static Query? ToQuery(ResultFilters? filters)
    {
        if (filters is null)
            return null;

        var query = new Query();
        foreach (var (name, value) in filters.ToQuery())
            query.Add(new KeyValuePair<string, string>(name, value));

        return query;
    }
}
