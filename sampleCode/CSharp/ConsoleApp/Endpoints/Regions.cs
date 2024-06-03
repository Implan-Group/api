namespace ConsoleApp.Endpoints;

public sealed record class Region
{
    public string HashId { get; set; }
    public long? Urid { get; set; }
    public int? UserModelId { get; set; }
    public string Description { get; set; }
    public int? ModelId { get; set; }
    public string ModelBuildStatus { get; set; }
    public double? Employment { get; set; }
    public double? Output { get; set; }
    public double? ValueAdded { get; set; }
    public int AggregationSchemeId { get; set; }
    public int DatasetId { get; set; }
    public string DatasetDescription { get; set; }
    public string? FipsCode { get; set; }
    public string? ProvinceCode { get; set; }
    public string? M49Code { get; set; }
    public string RegionType { get; set; }
    public bool HasAccessibleChildren { get; set; }
    public string RegionTypeDescription { get; set; }
    public string? GeoId { get; set; }
    public bool IsMrioAllowed { get; set; }
}

public static class Regions
{
    /// <summary>
    /// Gets a list of all Region Types
    /// </summary>
    /// <returns></returns>
    public static string[] GetRegionTypes()
    {
        var request = new RestRequest("api/v1/region/RegionTypes");
        //var request = new RestRequest("api/v1/region/region-types");
        request.Method = Method.Get;

        return Rest.GetResponseData<string[]>(request).ThrowIfNull();
    }

    public static Region GetTopLevelRegion(int aggregationSchemeId, int dataSetId, string? hashIdOrUrid = null)
    {
        // GET {api_domain}api/v1/region/{aggregationSchemeId}/{dataSetId}
        var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);
        if (!string.IsNullOrWhiteSpace(hashIdOrUrid))
        {
            request.AppendUrlSegment("hashIdOrUrid", hashIdOrUrid);
        }
        
        return Rest.GetResponseData<Region>(request);
    }

    public static Region[] GetRegionChildren(
        int aggregationSchemeId, int dataSetId, 
        string? hashIdOrUrid = null,
        string? regionType = null)
    {
        // GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/children?regionTypeFilter={{regionType}}

        RestRequest request;
        if (!string.IsNullOrWhiteSpace(hashIdOrUrid))
        {
            request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/{hashIdOrUrid}/children");
            request.AddUrlSegment("hashIdOrUrid", hashIdOrUrid);
        }
        else
        {
            request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/children");
        }
        
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);
        if (!string.IsNullOrWhiteSpace(regionType))
        {
            request.AddParameter("regionTypeFilter", regionType);
        }

        return Rest.GetResponseData<Region[]>(request).ThrowIfNull();
    }

    public static Region[] GetUserRegions(int aggregationSchemeId, int dataSetId)
    {
        // GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/user
        var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/user");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);

        return Rest.GetResponseData<Region[]>(request).ThrowIfNull();
    }
}