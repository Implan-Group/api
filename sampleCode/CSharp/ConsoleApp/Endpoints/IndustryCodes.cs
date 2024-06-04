namespace ConsoleApp.Endpoints;

public sealed record class IndustryCode
{
    public int Id { get; set; }
    public int Code { get; set; }
    public string Description { get; set; }
}

public static class IndustryCodes
{
    public static IndustryCode[] GetIndustryCodes(int? aggregationSchemeId = null, int? industrySetId = null)
    {
        // {{api_domain}}api/v1/IndustryCodes?industrySetId=
        RestRequest request;
        if (aggregationSchemeId is null)
        {
            request = new RestRequest("api/v1/IndustryCodes");
        }
        else
        {
            request = new RestRequest("api/v1/IndustryCodes/{aggregationSchemeId}");
            request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId.Value);
        }

        if (industrySetId is not null)
        {
            request.AddParameter("industrySetId", industrySetId.Value);
        }

        return Rest.GetResponseData<IndustryCode[]>(request).ThrowIfNull();
    }
}