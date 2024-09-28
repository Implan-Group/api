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
