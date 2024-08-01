namespace ConsoleApp.Endpoints;

public sealed record class Specification
{
    public required string Name { get; init; }
    public required string Code { get; init; }
}

public static class SpecificationEndpoints
{
    public static Specification[] GetSpecifications(Guid projectGuid, string eventType)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/eventtype/{eventType}/specification");
        request.Method = Method.Get;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddUrlSegment("eventType", eventType);

        Specification[] specifications = Rest.GetResponseData<Specification[]>(request) ?? [];
        return specifications;
    }
}