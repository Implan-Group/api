namespace Implan.ApiSamples.Models;

/// <summary>
/// The values accepted by the <c>regionTypeFilter</c> parameter.
/// </summary>
/// <remarks>
/// Read them from <c>GET /api/v1/region/RegionTypes</c> rather than hardcoding,
/// which is what the Regions workflow demonstrates. They are listed here so the
/// editor can complete them and so a typo fails at compile time rather than as an
/// empty result.
///
/// For Canadian data, <see cref="State"/> filters to Provinces and
/// <see cref="County"/> to Economic Regions.
/// </remarks>
public enum RegionType
{
    Country,
    State,
    Msa,
    County,
    CongressionalDistrict,
    Zipcode,
}

/// <summary>
/// Where a region's economic model is in the build process.
/// </summary>
/// <remarks>
/// A newly combined region starts at <c>New</c> and is only usable at
/// <c>Complete</c>. Anything else means waiting, and <c>Error</c> means it will
/// never finish.
/// </remarks>
public static class ModelBuildStatus
{
    public const string New = "New";
    public const string InProgress = "InProgress";
    public const string Complete = "Complete";
    public const string Error = "Error";
}

/// <summary>
/// One region, as the API returns it.
/// </summary>
/// <remarks>
/// A region in IMPLAN is not just a place, it is a place within one Aggregation
/// Scheme and one Dataset. The same county has a different <see cref="HashId"/> in
/// the 528 and 546 schemes, and in the 2023 and 2024 datasets, because the
/// underlying economic model differs.
///
/// Prefer HashId when you have a choice. <see cref="Urid"/> still works and appears
/// in older examples, but HashId is the identifier IMPLAN is standardizing on.
///
/// The identifier fields are populated selectively: an IMPLAN-defined region has a
/// Urid, a region you combined yourself has a <see cref="UserModelId"/> and no
/// <see cref="FipsCode"/>, and both have a HashId.
///
/// Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
/// </remarks>
public sealed class Region
{
    public string HashId { get; set; } = string.Empty;
    public long? Urid { get; set; }
    public int? UserModelId { get; set; }
    public string Description { get; set; } = string.Empty;
    public int? ModelId { get; set; }
    public string ModelBuildStatus { get; set; } = string.Empty;

    // Totals for the region, useful as a check that you picked the right one.
    public double? Employment { get; set; }
    public double? Output { get; set; }
    public double? ValueAdded { get; set; }

    public int? AggregationSchemeId { get; set; }
    public int? DatasetId { get; set; }
    public string DatasetDescription { get; set; } = string.Empty;

    // Geographic codes, whichever applies: FIPS in the US, province in Canada, M49
    // internationally.
    public string? FipsCode { get; set; }
    public string? ProvinceCode { get; set; }
    public string? M49Code { get; set; }
    public string? GeoId { get; set; }
    public string? SgcFullerCode { get; set; }

    public string RegionType { get; set; } = string.Empty;
    public string RegionTypeDescription { get; set; } = string.Empty;
    public bool HasAccessibleChildren { get; set; }

    /// <summary>
    /// Whether this region can take part in a multi-regional (MRIO) analysis. The
    /// MrioProject workflow checks this before building a project.
    /// </summary>
    public bool IsMrioAllowed { get; set; }

    /// <summary>
    /// Anything the API returned that this model does not declare.
    /// </summary>
    /// <remarks>
    /// The API gains fields over time. Capturing them rather than discarding them
    /// means you can see what a response really contained without changing the
    /// model.
    /// </remarks>
    [JsonExtensionData]
    public Dictionary<string, JsonElement> Extra { get; set; } = [];

    /// <summary>True when the economic model is ready to run impacts against.</summary>
    [JsonIgnore]
    public bool IsBuilt => ModelBuildStatus == Models.ModelBuildStatus.Complete;

    /// <summary>True for a region you combined or customized, rather than an IMPLAN one.</summary>
    [JsonIgnore]
    public bool IsUserDefined => UserModelId is not null;

    /// <summary>One line naming the region and its identifiers, for the console.</summary>
    public string Describe()
    {
        var parts = new List<string>
        {
            string.IsNullOrWhiteSpace(Description) ? "(unnamed)" : Description,
            $"hashId={HashId}",
        };
        if (Urid is not null)
            parts.Add($"urid={Urid}");
        if (!string.IsNullOrWhiteSpace(ModelBuildStatus))
            parts.Add(ModelBuildStatus);
        return string.Join("  ", parts);
    }
}

/// <summary>
/// The body for combining two or more regions into one.
/// </summary>
/// <remarks>
/// Supply the regions through <see cref="HashIds"/>, <see cref="Urids"/>, or both;
/// two or more regions are required between them. HashId is the identifier IMPLAN
/// is standardizing on, so these samples use it. The description becomes the new
/// region's name and has to be unique for your account, which is why the samples
/// put a timestamp in it.
///
/// Regions being combined must come from the same dataset, must not overlap, and
/// must not nest inside one another: a state and a county within it cannot be
/// combined.
///
/// Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
/// </remarks>
public sealed class CombineRegionRequest
{
    public string Description { get; set; } = string.Empty;
    public List<string> HashIds { get; set; } = [];
    public List<long> Urids { get; set; } = [];
}
