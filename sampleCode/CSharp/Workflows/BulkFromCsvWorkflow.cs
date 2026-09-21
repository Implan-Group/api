using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 8: BulkFromCsv.
/// </summary>
/// <remarks>
/// Goal: drive many regions, projects, and runs from input files.
///
/// This is what batch work looks like in practice. An analyst keeps the study areas
/// and the events in spreadsheets, and the script turns them into combined regions,
/// one project per region, and a final project holding all of them.
///
/// Three habits make the difference between a script that finishes and one that
/// trips the rate limit or falls over halfway:
///
///   - Look up regions once and cache the lookup. The FIPS-to-region map is built
///     from two calls per state, not one call per county.
///   - Reuse what already exists. Re-running finds the regions, the folder, and the
///     projects it made last time instead of failing on duplicate names.
///   - Throttle. The client's rate limiter is switched on for this workflow, because
///     a loop over hundreds of regions will otherwise earn a 429 and then a ban.
///
/// Input files, all in <c>data/</c>:
///
///   state_based.csv   fips, region_description, model_name
///   county_based.csv  fips, region_description, model_name
///   demo_events.csv   Name, Code, Type, Value
///
/// Rows sharing a model_name are combined into one region.
///
/// Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// </remarks>
public static class BulkFromCsvWorkflow
{
    /// <summary>The folder in IMPLAN Cloud these projects are filed under.</summary>
    private static readonly string FolderName = $"{Config.TitlePrefix} - Bulk From CSV";

    /// <summary>
    /// Region model requests are the most tightly limited family, so this workflow
    /// stays under the published five per minute. See the wiki home page.
    /// </summary>
    private const int RegionRequestsPerMinute = 5;

    private static readonly (string Label, Func<ApiClient, long, ResultFilters?, string> Fetch)[] Reports =
    [
        ("Summary Economic Indicators", ImpactResults.GetSummaryEconomicIndicators),
        ("Detailed Economic Indicators", ImpactResults.GetDetailedEconomicIndicators),
        ("Summary Taxes", ImpactResults.GetSummaryTaxes),
        ("Detailed Taxes", ImpactResults.GetDetailedTaxes),
    ];

