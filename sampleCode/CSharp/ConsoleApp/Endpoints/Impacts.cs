namespace ConsoleApp.Endpoints;

public static class Impacts
{
    /// <summary>
    /// Runs the Impact for the Project with the given <paramref name="projectGuid"/>
    /// </summary>
    /// <param name="projectGuid">
    /// The Project's Id
    /// </param>
    /// <returns>
    /// An <see cref="Int64"/> Impact Run Id that can be used to query for Impact Run Status
    /// </returns>
    public static long RunImpact(Guid projectGuid)
    {
        var request = new RestRequest("api/v1/impact/{projectId}");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);

        long impactId = Rest.GetResponseData<long>(request);
        return impactId;
    }
}