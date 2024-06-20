using System.Diagnostics.CodeAnalysis;

namespace ConsoleApp.Endpoints;

/// <summary>
/// An Event to be added to a Group
/// </summary>
public sealed record class GroupEvent
{
    public GroupEvent()
    {
    }

    [SetsRequiredMembers]
    public GroupEvent(Guid eventId)
    {
        EventId = eventId;
    }

    /// <summary>
    /// The <see cref="Guid"/> Id for the Event to associate
    /// </summary>
    public required Guid EventId { get; init; }
    /// <summary>
    /// Percentage (0.0 .. 1.0) of Scaling to apply to this Event
    /// </summary>
    public double ScalingFactor { get; set; } = 1.0d;
}

/// <summary>
/// 
/// </summary>
/// <remarks>
/// Only one of <see cref="HashId"/>, <see cref="Urid"/>, <see cref="ModelId"/>, or <see cref="UserModelId"/> should be specified in the Request Body
/// `HashId` is the preferred option
/// </remarks>
public sealed record class Group
{
    /// <summary>
    /// Unique-per-Project Name for this Group
    /// </summary>
    public required string Title { get; init; }

    /// <summary>
    /// Unique identifier for this Group, will be created during the `CreateGroup` endpoint call -- do not specify in incoming body
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// The Project's GUID Identifier -- does not need to be in incoming body as it is passed as an Url parameter
    /// </summary>
    public Guid ProjectId { get; set; }

    /// <summary>
    /// The HashId for the Region to associate with this Group
    /// </summary>
    public string? HashId { get; set; }

    /// <summary>
    /// The URID for the associated Region
    /// </summary>
    public long? Urid { get; set; }

    /// <summary>
    /// The User Model Id for the associated Region
    /// </summary>
    public int? UserModelId { get; set; }

    /// <summary>
    /// The Model Id for the associated Region
    /// </summary>
    public int? ModelId { get; set; }

    /// <summary>
    /// The Dollar Year for the Group (same as 4-digit year)
    /// </summary>
    public int? DollarYear { get; set; }
    /// <summary>
    /// Percentage (0.0 .. 1.0) of Scaling to apply to this Group
    /// </summary>
    public double ScalingFactor { get; set; } = 1.0d;
    /// <summary>
    /// The Data Set Id for the Group (see above)
    /// </summary>
    public int? DatasetId { get; set; }
    /// <summary>
    /// A list of the Events to associate with this Group
    /// </summary>
    public GroupEvent[] GroupEvents { get; set; } = [];
}

public static class Groups
{
    public static Group AddGroupToProject(Guid projectGuid, Group group)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/group");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(group);

        Group responseGroup = Rest.GetResponseData<Group>(request).ThrowIfNull();
        return responseGroup;
    }
}