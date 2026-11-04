namespace Implan.ApiSamples.Models;

/// <summary>
/// The states an impact run moves through.
/// </summary>
/// <remarks>
/// <c>Complete</c> is the only one that means results can be read. <c>Error</c> and
/// <c>UserCancelled</c> are terminal failures: polling past them waits forever. A
/// 404 from the status endpoint is expected for the first few seconds of a run; one
/// that lasts past a minute is terminal, and means the run never attached to a
/// project, most often because a group was saved without a dollar year.
///
/// Wiki: Get Impact Status
/// https://github.com/Implan-Group/api/wiki/Get-Impact-Status
/// </remarks>
public enum ImpactStatus
{
    Unknown,
    New,
    InProgress,
    ReadyForWarehouse,
    Complete,
    Error,
    UserCancelled,
}

/// <summary>Helpers for reading an impact status.</summary>
public static class ImpactStatusExtensions
{
    /// <summary>True when the run has stopped and will not produce results.</summary>
    public static bool IsTerminalFailure(this ImpactStatus status) =>
        status is ImpactStatus.Error or ImpactStatus.UserCancelled;
}

/// <summary>
/// The three effects an impact analysis separates.
/// </summary>
/// <remarks>
/// Direct is the activity itself, Indirect is its supply chain, and Induced is the
/// household spending of everyone paid along the way.
///
/// Support: Examining Results and Interpreting Direct, Indirect, and Induced Effects
/// https://support.implan.com/hc/en-us/articles/360038799153
/// </remarks>
public enum ImpactType
{
    Direct,
    Indirect,
    Induced,
}

/// <summary>
/// Filters for the Estimated Growth Percentage report.
/// </summary>
/// <remarks>
/// Every list has to be present in the request, even when empty, so all five
/// default to empty lists here rather than to null. <see cref="DollarYear"/> is
/// required.
///
/// This is the body of a GET request, which is unusual but is what the endpoint
/// requires; see <c>Endpoints.ImpactResults.GetEstimatedGrowthPercentage</c>.
/// </remarks>
public sealed class ImpactResultsExportRequest
{
    public int DollarYear { get; set; }
    public List<string> Regions { get; set; } = [];
    public List<string> Impacts { get; set; } = [];
    public List<string> GroupNames { get; set; } = [];
    public List<string> EventNames { get; set; } = [];
    public List<string> EventTags { get; set; } = [];
}

/// <summary>
/// Optional filters shared by the CSV report endpoints.
/// </summary>
/// <remarks>
/// These go on the query string rather than in a body. Leaving one empty means no
/// filter on that dimension.
///
/// <see cref="Year"/> overrides the dollar year the results are expressed in. Left
/// unset, the API uses your account's dollar-year preference, falling back to the
/// current calendar year, so the samples set it explicitly to keep runs
/// reproducible.
///
/// <see cref="Regions"/> and <see cref="Groups"/> take the names exactly as the
/// reports print them in the ModelName and GroupName columns, and those carry the
/// data year in brackets: <c>Oregon (2024)</c>, not <c>Oregon</c>. A value that
/// matches nothing is a 400 naming it, not an empty report.
/// </remarks>
public sealed class ResultFilters
{
    public int? Year { get; set; }
    public List<string> Regions { get; set; } = [];
    public List<string> Impacts { get; set; } = [];
    public List<string> Groups { get; set; } = [];
    public List<string> Events { get; set; } = [];
    public List<string> EventTags { get; set; } = [];

    /// <summary>
    /// Renders the filters as query parameters, omitting the empty ones.
    /// </summary>
    /// <remarks>
    /// A list becomes a repeated parameter, one per value, which is the shape the
    /// API expects for these: two regions means
    /// <c>regions=Oregon&amp;regions=Wisconsin</c>.
    /// </remarks>
    public Query ToQuery()
    {
        return new Query()
            .With("year", Year)
            .WithEach("regions", Regions)
            .WithEach("impacts", Impacts)
            .WithEach("groups", Groups)
            .WithEach("events", Events)
            .WithEach("eventTags", EventTags);
    }
}
