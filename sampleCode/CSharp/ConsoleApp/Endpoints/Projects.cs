namespace ConsoleApp.Endpoints;

public sealed record class Project
{
    public Guid Id { get; set; }
    public string Title { get; set; }
    public int AggregationSchemeId { get; set; }
    public int HouseholdSetId { get; set; }
    public bool IsMrio { get; set; }
    public int? FolderId { get; set; }
    public long? LastImpactRunId { get; set; }
}

public class Projects
{
    public static Project Create(Project project)
    {
        // POST {{api_domain}}api/v1/impact/project
        var request = new RestRequest("api/v1/impact/project");
        request.Method = Method.Post;
        
        // The body must be the Jsonified Project model
        request.AddJsonBody(project);

        return Rest.GetResponseData<Project>(request);
    }

    public static Project GetProject(Guid projectGuid)
    {
        // {{api_domain}}api/v1/impact/project/:projectGuid
        var request = new RestRequest("api/v1/impact/project/{projectGuid}");
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Project>(request);
    }
}