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

        long impactRunId = Rest.GetResponseData<long>(request);
        return impactRunId;
    }

    /// <summary>
    /// 
    /// </summary>
    /// <param name="impactRunId"></param>
    /// <returns>
    /// The current status of the Impact Run, one of:
    /// Unknown
    /// New
    /// InProgress
    /// ReadyForWarehouse
    /// Complete
    /// Error
    /// </returns>
    public static string GetImpactStatus(long impactRunId)
    {
        var request = new RestRequest("api/v1/impact/status/{impactRunId}");
        request.Method = Method.Get;
        request.AddUrlSegment("impactRunId", impactRunId);

        string status = Rest.GetResponseData<string>(request).ThrowIfNull();
        return status;
    }
}