    public static void Run()
    {
        var client = Auth.CreateClient();

        // Bulk work needs the throttle. Without it, a few hundred region calls earn
        // a 429 and then a temporary ban.
        client.RateLimiter = new RateLimiter(RegionRequestsPerMinute);

        // Step 1. Resolve identifiers and read the input files.
        ConsoleLog.Heading("Step 1: resolve identifiers and read the input files");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        var stateRows = ReadCsv(Path.Combine(Config.DataDirectory, "state_based.csv"));
        var countyRows = ReadCsv(Path.Combine(Config.DataDirectory, "county_based.csv"));
        var eventRows = ReadCsv(Path.Combine(Config.DataDirectory, "demo_events.csv"));
        ConsoleLog.Info("  {0} state rows, {1} county rows, {2} event rows",
            stateRows.Count, countyRows.Count, eventRows.Count);

        // Step 2. Build the combined regions. The lookup is shared so the state list
        // is fetched once for both files.
        ConsoleLog.Heading("Step 2: build the combined regions");
        var lookup = new RegionLookup(client, ids);
        var models = BuildModels(client, ids, stateRows, lookup);
        models.AddRange(BuildModels(client, ids, countyRows, lookup));
        ConsoleLog.Info("  {0} regions ready", models.Count);

        // Step 3. A folder to keep the projects together.
        ConsoleLog.Heading("Step 3: find or create the folder");

        // GET /api/v1/impact/folder, then POST if needed  (wiki: Projects, folders)
        var folder = Projects.FindOrCreateFolder(client, FolderName);
        ConsoleLog.Info("  folder '{0}' id {1}", folder.Title, folder.Id);

        // Step 4. One project per region.
        ConsoleLog.Heading("Step 4: one Project per region");
        var dollarYear = Config.CurrentDollarYear;

        foreach (var model in models)
        {
            ConsoleLog.Info("  {0}", model.Description);

            // POST /api/v1/impact/project  (wiki: Create Project)
            var project = Projects.CreateProject(client, new Project
            {
                Title = Config.UniqueTitle(model.Description),
                AggregationSchemeId = ids.AggregationSchemeId,
                HouseholdSetId = ids.HouseholdSetId,
                FolderId = folder.FolderIdForProject,
            });

            var created = AddEventsFromCsv(client, project.Id!.Value, eventRows);

            // POST /api/v1/impact/project/{projectId}/group  (wiki: Create Group)
            Groups.CreateGroup(client, project.Id.Value, new Group
            {
                Title = Config.UniqueTitle(model.Description),
                HashId = model.HashId,
                DatasetId = ids.DatasetId,
                DollarYear = dollarYear,
                GroupEvents = created.Select(e => new GroupEvent { EventId = e.Id!.Value }).ToList(),
            });

            RunAndDownload(client, project, Truncate(model.Description, 40));
        }

        // Step 5. One project holding every region, so the whole set can be read as
        // a single analysis.
        ConsoleLog.Heading("Step 5: one Project holding every region");

        var combinedProject = Projects.CreateProject(client, new Project
        {
            Title = Config.UniqueTitle("All Models"),
            AggregationSchemeId = ids.AggregationSchemeId,
            HouseholdSetId = ids.HouseholdSetId,
            FolderId = folder.FolderIdForProject,
        });
        ConsoleLog.Info("  {0}", combinedProject.Describe());

        // The events are created once and shared by every group, exactly as in the
        // MultiEventToMultiGroup workflow.
        var allEvents = AddEventsFromCsv(client, combinedProject.Id!.Value, eventRows);
        var eventLinks = allEvents.Select(e => new GroupEvent { EventId = e.Id!.Value }).ToList();

        foreach (var model in models)
        {
            Groups.CreateGroup(client, combinedProject.Id.Value, new Group
            {
                Title = Config.UniqueTitle(model.Description),
                HashId = model.HashId,
                DatasetId = ids.DatasetId,
                DollarYear = dollarYear,
                GroupEvents = eventLinks,
            });
        }

        ConsoleLog.Info("  {0} groups added", models.Count);

        RunAndDownload(client, combinedProject, "all-models");

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Folder:  {0}", FolderName);
        ConsoleLog.Info("Regions: {0}", models.Count);
        ConsoleLog.Info("Reports: {0}", Path.Combine(Config.ReportsDirectory, FolderName));
        ConsoleLog.Info();
        ConsoleLog.Info("Delete the folder and its projects from IMPLAN Cloud when you are done.");
    }

