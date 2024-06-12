using System.Diagnostics.CodeAnalysis;

namespace ConsoleApp.Endpoints;

public sealed record class Region
{
    /// <summary>
    /// The HashId for this Region (used to reference this exact Region)
    /// </summary>
    public string HashId { get; set; }
    /// <summary>
    /// The URID for this Region (depreciated way to reference this exact Region)
    /// </summary>
    public long? Urid { get; set; }
    /// <summary>
    /// The User's Model Id for this Region, filled in for Combined and Customized Regions
    /// </summary>
    public int? UserModelId { get; set; }
    /// <summary>
    /// The description of this Region
    /// </summary>
    public string Description { get; set; }
    /// <summary>
    /// Unique identifier for a particular model, used internally
    /// </summary>
    public int? ModelId { get; set; }
    /// <summary>
    /// The current status of the Model's Build progress. Certain complex Models may take time to process until they are `Complete`
    /// </summary>
    public string ModelBuildStatus { get; set; }
    /// <summary>
    /// Total employment value for this Region
    /// </summary>
    public double? Employment { get; set; }
    /// <summary>
    /// Total industry output value for this Region
    /// </summary>
    public double? Output { get; set; }
    /// <summary>
    /// Total value-added for this Region
    /// </summary>
    public double? ValueAdded { get; set; }
    /// <summary>
    /// The Aggregation Scheme that includes this Region
    /// </summary>
    public int AggregationSchemeId { get; set; }
    /// <summary>
    /// The Dataset that includes this Region
    /// </summary>
    public int DatasetId { get; set; }
    /// <summary>
    /// A description of the Dataset that usually includes the Data Year
    /// </summary>
    public string DatasetDescription { get; set; }
    /// <summary>
    /// The Federal Information Processing Standards (FIPS) Code for this Region
    /// </summary>
    public string? FipsCode { get; set; }
    /// <summary>
    /// If a Canadian Region, the Code for the Province
    /// </summary>
    public string? ProvinceCode { get; set; }
    /// <summary>
    /// The M49 standard Code for this Region
    /// </summary>
    public string? M49Code { get; set; }
    /// <summary>
    /// The Region's Type, one of:
    /// `country`, `state`, `msa`, `county`, `Congressional District`, `zipcode`
    /// </summary>
    public string RegionType { get; set; }
    /// <summary>
    /// Whether or not this Region has other children Regions associated with it
    /// e.g. A `state` has many `county` and `zipcode` children
    /// </summary>
    public bool HasAccessibleChildren { get; set; }
    /// <summary>
    /// A further description of the <see cref="RegionType"/>
    /// </summary>
    public string RegionTypeDescription { get; set; }
    /// <summary>
    /// The first non-`null` value among <see cref="ProvinceCode"/>, <see cref="FipsCode"/>, or <see cref="M49Code"/> (in that order) (used internally)
    /// </summary>
    public string? GeoId { get; set; }
    /// <summary>
    /// Whether or not the Region supports Multi-Region Input/Ouput  (MRIO) Analysis
    /// </summary>
    public bool IsMrioAllowed { get; set; }
}

public class CombineRegionRequest
{
    /// <summary>
    /// A unique-per-Project description for this Combined Region
    /// </summary>
    public string Description { get; set; }

    /// <summary>
    /// An array of the HashIds for all the Regions to be combined
    /// </summary>
    public string[] HashIds { get; set; } = [];

    /// <summary>
    /// An array of the Urids for all the Regions to be combined
    /// </summary>
    public long[] Urids { get; set; } = [];
}   

public static class Regions
{
    /// <summary>
    /// Gets a list of all Region Types
    /// </summary>
    public static string[] GetRegionTypes()
    {
        var request = new RestRequest("api/v1/region/RegionTypes");
        //var request = new RestRequest("api/v1/region/region-types");
        request.Method = Method.Get;

        return Rest.GetResponseData<string[]>(request).ThrowIfNull();
    }

    /// <summary>
    /// Gets the Top-Level Region for a given Aggregation Scheme and Dataset
    /// </summary>
    /// <param name="aggregationSchemeId"></param>
    /// <param name="dataSetId"></param>
    /// <returns></returns>
    public static Region GetTopLevelRegion(int aggregationSchemeId, int dataSetId)
    {
        var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);

        return Rest.GetResponseData<Region>(request).ThrowIfNull();
    }

    // TODO: This endpoint does not currently work with HashIds, PHX-12050 will add this feature
    // [return: MaybeNull]
    // public static Region? GetRegion(int aggregationSchemeId, int dataSetId, string hashIdOrUrid)
    // {
    //     var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/{hashIdOrUrid}");
    //     request.Method = Method.Get;
    //     request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
    //     request.AddUrlSegment("dataSetId", dataSetId);
    //     request.AddUrlSegment("hashIdOrUrid", hashIdOrUrid);
    //
    //     return Rest.GetResponseData<Region>(request);
    // }

    /// <summary>
    /// Returns all the child Regions for an Aggregation Scheme and Dataset
    /// </summary>
    /// <param name="aggregationSchemeId">
    /// Required Aggregation Scheme Id
    /// </param>
    /// <param name="dataSetId">
    /// Required Data Set Id
    /// </param>
    /// <param name="hashIdOrUrid">
    /// Optional HashId or Urid (for filtering)
    /// </param>
    /// <param name="regionType">
    /// Optional RegionType (for filtering) (find with <see cref="GetRegionTypes"/>)
    /// </param>
    /// <returns>
    /// An array of Regions that match the given filters
    /// </returns>
    public static Region[] GetRegionChildren(
        int aggregationSchemeId, int dataSetId, 
        string? hashIdOrUrid = null,
        string? regionType = null)
    {
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

    /// <summary>
    /// Returns an array of all the user-defined Regions for an Aggregation Scheme and Dataset
    /// </summary>
    /// <param name="aggregationSchemeId">
    /// Required Aggregation Scheme Id
    /// </param>
    /// <param name="dataSetId">
    /// Required Data Set Id
    /// </param>
    /// <returns>
    /// An array of user Regions that match the given filters
    /// </returns>
    public static Region[] GetUserRegions(int aggregationSchemeId, int dataSetId)
    {
        var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/user");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);

        return Rest.GetResponseData<Region[]>(request).ThrowIfNull();
    }

    
    /// <summary>
    /// Combines multiple Regions into a single Combined Region
    /// </summary>
    /// <param name="aggregationSchemeId">
    /// Required Aggregation Scheme Id
    /// </param>
    /// <param name="payload">
    /// Required <see cref="CombineRegionRequest"/> that details which Regions are to be Combined under what Name
    /// </param>
    /// <returns>
    /// The combined <see cref="Region"/>
    /// </returns>
    public static Region CombineRegions(int aggregationSchemeId, CombineRegionRequest payload)
    {
        var request = new RestRequest("api/v1/region/build/combined/{aggregationSchemeId}");
        request.Method = Method.Post;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddJsonBody(payload);
        
        // This endpoint returns an array of Regions, but there should only be a single Region in it (the one we're building)
        Region[] regions = Rest.GetResponseData<Region[]>(request).ThrowIfNull();
        if (regions.Length != 1)
            throw new UnreachableException();

        Region region = regions[0];
        return region;
    }
}