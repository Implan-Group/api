namespace ConsoleApp.Regions;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

public static class RegionEndpoints
{
    /// <summary>
    /// Gets a list of all Region Types
    /// </summary>
    public static string[] GetRegionTypes()
    {
#if LOCAL
        RestRequest request = new RestRequest("api/v1/region/region-types");
#else
        RestRequest request = new RestRequest("api/v1/region/RegionTypes");
#endif
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
        RestRequest request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);

        return Rest.GetResponseData<Region>(request).ThrowIfNull();
    }
    
    public static Region? GetRegion(int aggregationSchemeId, int dataSetId, string hashIdOrUrid)
    {
        var request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/{hashIdOrUrid}");
        request.Method = Method.Get;
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.AddUrlSegment("dataSetId", dataSetId);
        request.AddUrlSegment("hashIdOrUrid", hashIdOrUrid);
    
        return Rest.GetResponseData<Region>(request);
    }

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
        
        // There are different routes depending on our filters
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
        RestRequest request = new RestRequest("api/v1/region/{aggregationSchemeId}/{dataSetId}/user");
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
        RestRequest request = new RestRequest("api/v1/region/build/combined/{aggregationSchemeId}");
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
