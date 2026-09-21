namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Group endpoints.
/// </summary>
/// <remarks>
/// A Group pairs one region and one dollar year with the Events that happen there.
/// An analysis comparing three states is three Groups holding the same Events.
///
/// Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
/// </remarks>
public static class Groups
{
    /// <summary>
    /// Adds a Group to a Project and returns it with its generated id.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
    ///
    /// Supply exactly one region identifier, and always supply the dollar year:
    /// there is no server-side default, and a Group stored without one produces an
    /// impact run that never attaches, which surfaces later as a 404 from the status
    /// endpoint rather than as an error here.
    ///
    /// Every event id in the group has to belong to this Project; one that does not
    /// earns a 422 naming the problem.
    /// </remarks>
    public static Group CreateGroup(ApiClient client, Guid projectId, Group group)
    {
        return client.PostJson<Group>($"/api/v1/impact/project/{projectId}/group", group);
    }

    /// <summary>
    /// Lists every Group in a Project.
    /// </summary>
    /// <remarks>GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)</remarks>
    public static List<Group> GetGroups(ApiClient client, Guid projectId)
    {
        return client.GetJson<List<Group>>($"/api/v1/impact/project/{projectId}/group");
    }

    /// <summary>
    /// Reads one Group.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}/group/{groupId}  (wiki: Get Group)
    ///
    /// Read a single Group rather than scanning the list when you care about a
    /// Group's scaling factors; the single-Group read is the authoritative one.
    /// </remarks>
    public static Group GetGroup(ApiClient client, Guid projectId, Guid groupId)
    {
        return client.GetJson<Group>($"/api/v1/impact/project/{projectId}/group/{groupId}");
    }

    /// <summary>
    /// Removes a Group from a Project.
    /// </summary>
    /// <remarks>
    /// DELETE /api/v1/impact/project/{projectId}/group/{groupId}  (wiki: Delete Group)
    /// </remarks>
    public static void DeleteGroup(ApiClient client, Guid projectId, Guid groupId)
    {
        client.Delete($"/api/v1/impact/project/{projectId}/group/{groupId}");
    }
}
