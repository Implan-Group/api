﻿namespace ConsoleApp.Endpoints;

public sealed record class AggregationScheme
{
    public int Id { get; set; }
    public string Description { get; set; }
    public int IndustrySetId { get; set; }
    public int[] HouseholdSetIds { get; set; }
    public string MapCode { get; set; }
    public string Status { get; set; }
}

/// <remarks>the default Aggregation Scheme ID is 8: Unaggregated 546 Industries</remarks>
public static class AggregationSchemes
{
    public static AggregationScheme[] GetAggregationSchemes(int? industrySetId = null)
    {
        //GET {api_domain}api/v1/aggregationschemes?industrySetId={industrySetId}
        RestRequest request = new RestRequest("api/v1/aggregationSchemes");
        request.Method = Method.Get;
        if (industrySetId is not null)
        {
            request.AddParameter("industrySetId", industrySetId.Value);
        }
        
        return Rest.GetResponseData<AggregationScheme[]>(request);
    }
}