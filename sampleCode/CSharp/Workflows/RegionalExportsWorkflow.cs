using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 9: RegionalExports.
/// </summary>
/// <remarks>
/// Goal: download a regional data export for many regions, without tripping the rate
/// limit.
///
/// Regional data exports describe a region's economy as it already is, so they need
/// no project and no impact run, only a built region. Wanting one for every MSA, or
/// every county in a state, is common.
///
/// The naive version of this asks each region for its status, then downloads. That
/// is one extra call per region, which for three thousand counties is hours of
/// waiting under the published five-region-model-requests-per-minute limit. It is
/// also unnecessary: the children listing already carries the build status for every
/// region it returns, so one call gives both the list and which of them are ready.
///
/// So the shape here is:
///
///   1. One children call: every region, with its build status.
///   2. One build-and-return call for whichever are not built, then wait.
///   3. Download, skipping any file already on disk so a re-run resumes.
///
/// The export is a parameter. RegionOverviewIndustries and the single-file GAMS
/// export are named for convenience, but any report from the wiki's Regional Data
/// Exports section can be passed by name.
///
/// Wiki: Regional Data Exports
/// https://github.com/Implan-Group/api/wiki/Regional-Data-Exports
/// </remarks>
public static class RegionalExportsWorkflow
{
    private const int RegionRequestsPerMinute = 5;

    /// <summary>How many regions to ask for in one build-and-return call.</summary>
    private const int BuildBatchSize = 25;

    /// <summary>
    /// Downloads one export for every region of a type.
    /// </summary>
    /// <param name="regionType">Which regions to export.</param>
    /// <param name="exportName">Which report to download.</param>
    /// <param name="limit">
    /// Caps how many regions are processed, which keeps a first run short. Pass null
    /// to process all of them, and expect it to take a while: the rate limit, not
    /// the API's speed, sets the pace.
    /// </param>
    public static void Run(
        RegionType regionType = RegionType.Msa,
        string exportName = RegionalDataExports.RegionOverviewIndustries,
        int? limit = 10)
    {
        var client = Auth.CreateClient();
        client.RateLimiter = new RateLimiter(RegionRequestsPerMinute);

        // Step 1. Resolve identifiers.
        ConsoleLog.Heading("Step 1: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. One call for the list and the build status together. This is the
        // step that keeps the workflow inside the rate limit.
        ConsoleLog.Heading("Step 2: list the regions, with their build status");

        // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
        // (wiki: Regional Children)
        var found = Regions.GetRegionChildren(
            client, ids.AggregationSchemeId, ids.DatasetId, regionType: regionType);
        ConsoleLog.Info("  {0} regions of type {1}", found.Count, regionType);

        if (limit is not null && found.Count > limit)
        {
            found = found.Take(limit.Value).ToList();
            ConsoleLog.Info("  limited to the first {0} for this run", limit);
        }

        var built = found.Where(r => r.IsBuilt).ToList();
        var unbuilt = found.Where(r => !r.IsBuilt).ToList();
        ConsoleLog.Info("  {0} already built, {1} not yet", built.Count, unbuilt.Count);
        ConsoleLog.Info("  (that status came from the same call as the list, so this cost");
        ConsoleLog.Info("   one request rather than one per region)");

        // Step 3. Build whatever is missing.
        if (unbuilt.Count > 0)
        {
            ConsoleLog.Heading("Step 3: build the models that are missing");
            for (var start = 0; start < unbuilt.Count; start += BuildBatchSize)
            {
                var batch = unbuilt.Skip(start).Take(BuildBatchSize).ToList();
                ConsoleLog.Info("  requesting {0} models ({1} to {2} of {3})",
                    batch.Count, start + 1, start + batch.Count, unbuilt.Count);

                // POST /api/v1/region/build-and-return/{aggregationSchemeId}
                // (wiki: Build and Return Regions)
                Regions.BuildAndReturnRegions(
                    client, ids.AggregationSchemeId, batch.Select(r => r.HashId).ToList());

                // These are IMPLAN regions rather than user regions, so the
                // user-region endpoint does not see them. Give the queue time to
                // work and let the download step treat a 400 as "still building".
                Thread.Sleep(TimeSpan.FromSeconds(30));
            }
        }
        else
        {
            ConsoleLog.Heading("Step 3: nothing to build");
            ConsoleLog.Info("  every region already has a model");
        }

        // Step 4. Download. Skipping files already on disk makes a re-run resume
        // rather than start over, which matters when the whole job takes an hour.
        ConsoleLog.Heading("Step 4: download the export for each region");
        var extension = RegionalDataExports.FileExtensionFor(exportName);
        var destination = Path.Combine(
            Config.ReportsDirectory,
            $"{exportName}-agg{ids.AggregationSchemeId}-ds{ids.DatasetId}");
        Directory.CreateDirectory(destination);
        ConsoleLog.Info("  into {0}", destination);

        int downloaded = 0, skipped = 0, failed = 0;

        foreach (var region in found)
        {
            var path = Path.Combine(
                destination, ImpactResults.SafeFileName(region.Description) + extension);

            if (File.Exists(path))
            {
                skipped++;
                continue;
            }

            string content;
            try
            {
                // GET /api/v1/regions/export/{aggregationSchemeId}/{exportName}?hashId=...
                // (wiki: Regional Data Exports)
                content = RegionalDataExports.GetExport(
                    client, ids.AggregationSchemeId, exportName, region.HashId);
            }
            catch (ImplanApiException error)
            {
                if (error.StatusCode == 400)
                {
                    // From these endpoints a 400 nearly always means the model is
                    // still building rather than that the request was wrong.
                    ConsoleLog.Info("  {0}: not ready yet (400); run again later", region.Description);
                }
                else
                {
                    ConsoleLog.Info("  {0}: {1}", region.Description, error.Problem.Describe());
                }

                failed++;
                continue;
            }

            File.WriteAllText(path, content);
            downloaded++;
            ConsoleLog.Info("  {0}", Path.GetFileName(path));
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Downloaded: {0}", downloaded);
        ConsoleLog.Info("Skipped (already on disk): {0}", skipped);
        ConsoleLog.Info("Not ready or failed: {0}", failed);
        ConsoleLog.Info("Folder: {0}", destination);
        if (failed > 0)
        {
            ConsoleLog.Info();
            ConsoleLog.Info("Run this again to pick up the ones that were still building.");
        }
    }
}
