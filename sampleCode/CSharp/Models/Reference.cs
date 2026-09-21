namespace Implan.ApiSamples.Models;

/// <summary>Which country's data an Aggregation Scheme covers.</summary>
public enum MapCode
{
    // The serialized names are what the API uses; the display names here are what
    // the samples pass on the command line.
    US,
    CAN,
    INTL,
}

/// <summary>
/// The full list of industries for a country, in one vintage.
/// </summary>
/// <remarks>
/// IMPLAN revises its industry list periodically, so several sets coexist: the US
/// has had 536, 546, and 528 industries. Exactly one set is flagged
/// <see cref="IsDefault"/>, and that is the current one. Descriptions carry a
/// country in parentheses, for example <c>528 Industries (latest US)</c>, so match
/// on the id rather than on the text wherever you can.
///
/// Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries
/// </remarks>
public sealed class IndustrySet
{
    public int Id { get; set; }
    public string Description { get; set; } = string.Empty;
    public int? DefaultAggregationSchemeId { get; set; }
    public bool? ActiveStatus { get; set; }
    public bool? IsDefault { get; set; }
    public int? MapTypeId { get; set; }
    public bool IsNaicsCompatible { get; set; }
}

/// <summary>
/// How industries are grouped for a Project.
/// </summary>
/// <remarks>
/// An Unaggregated scheme keeps every industry separate; the NAICS schemes roll
/// them up. A Project's scheme is fixed at creation and cannot be changed, and
/// every region identifier and industry code you use has to come from the same
/// scheme.
///
/// <see cref="Status"/> is <c>Complete</c> when the scheme is ready to use.
///
/// Wiki: Aggregation Schemes
/// https://github.com/Implan-Group/api/wiki/Aggregation-Schemes
/// </remarks>
public sealed class AggregationScheme
{
    public int Id { get; set; }
    public string Description { get; set; } = string.Empty;
    public int IndustrySetId { get; set; }
    public List<int> HouseholdSetIds { get; set; } = [];
    public string MapCode { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
}

/// <summary>
/// One data year, within one Aggregation Scheme.
/// </summary>
/// <remarks>
/// Dataset ids are specific to a scheme and are not ordered by year, so an id taken
/// from another scheme is either rejected or, worse, silently resolves to a
/// different year. Always read the list for the scheme you are using and take the
/// entry flagged <see cref="IsDefault"/>.
///
/// Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets
/// </remarks>
public sealed class Dataset
{
    public int Id { get; set; }
    public string Description { get; set; } = string.Empty;
    public bool IsDefault { get; set; }
}

/// <summary>
/// One industry within an Industry Set.
/// </summary>
/// <remarks>
/// The same <see cref="Code"/> means different industries in different sets: 509 is
/// Full-service restaurants in the 546 set and Federal electric utilities in the
/// 528 set. The samples check the description alongside the code for that reason.
/// </remarks>
public sealed class IndustryCode
{
    public int Id { get; set; }
    public int Code { get; set; }
    public string Description { get; set; } = string.Empty;
}

/// <summary>
/// A valid code for an event type that needs one.
/// </summary>
/// <remarks>
/// Household Income events, for instance, take an income bracket such as
/// <c>10002 - Households 15-30k</c> rather than an industry.
/// </remarks>
public sealed class Specification
{
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
}

/// <summary>
/// Everything a workflow needs to address data, resolved from the API.
/// </summary>
/// <remarks>
/// Built by <c>Endpoints.Identifiers.Resolve</c>. Holding these together means a
/// workflow asks for them once and then passes one object around, instead of
/// threading four integers through every call.
/// </remarks>
public sealed class Identifiers
{
    public required MapCode MapCode { get; init; }
    public required IndustrySet IndustrySet { get; init; }
    public required AggregationScheme AggregationScheme { get; init; }
    public required Dataset Dataset { get; init; }
    public required int HouseholdSetId { get; init; }

    public int AggregationSchemeId => AggregationScheme.Id;
    public int DatasetId => Dataset.Id;

    /// <summary>A short block naming everything that was resolved, for the console.</summary>
    public string Describe()
    {
        return string.Join(Environment.NewLine,
            $"  Map code:           {MapCode}",
            $"  Industry Set:       {IndustrySet.Id} - {IndustrySet.Description}",
            $"  Aggregation Scheme: {AggregationScheme.Id} - {AggregationScheme.Description}",
            $"  Dataset:            {Dataset.Id} - {Dataset.Description}",
            $"  Household Set:      {HouseholdSetId}");
    }
}