    /// <summary>
    /// Reads one input file, keeping FIPS codes as text.
    /// </summary>
    /// <remarks>
    /// FIPS codes have leading zeros that matter: Alabama is <c>01000</c>, and
    /// reading that as a number turns it into 1000, which is not a place.
    ///
    /// This parser handles quoted fields, which the region files use because some
    /// descriptions contain a comma. It is not a general CSV library, and does not
    /// need to be for these files.
    /// </remarks>
    private static List<Dictionary<string, string>> ReadCsv(string path)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException(
                $"Missing input file {path}. The samples ship with these in data/.");
        }

        var lines = File.ReadAllLines(path);
        if (lines.Length < 2)
            return [];

        var headers = SplitCsvLine(lines[0]);
        var rows = new List<Dictionary<string, string>>();

        foreach (var line in lines.Skip(1))
        {
            if (string.IsNullOrWhiteSpace(line))
                continue;

            var values = SplitCsvLine(line);
            var row = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            for (var i = 0; i < headers.Count; i++)
                row[headers[i]] = i < values.Count ? values[i] : string.Empty;

            rows.Add(row);
        }

        return rows;
    }

    /// <summary>Splits one CSV line, honoring double quotes around a field.</summary>
    private static List<string> SplitCsvLine(string line)
    {
        var fields = new List<string>();
        var current = new System.Text.StringBuilder();
        var inQuotes = false;

        foreach (var character in line)
        {
            switch (character)
            {
                case '"':
                    inQuotes = !inQuotes;
                    break;
                case ',' when !inQuotes:
                    fields.Add(current.ToString().Trim());
                    current.Clear();
                    break;
                default:
                    current.Append(character);
                    break;
            }
        }

        fields.Add(current.ToString().Trim());
        return fields;
    }

    /// <summary>Turns the rows of one input file into built regions, one per model name.</summary>
    private static List<Region> BuildModels(
        ApiClient client,
        Models.Identifiers ids,
        List<Dictionary<string, string>> rows,
        RegionLookup lookup)
    {
        var built = new List<Region>();

        var byModel = rows
            .GroupBy(r => r["model_name"])
            .ToDictionary(g => g.Key, g => g.Select(r => r["fips"]).ToList());

        foreach (var (modelName, fipsCodes) in byModel)
        {
            // Naming the region for the scheme and dataset means the same input file
            // can be run against several data years without a name collision.
            var description =
                $"{Config.TitlePrefix} {modelName} {ids.AggregationSchemeId}-{ids.DatasetId}";

            var existing = Regions.FindExistingUserRegion(
                client, ids.AggregationSchemeId, ids.DatasetId, description);

            if (existing is { IsBuilt: true })
            {
                ConsoleLog.Info("  {0} already built, reusing it", modelName);
                built.Add(existing);
                continue;
            }

            var members = fipsCodes.Select(lookup.Find).ToList();

            if (members.Count == 1)
            {
                // One region needs no combining; use IMPLAN's own region directly.
                ConsoleLog.Info("  {0} is a single region ({1}), using it as is",
                    modelName, members[0].Description);
                built.Add(members[0]);
                continue;
            }

            ConsoleLog.Info("  {0}: combining {1} regions", modelName, members.Count);

            // POST /api/v1/region/build/combined/{aggregationSchemeId}
            // (wiki: Combine Regions)
            var combined = Regions.BuildCombinedRegion(client, ids.AggregationSchemeId,
                new CombineRegionRequest
                {
                    Description = description,
                    HashIds = members.Select(m => m.HashId).ToList(),
                });

            // GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
            built.Add(Regions.WaitForRegionBuild(client, combined.HashId));
            ConsoleLog.Info("    built as {0}", combined.HashId);
        }

        return built;
    }

    /// <summary>
    /// Creates one event per row of the events file.
    /// </summary>
    /// <remarks>
    /// Two event types are covered: an Industry Output event, where the code names
    /// an industry, and a Commodity Output event, where it names a commodity. Add
    /// another branch here to support more.
    /// </remarks>
    private static List<ImpactEvent> AddEventsFromCsv(
        ApiClient client,
        Guid projectId,
        List<Dictionary<string, string>> rows)
    {
        var created = new List<ImpactEvent>();

        foreach (var row in rows)
        {
            var title = Config.UniqueTitle(row["Name"]);
            var code = int.Parse(row["Code"]);
            var value = double.Parse(row["Value"]);
            var kind = row["Type"].Trim();

            ImpactEvent impactEvent = kind.ToLowerInvariant() switch
            {
                "industry output" => new IndustryOutputEvent
                {
                    Title = title, IndustryCode = code, Output = value,
                },
                "commodity output" => new CommodityOutputEvent
                {
                    Title = title, CommodityCode = code, Output = value,
                },
                _ => throw new ArgumentException(
                    $"Event type '{kind}' in demo_events.csv is not one this workflow "
                    + "builds. Add a branch for it in AddEventsFromCsv."),
            };

            // POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
            created.Add(Events.CreateEvent(client, projectId, impactEvent));
        }

        ConsoleLog.Info("    added {0} events", created.Count);
        return created;
    }

    /// <summary>Runs one project, waits for it, and saves its reports.</summary>
    private static long? RunAndDownload(ApiClient client, Project project, string label)
    {
        // POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)
        var runId = Impacts.RunImpact(client, project.Id!.Value);
        ConsoleLog.Info("    run {0} started", runId);

        try
        {
            // GET /api/v1/impact/status/{runId}, polled  (wiki: Get Impact Status)
            Impacts.WaitForImpact(client, runId);
        }
        catch (Exception error) when (error is InvalidOperationException or TimeoutException)
        {
            // One failed run should not stop a batch of fifty. Report it and carry on.
            ConsoleLog.Info("    run {0} did not complete: {1}", runId, error.Message);
            return null;
        }

        var destination = Path.Combine(Config.ReportsDirectory, FolderName, $"{label}-{runId}");
        var filters = new ResultFilters { Year = Config.CurrentDollarYear };

        foreach (var (reportLabel, fetch) in Reports)
        {
            var csv = fetch(client, runId, filters);
            ImpactResults.SaveCsv(csv, Path.Combine(destination, $"{reportLabel}.csv"));
        }

        return runId;
    }

    private static string Truncate(string text, int length) =>
        text.Length <= length ? text : text[..length];

    /// <summary>
    /// Finds regions by FIPS code, with as few API calls as possible.
    /// </summary>
    /// <remarks>
    /// All the states are fetched once. Counties are fetched per state, and only for
    /// the states actually referenced, then kept. A file naming forty counties
    /// across three states costs four calls, not forty.
    /// </remarks>
    private sealed class RegionLookup
    {
        private readonly Dictionary<string, Region> _states = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, Dictionary<string, Region>> _countiesByState = new();
        private readonly ApiClient _client;
        private readonly Models.Identifiers _ids;

        public RegionLookup(ApiClient client, Models.Identifiers ids)
        {
            _client = client;
            _ids = ids;
        }

        /// <summary>
        /// Returns the region for a FIPS code, state or county.
        /// </summary>
        /// <remarks>A state code is two digits, or five ending in three zeros.</remarks>
        public Region Find(string fips)
        {
            fips = fips.Trim();
            var isState = fips.Length == 2 || (fips.Length == 5 && fips.EndsWith("000", StringComparison.Ordinal));
            var stateFips = fips[..2];

            if (isState)
            {
                LoadStates();
                return _states.TryGetValue(stateFips, out var state)
                    ? state
                    : throw new KeyNotFoundException($"No state with FIPS code {fips}.");
            }

            var counties = LoadCounties(stateFips);
            return counties.TryGetValue(fips, out var county)
                ? county
                : throw new KeyNotFoundException(
                    $"No county with FIPS code {fips} in state {stateFips}. Check the code "
                    + "against the current data year.");
        }

        private void LoadStates()
        {
            if (_states.Count > 0)
                return;

            // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
            // (wiki: Regional Children)
            var found = Regions.GetRegionChildren(
                _client, _ids.AggregationSchemeId, _ids.DatasetId, regionType: RegionType.State);

            foreach (var region in found.Where(r => !string.IsNullOrWhiteSpace(r.FipsCode)))
                _states[region.FipsCode!] = region;

            ConsoleLog.Info("  cached {0} states", _states.Count);
        }

        private Dictionary<string, Region> LoadCounties(string stateFips)
        {
            if (_countiesByState.TryGetValue(stateFips, out var cached))
                return cached;

            LoadStates();
            if (!_states.TryGetValue(stateFips, out var state))
                throw new KeyNotFoundException($"No state with FIPS code {stateFips}.");

            // GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children
            // (wiki: Regional Children)
            var found = Regions.GetRegionChildren(
                _client, _ids.AggregationSchemeId, _ids.DatasetId, state.HashId, RegionType.County);

            var counties = new Dictionary<string, Region>(StringComparer.OrdinalIgnoreCase);
            foreach (var region in found.Where(r => !string.IsNullOrWhiteSpace(r.FipsCode)))
                counties[region.FipsCode!] = region;

            _countiesByState[stateFips] = counties;
            ConsoleLog.Info("  cached {0} counties in {1}", counties.Count, state.Description);
            return counties;
        }
    }
}
