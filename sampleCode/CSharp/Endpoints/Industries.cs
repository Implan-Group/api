namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Industry Set and Industry Code endpoints.
/// </summary>
/// <remarks>
/// An Industry Set is a vintage of IMPLAN's industry list; an Industry Code names
/// one industry inside a set. Codes are only meaningful with their set: 509 is
/// Full-service restaurants in the 546 set and Federal electric utilities in the
/// 528 set, so a code copied from an older example lands on the wrong industry
/// rather than failing.
///
/// Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries
/// </remarks>
public static class Industries
{
    /// <summary>
    /// Lists every Industry Set, including retired ones.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/industry-sets  (wiki: Get Industry Sets)
    ///
    /// <c>activeStatus</c> marks a set as still supported, and exactly one set
    /// carries <c>isDefault</c>, which is the current United States list. There is
    /// no public endpoint for reading a single set, so filter this list when you
    /// want one.
    /// </remarks>
    public static List<IndustrySet> GetIndustrySets(ApiClient client)
    {
        return client.GetJson<List<IndustrySet>>("/api/v1/industry-sets");
    }

    /// <summary>
    /// Lists the industries in an Aggregation Scheme, ordered by code.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/IndustryCodes/{aggregationSchemeId}
    /// (wiki: Industry Codes by Aggregation Scheme)
    ///
    /// This route takes no query string. An <c>industrySetId</c> parameter added
    /// here is ignored, because a scheme already implies its Industry Set; the
    /// method below is the one that accepts it. For a custom scheme these are the
    /// scheme's own aggregated sectors.
    /// </remarks>
    public static List<IndustryCode> GetIndustryCodesForScheme(ApiClient client, int aggregationSchemeId)
    {
        return client.GetJson<List<IndustryCode>>($"/api/v1/IndustryCodes/{aggregationSchemeId}");
    }

    /// <summary>
    /// Lists the industries in an Industry Set, ordered by code.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/IndustryCodes  (wiki: Industry Codes by Industry Set)
    ///
    /// Omitting <paramref name="industrySetId"/> uses the current default United
    /// States set.
    /// </remarks>
    public static List<IndustryCode> GetIndustryCodesForSet(ApiClient client, int? industrySetId = null)
    {
        var query = new Query().With("industrySetId", industrySetId);

        return client.GetJson<List<IndustryCode>>("/api/v1/IndustryCodes", query);
    }

    /// <summary>
    /// Finds one industry by code, and confirms it is the industry you meant.
    /// </summary>
    /// <remarks>
    /// Checking the description as well as the code is the guard against the trap
    /// this class's remarks describe. The comparison is loose on purpose: IMPLAN
    /// rewords descriptions between vintages, so a substring match either way is
    /// enough to catch a code that has moved to a different industry entirely.
    /// </remarks>
    public static IndustryCode FindIndustry(
        IEnumerable<IndustryCode> industries,
        int code,
        string expectedDescription)
    {
        foreach (var industry in industries.Where(i => i.Code == code))
        {
            var actual = industry.Description;
            if (actual.Contains(expectedDescription, StringComparison.OrdinalIgnoreCase)
                || expectedDescription.Contains(actual, StringComparison.OrdinalIgnoreCase))
            {
                return industry;
            }

            throw new KeyNotFoundException(
                $"Industry code {code} is '{industry.Description}' in this Aggregation "
                + $"Scheme, not '{expectedDescription}'. Industry codes differ between "
                + "Industry Sets; look the industry up by description instead.");
        }

        throw new KeyNotFoundException($"No industry with code {code} in this Aggregation Scheme.");
    }

    /// <summary>
    /// Finds one industry by description, matched case-insensitively.
    /// </summary>
    /// <remarks>
    /// Use this when you know the industry by name and want whatever code it carries
    /// in the scheme you resolved, which is the portable way to write a sample.
    /// </remarks>
    public static IndustryCode FindIndustryByDescription(
        IEnumerable<IndustryCode> industries,
        string description)
    {
        var matches = industries
            .Where(i => string.Equals(i.Description, description, StringComparison.OrdinalIgnoreCase))
            .ToList();

        return matches.Count switch
        {
            1 => matches[0],
            0 => throw new KeyNotFoundException(
                $"No industry named '{description}' in this Aggregation Scheme. "
                + "Print the industry list to see the available descriptions."),
            _ => throw new KeyNotFoundException(
                $"'{description}' matches {matches.Count} industries in this Aggregation "
                + "Scheme; use the code instead."),
        };
    }
}

