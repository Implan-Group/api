namespace ConsoleApp.Endpoints;

public sealed record class DataSet
{
    public int Id { get; set; }
    public string Description { get; set; }
    public bool IsDefault { get; set; }
}

public static class DataSetEndpoints
{
    public static DataSet[] GetDataSets(int aggregationSchemeId)
    {
        RestRequest request = new RestRequest("api/v1/datasets/{aggregationSchemeId}");
        request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId);
        request.Method = Method.Get;

        return Rest.GetResponseData<DataSet[]>(request).ThrowIfNull();
    }
}