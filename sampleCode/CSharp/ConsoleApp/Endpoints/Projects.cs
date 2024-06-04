﻿namespace ConsoleApp.Endpoints;

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
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Project>(request).ThrowIfNull();
    }
}