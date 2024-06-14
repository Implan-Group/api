namespace ConsoleApp.Endpoints;

public sealed record class GroupEvent
{
    public Guid EventId { get; set; }
    public double ScalingFactor { get; set; } = 1.0d;
}

public sealed record class Group
{
    public Guid Id { get; set; }
    public Guid ProjectId { get; set; }
    public string? HashId { get; set; }
    public long? Urid { get; set; }
    public int? UserModelId { get; set; }
    public int? ModelId { get; set; }
    public string Title { get; set; }
    public int? DollarYear { get; set; }
    public double ScalingFactor { get; set; } = 1.0d;
    public int? DatasetId { get; set; }
    public GroupEvent[] GroupEvents { get; set; } = [];
}

public static class Groups
{
    public static Group AddGroup(Guid projectGuid, Group group)
    {
        // [HttpPost("external/api/v1/impact/project/{projectId}/group")]
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/group");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(group);

        return Rest.GetResponseData<Group>(request).ThrowIfNull();
    }
}