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
        return client.GetText($"{Results}/SummaryEconomicIndicators/{runId}", filters?.ToQuery());
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
        return client.GetText($"{Results}/ExportDetailEconomicIndicators/{runId}", filters?.ToQuery());
    }

    /// <summary>
    /// Tax revenue by level of government.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/results/SummaryTaxes/{runId}, or its <c>can/</c> or
    /// <c>intl/</c> route (wiki: Results - Summary Taxes)
    ///
    /// Each country taxes at different levels of government, so each has its own
    /// route, chosen here from the Project's map code. The United States route
    /// refuses a Canadian or international run with a 422.
    /// </remarks>
    public static string GetSummaryTaxes(
        ApiClient client, long runId, ResultFilters? filters = null, MapCode mapCode = MapCode.US)
    {
        var route = mapCode switch
        {
            MapCode.CAN => "can/",
            MapCode.INTL => "intl/",
            _ => string.Empty,
        };
        return client.GetText($"{Results}/SummaryTaxes/{route}{runId}", filters?.ToQuery());
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
        return client.GetText($"{Results}/DetailedTaxes/{runId}", filters?.ToQuery());
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
    /// <summary>
    /// A Summary Economic Indicators report summed by effect. Direct is the activity
    /// itself; Indirect and Induced are the supply chain and the household spending it
    /// sets off.
    /// </summary>
    public sealed record EffectTotals(double DirectOutput, double IndirectAndInducedOutput, double Employment);

    /// <summary>Sums a Summary Economic Indicators report by effect.</summary>
    /// <remarks>
    /// Each row is one Group, Event, and effect, whose Impact column reads
    /// "1 - Direct", "2 - Indirect", or "3 - Induced". The report's last row,
    /// "Totals", is skipped so nothing is counted twice.
    /// </remarks>
    public static EffectTotals SumEffects(string csvText)
    {
        var lines = csvText.Split('\n').Select(l => l.TrimEnd('\r')).Where(l => l.Trim().Length > 0).ToList();
        if (lines.Count == 0)
            return new EffectTotals(0, 0, 0);

        var header = Csv.SplitLine(lines[0]);
        var groupColumn = header.IndexOf("GroupName");
        var impactColumn = header.IndexOf("Impact");
        var outputColumn = header.IndexOf("Output");
        var employmentColumn = header.IndexOf("Employment");

        double direct = 0, indirectAndInduced = 0, employment = 0;
        foreach (var line in lines.Skip(1))
        {
            var row = Csv.SplitLine(line);
            if (row.Count <= Math.Max(outputColumn, employmentColumn) || row[groupColumn] == "Totals" || row[impactColumn].Length == 0)
                continue;

            var output = double.Parse(row[outputColumn], System.Globalization.CultureInfo.InvariantCulture);
            if (row[impactColumn].StartsWith('1'))
                direct += output;
            else
                indirectAndInduced += output;
            employment += double.Parse(row[employmentColumn], System.Globalization.CultureInfo.InvariantCulture);
        }

        return new EffectTotals(direct, indirectAndInduced, employment);
    }

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
}
