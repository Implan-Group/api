using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 7: RunImpactAnalysis.
/// </summary>
/// <remarks>
/// Goal: run a project, wait for it correctly, and download every standard report.
///
/// Running is asynchronous. The POST returns a run id immediately and the analysis
/// takes a few minutes, so the interesting part of this workflow is the waiting, and
/// specifically knowing when to stop:
///
///   - <c>Complete</c> means the results are ready.
///   - <c>Error</c> and <c>UserCancelled</c> are terminal. Polling past them waits
///     forever, which is the bug in most first attempts at this.
///   - A 404 from the status endpoint is also terminal, and means the run never
///     attached to a project. The usual cause is a Group saved without a dollar year.
///
/// Poll the status endpoint and not the results endpoints. Status is cheap; results
/// are not, and reading one before the run finishes produces an error that reads
/// like a different problem.
///
/// Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
/// Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results
/// </remarks>
public static class RunImpactAnalysisWorkflow
{
    /// <summary>The four query-filtered reports, and the file each is saved as.</summary>
    private static readonly (string Label, Func<ApiClient, long, ResultFilters?, string> Fetch)[] Reports =
    [
        ("Summary Economic Indicators", ImpactResults.GetSummaryEconomicIndicators),
        ("Detailed Economic Indicators", ImpactResults.GetDetailedEconomicIndicators),
        ("Summary Taxes", ImpactResults.GetSummaryTaxes),
        ("Detailed Taxes", ImpactResults.GetDetailedTaxes),
    ];

    public static long Run(Guid? projectId = null)
    {
        var client = Auth.CreateClient();

        // Step 1. Find the project. Passing an id is the normal path; without one,
        // the most recently created project is used, which makes this easy to chain
        // after CreateProject.
        ConsoleLog.Heading("Step 1: find the Project");
        Project project;
        if (projectId is null)
        {
            // GET /api/v1/impact/project  (wiki: Get Projects)
            var mine = Projects.GetProjects(client);
            if (mine.Count == 0)
            {
                throw new KeyNotFoundException(
                    "You have no projects. Run the CreateProject workflow first, or pass --project-id.");
            }

            // The API returns projects oldest first, so the newest is last.
            project = mine[^1];
            ConsoleLog.Info("  no --project-id given, so using your most recent project");
        }
        else
        {
            // GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
            project = Projects.GetProject(client, projectId.Value);
        }

        ConsoleLog.Info("  {0}", project.Describe());

        // Projects other people have shared with you can be run too; this is how you
        // find them.
        // GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
        var shared = Projects.GetSharedProjects(client);
        ConsoleLog.Info("  ({0} projects have also been shared with you)", shared.Count);

        // Step 2. Start the run.
        ConsoleLog.Heading("Step 2: start the impact");

        // POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
        var runId = Impacts.RunImpact(client, project.Id!.Value);
        ConsoleLog.Info("  run id {0}", runId);
        ConsoleLog.Info("  a run id means the request was accepted, not that it succeeded");

        // Step 3. Wait. The helper handles the terminal states and the timeout,
        // which is the part worth copying.
        ConsoleLog.Heading("Step 3: wait for it to finish");
        ConsoleLog.Info("  polling every {0:F0}s, giving up after {1:F0} minutes",
            Config.ImpactPollInterval.TotalSeconds, Config.ImpactTimeout.TotalMinutes);

        // GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
        Impacts.WaitForImpact(client, runId);
        ConsoleLog.Info("  complete");

        // Cancelling is the other half of this endpoint pair. Not run here, but this
        // is the call:
        //
        //   Impacts.CancelImpact(client, runId);
        //
        // PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)

        // Step 4. Download the reports. Every one of them is CSV text.
        ConsoleLog.Heading("Step 4: download the results");
        var destination = Path.Combine(
            Config.ReportsDirectory, ImpactResults.SafeFileName(project.Title));

        // Setting the dollar year explicitly keeps repeated runs comparable. Left
        // unset, the API uses your account preference, which may differ from a
        // colleague's.
        var filters = new ResultFilters { Year = Config.CurrentDollarYear };
        ConsoleLog.Info("  dollar year {0}", filters.Year);

        foreach (var (label, fetch) in Reports)
        {
            // GET /api/v1/impact/results/...  (wiki: Impact Results)
            var csv = fetch(client, runId, filters);
            ImpactResults.SaveCsv(csv, Path.Combine(destination, $"{label}.csv"));
        }

        // Estimated Growth Percentage is the odd one out: its filters go in a JSON
        // body on a GET, and all five lists have to be present even when empty.
        var growthRequest = new ImpactResultsExportRequest { DollarYear = Config.CurrentDollarYear };

        // GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}, with a JSON body
        // (wiki: Results - Estimated Growth Percentage)
        var growthCsv = ImpactResults.GetEstimatedGrowthPercentage(client, runId, growthRequest);
        ImpactResults.SaveCsv(growthCsv, Path.Combine(destination, "Estimated Growth Percentage.csv"));

        // Step 5. Confirm what landed. A report whose first line is JSON rather than
        // a header row means something went wrong that the status check did not catch.
        ConsoleLog.Heading("Step 5: check the files");
        foreach (var path in Directory.GetFiles(destination, "*.csv").Order())
        {
            var firstLine = File.ReadLines(path).FirstOrDefault() ?? string.Empty;
            var looksLikeCsv = firstLine.Contains(',') && !firstLine.StartsWith('{');
            ConsoleLog.Info("  {0,-34} {1}  {2}",
                Path.GetFileName(path),
                looksLikeCsv ? "ok " : "??",
                firstLine.Length > 60 ? firstLine[..60] : firstLine);
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Run id:  {0}", runId);
        ConsoleLog.Info("Reports: {0}", destination);
        return runId;
    }
}
