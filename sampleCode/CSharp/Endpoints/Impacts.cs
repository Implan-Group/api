using System.Diagnostics;

namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Running an impact, and waiting for it.
/// </summary>
/// <remarks>
/// Running is asynchronous. The POST returns a run id straight away, the analysis
/// takes a few minutes, and the status endpoint says when results are ready.
///
/// Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
/// </remarks>
public static class Impacts
{
    /// <summary>
    /// Starts an impact analysis and returns its run id.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
    ///
    /// The Project needs at least one Group holding at least one Event. The response
    /// body is the run id as a bare number, not an object.
    ///
    /// The run id coming back does not mean the analysis started successfully; that
    /// is what the status endpoint is for.
    /// </remarks>
    public static long RunImpact(ApiClient client, Guid projectId)
    {
        var text = client.PostText($"/api/v1/impact/{projectId}").Trim().Trim('"');
        return long.TryParse(text, out var runId)
            ? runId
            : throw new InvalidOperationException(
                $"Expected a run id from RunImpact, got '{text}'.");
    }

    /// <summary>
    /// Reads where an impact run has got to.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/status/{runId}  (wiki: Get Impact Status)
    ///
    /// The body is a bare word such as <c>Complete</c>, sent as plain text rather
    /// than as JSON, so it is read as text. Anything other than <c>Complete</c>
    /// means not ready; <c>Error</c> and <c>UserCancelled</c> mean it stopped and
    /// will not produce results.
    ///
    /// A 404 means the run has no analyses. For a few seconds after a run starts
    /// that is normal, because the analyses are still being created; see
    /// <see cref="WaitForImpact"/>, which allows for it. A 404 that persists means
    /// the run never attached to a project.
    /// </remarks>
    public static ImpactStatus GetImpactStatus(ApiClient client, long runId)
    {
        var text = client.GetText($"/api/v1/impact/status/{runId}").Trim().Trim('"');

        if (Enum.TryParse<ImpactStatus>(text, ignoreCase: true, out var status))
            return status;

        // A status this sample has not seen. Report it rather than guessing.
        ConsoleLog.Debug($"Unrecognized impact status '{text}'");
        return ImpactStatus.Unknown;
    }

    /// <summary>
    /// Cancels a running impact analysis.
    /// </summary>
    /// <remarks>
    /// PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)
    ///
    /// Useful when a run is taking far longer than expected, or when you spotted a
    /// mistake in the Project. Answers with a short sentence confirming the
    /// cancellation.
    /// </remarks>
    public static string CancelImpact(ApiClient client, long runId)
    {
        return client.PutText($"/api/v1/impact/cancel/{runId}").Trim().Trim('"');
    }

    /// <summary>
    /// Polls until an impact run finishes, and returns its final status.
    /// </summary>
    /// <remarks>
    /// Throws on a terminal failure, on a 404 that outlasts the start-up window, and
    /// on a run that has not finished inside the timeout.
    ///
    /// Poll this endpoint and not the results endpoints. The status call is cheap;
    /// the results endpoints are not, and reading one before the run is complete
    /// produces an error that looks like a different problem.
    ///
    /// Expect a 404 on the first poll. For a few seconds after a run starts its
    /// analyses do not exist yet, and status answers 404 "No analyses exist" until
    /// they do; on INT the window was under 20 seconds. So a 404 is treated as "not
    /// registered yet" for the first <see cref="Config.ImpactStartGrace"/>, and only
    /// a 404 that persists past that is reported as a run that never attached.
    /// </remarks>
    public static ImpactStatus WaitForImpact(
        ApiClient client,
        long runId,
        TimeSpan? timeout = null,
        TimeSpan? pollInterval = null)
    {
        var limit = timeout ?? Config.ImpactTimeout;
        var interval = pollInterval ?? Config.ImpactPollInterval;
        var elapsed = Stopwatch.StartNew();
        ImpactStatus? lastStatus = null;
        var saidNotRegistered = false;

        while (true)
        {
            ImpactStatus status;
            try
            {
                status = GetImpactStatus(client, runId);
            }
            catch (ImplanApiException error) when (error.StatusCode == 404)
            {
                if (elapsed.Elapsed < Config.ImpactStartGrace)
                {
                    if (!saidNotRegistered)
                    {
                        ConsoleLog.Info("  run {0}: starting, not registered yet", runId);
                        saidNotRegistered = true;
                    }

                    Thread.Sleep(interval);
                    continue;
                }

                throw new InvalidOperationException(
                    $"Impact run {runId} still has no analyses after "
                    + $"{Config.ImpactStartGrace.TotalSeconds:F0} seconds, which means it never "
                    + "attached to the project. A common cause is a Group saved without a "
                    + "dollar year. This is terminal: fix the Group and run the Project again."
                    + Environment.NewLine + error.Problem.Describe(), error);
            }

            if (status != lastStatus)
            {
                lastStatus = status;
                ConsoleLog.Info("  run {0}: {1}", runId, status);
            }

            if (status == ImpactStatus.Complete)
                return status;

            if (status.IsTerminalFailure())
            {
                throw new InvalidOperationException(
                    $"Impact run {runId} ended with status '{status}'. Check the Project's "
                    + "Events and Groups in IMPLAN Cloud, then run it again.");
            }

            if (elapsed.Elapsed >= limit)
            {
                throw new TimeoutException(
                    $"Impact run {runId} was still '{status}' after {limit.TotalSeconds:F0} "
                    + "seconds. It may still finish; check the Project in IMPLAN Cloud.");
            }

            Thread.Sleep(interval);
        }
    }
}
