using ConsoleApp.Services;
using RestSharp;

namespace ConsoleApp.AggregationSchemes;

public sealed record class AggregationScheme
{
    public int Id { get; set; }
    public string Description { get; set; }
    public int IndustrySetId { get; set; }
    public int[] HouseholdSetIds { get; set; }
    public string MapCode { get; set; }
    public string Status { get; set; }
}

public class AggregationSchemes
{
    public static AggregationScheme[] GetAggregationSchemes(int? industrySetId = null)
    {
        //GET {api_domain}api/v1/aggregationschemes?industrySetId={industrySetId}
        var request = new RestRequest("api/v1/aggregationSchemes");
        if (industrySetId is not null)
        {
            request.AddParameter("industrySetId", industrySetId.Value);
        }
        request.Method = Method.Get;

        return Rest.GetResponseData<AggregationScheme[]>(request);
    }
    
    
    //AddUrlSegment works with placeholder values in the request URL
    // {entity}
}