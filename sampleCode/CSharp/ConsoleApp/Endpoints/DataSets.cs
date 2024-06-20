namespace ConsoleApp.Endpoints;

public sealed record class DataSet
{
    public int Id { get; set; }
    public string Description { get; set; }
    public bool IsDefault { get; set; }
}

public class DataSets
{
    public static DataSet[] GetDataSets(int aggregationSchemeId)
    {
        // GET {api_domain}api/v1/datasets/{aggregationSchemeId}
        RestRequest request = new RestRequest("api/v1/datasets/{aggregationSchemeId}");
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.Method = Method.Get;

        return Rest.GetResponseData<DataSet[]>(request).ThrowIfNull();
    }
}