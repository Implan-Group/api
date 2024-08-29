namespace ConsoleApp.Endpoints;

public static class ImpactEndpoints
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
        RestRequest request = new RestRequest("api/v1/impact/{projectId}");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);

        long impactRunId = Rest.GetResponseData<long>(request);
        return impactRunId;
    }

    /// <summary>
    /// Gets the current Status for the Impact Analysis with the given <paramref name="impactRunId"/>
    /// </summary>
    /// <param name="impactRunId">
    /// The Project's Impact Run Identifier
    /// </param>
    /// <returns>
    /// <list type="bullet">
    /// <listheader>
    /// The current status of the Impact Analysis, one of:
    /// </listheader>
    /// <item>Unknown</item>
    /// <item>New</item>
    /// <item>InProgress</item>
    /// <item>ReadyForWarehouse</item>
    /// <item>Complete</item>
    /// <item>Error</item>
    /// <item>UserCancelled</item>
    /// </list>
    /// </returns>
    public static string GetImpactStatus(long impactRunId)
    {
        RestRequest request = new RestRequest("api/v1/impact/status/{impactRunId}");
        request.Method = Method.Get;
        request.AddUrlSegment("impactRunId", impactRunId);

        string? status = Rest.GetResponseContent(request);
        return status ?? "Unknown";
    }

    /// <summary>
    /// Tries to cancel a running Impact Analysis
    /// </summary>
    /// <param name="impactRunId">
    /// The Project's Impact Run Identifier
    /// </param>
    /// <returns>
    /// <c>true</c> if the Impact Analysis was able to be cancelled,
    /// <c>false</c> otherwise
    /// </returns>
    public static bool CancelImpact(long impactRunId)
    {
        RestRequest request = new RestRequest("api/v1/impact/cancel/{impactRunId}");
        request.Method = Method.Put;
        request.AddUrlSegment("impactRunId", impactRunId);

        string? result = Rest.GetResponseContent(request);
        return string.Equals(result, "Analysis run cancelled.", StringComparison.OrdinalIgnoreCase);
    }
}