namespace ConsoleApp.Endpoints;

public sealed record class Project
{
    public Guid Id { get; set; }
    public required string Title { get; set; }
    public required int AggregationSchemeId { get; set; }
    public required int HouseholdSetId { get; set; }
    public bool IsMrio { get; set; } = false;
    public int? FolderId { get; set; } = null;
    public long? LastImpactRunId { get; set; } = null;
}

public class Projects
{
    public static Project Create(Project project)
    {
        var request = new RestRequest("api/v1/impact/project");
        request.Method = Method.Post;
        
        // The body must be the Jsonified Project model
        request.AddJsonBody(project);

        return Rest.GetResponseData<Project>(request).ThrowIfNull();
    }

    public static Project GetProject(Guid projectGuid)
    {
        var request = new RestRequest("api/v1/impact/project/{projectGuid}");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Project>(request).ThrowIfNull();
    }

    /// <summary>
    /// Returns a list of <see cref="Project"/>s that belong to the currently Authorized Implan User
    /// </summary>
    /// <returns></returns>
    public static Project[] GetProjects()
    {
        var request = new RestRequest("api/v1/impact/project");
        request.Method = Method.Get;

        return Rest.GetResponseData<Project[]>(request).ThrowIfNull();
    }

    /// <summary>
    /// Returns a list of <see cref="Project"/>s that have been shared with the currently Authorized Implan User
    /// </summary>
    /// <returns></returns>
    public static Project[] GetSharedProjects()
    {
        var request = new RestRequest("api/v1/impact/project/shared");
        request.Method = Method.Get;

        return Rest.GetResponseData<Project[]>(request).ThrowIfNull();
    }
}