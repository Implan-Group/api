namespace ConsoleApp.Endpoints;

public sealed record class IndustrySet
{
    public int Id { get; set; }
    public string Description { get; set; }
    public int? DefaultAggregationSchemeId { get; set; }
    public bool? ActiveStatus { get; set; }
    public bool? IsDefault { get; set; }
    public int? MapTypeId { get; set; }
    public bool IsNaicsCompatible { get; set; }
}

public static class IndustrySets
{
    public static IndustrySet? GetIndustrySet(int industrySetId)
    {
        //[Route("external/api/v1/industry-sets")]
        var request = new RestRequest("api/v1/industry-sets/{industrySetId}");
        request.Method = Method.Get;
        request.AddUrlSegment("industrySetId", industrySetId);
        return Rest.GetResponseData<IndustrySet?>(request);
    }
    
    public static IndustrySet[] GetIndustrySets()
    {
        var request = new RestRequest("api/v1/industry-sets");
        request.Method = Method.Get;

        return Rest.GetResponseData<IndustrySet[]>(request).ThrowIfNull();
    }
}