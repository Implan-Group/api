namespace ConsoleApp.Endpoints;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

public sealed record class Project
{
    /// <summary>
    /// The unique identifier for this Project
    /// </summary>
    public Guid Id { get; set; }
    /// <summary>
    /// The unique description for this Project
    /// </summary>
    public required string Title { get; set; }
    /// <summary>
    /// The Aggregation Scheme this Project is using
    /// </summary>
    public required int AggregationSchemeId { get; set; }
    /// <summary>
    /// The Household Set this Project is using
    /// </summary>
    public required int HouseholdSetId { get; set; }
    /// <summary>
    /// Whether or not this Project is using Multi-Region Input/Output (MRIO) Analysis
    /// </summary>
    public bool IsMrio { get; set; } = false;
    /// <summary>
    /// If present, the identifier of the Folder that the Project is located under in IMPLAN Cloud
    /// </summary>
    public int? FolderId { get; set; } = null;
    /// <summary>
    /// If an Impact Analysis has already been performed for this Project, the Id of the last one (used for querying Analysis status)
    /// </summary>
    public long? LastImpactRunId { get; set; } = null;
}

public class ProjectEndpoints
{
    public static Project Create(Project project)
    {
        RestRequest request = new RestRequest("api/v1/impact/project");
        request.Method = Method.Post;
        
        // The body must be the Jsonified Project model
        request.AddJsonBody(project);

        return Rest.GetResponseData<Project>(request).ThrowIfNull();
    }

    public static Project GetProject(Guid projectGuid)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}");
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
        RestRequest request = new RestRequest("api/v1/impact/project");
        request.Method = Method.Get;

        return Rest.GetResponseData<Project[]>(request).ThrowIfNull();
    }

    /// <summary>
    /// Returns a list of <see cref="Project"/>s that have been shared with the currently Authorized Implan User
    /// </summary>
    /// <returns></returns>
    public static Project[] GetSharedProjects()
    {
        RestRequest request = new RestRequest("api/v1/impact/project/shared");
        request.Method = Method.Get;

        return Rest.GetResponseData<Project[]>(request).ThrowIfNull();
    }
}
