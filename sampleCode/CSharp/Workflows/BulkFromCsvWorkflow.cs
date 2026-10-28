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
///   - Reuse what already exists. Re-running gets back the combined regions it
///     built last time, because the API returns an existing region when both its
///     name and its member regions match, and files the new projects in the same
///     folder.
///   - Throttle. The client's rate limiter is switched on for this workflow, because
///     a burst of region builds will otherwise earn a 429 and then a ban. The
///     published limit counts builds, but the throttle applies to every request,
///     which is slower than the limit requires and keeps the script simple.
///
/// Input files, all in <c>data/</c>:
///
///   state_based.csv   fips, region_description, model_name
///   county_based.csv  fips, region_description, model_name
///   demo_events.csv   Name, Code, Type, Value
///
/// Rows sharing a model_name are combined into one region. Every row is checked
/// before anything is created in your account, so a mistake in the files stops
/// the run with the file and line to fix, not halfway through.
///
/// Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// </remarks>
public static class BulkFromCsvWorkflow
{
    /// <summary>The folder in IMPLAN Cloud these projects are filed under.</summary>
    private static readonly string FolderName = $"{Config.TitlePrefix} - Bulk From CSV";

    /// <summary>
    /// The published Region Models limit, five a minute. It counts model builds, not
    /// reads, but this workflow holds every request to that rate: slower than needed,
    /// and safely inside the limit. See the wiki home page.
    /// </summary>
    private const int RegionRequestsPerMinute = 5;

    /// <summary>The columns each input file must have.</summary>
    private static readonly string[] RegionColumns = ["fips", "region_description", "model_name"];

    private static readonly string[] EventColumns = ["Name", "Code", "Type", "Value"];

    /// <summary>The event types the events file can use, matched without regard to case.</summary>
    private static readonly string[] EventTypes = ["industry output", "commodity output"];

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

        // Bulk work needs the throttle. Without it, a burst of region builds earns a
        // 429 and then a temporary ban.
        client.RateLimiter = new RateLimiter(RegionRequestsPerMinute);

        // Step 1. Resolve identifiers and read the input files.
        ConsoleLog.Heading("Step 1: resolve identifiers and read the input files");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);

        var stateRows = ReadCsv(Path.Combine(Config.DataDirectory, "state_based.csv"), RegionColumns);
        var countyRows = ReadCsv(Path.Combine(Config.DataDirectory, "county_based.csv"), RegionColumns);
        var eventRows = ReadCsv(Path.Combine(Config.DataDirectory, "demo_events.csv"), EventColumns);
        ConsoleLog.Info("  {0} state rows, {1} county rows, {2} event rows",
            stateRows.Count, countyRows.Count, eventRows.Count);
        CheckInputs(stateRows, countyRows, eventRows);

        // Step 2. Build the combined regions. Every FIPS code is looked up before any
        // region is built, so a code that is not a place stops the run before
        // anything is created. The lookup is shared so the state list is fetched once.
        ConsoleLog.Heading("Step 2: build the combined regions");
        var lookup = new RegionLookup(client, ids);
        var membersByModel = MembersByModel(stateRows.Concat(countyRows), lookup);
        var models = BuildModels(client, ids, membersByModel);
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
    /// Reads one input file, keeping FIPS codes as text and skipping empty rows.
    /// </summary>
    /// <remarks>
    /// FIPS codes have leading zeros that matter: Alabama is <c>01000</c>, and
    /// reading that as a number turns it into 1000, which is not a place. Each row
    /// also records its line in the file under <c>line</c>, so a problem can be
    /// reported where it is.
    ///
    /// This parser handles quoted fields, which the region files use because some
    /// descriptions contain a comma. It is not a general CSV library, and does not
    /// need to be for these files.
    /// </remarks>
    internal static List<Dictionary<string, string>> ReadCsv(string path, string[] columns)
    {
        if (!File.Exists(path))
        {
            throw new FileNotFoundException(
                $"Missing input file {path}. The samples ship with these in data/.");
        }

        var lines = File.ReadAllLines(path);
        var name = Path.GetFileName(path);
        var headers = lines.Length == 0 ? [] : SplitCsvLine(lines[0]);

        var missing = columns.Where(c => !headers.Contains(c, StringComparer.OrdinalIgnoreCase)).ToList();
        if (missing.Count > 0)
        {
            throw new ArgumentException(
                $"{name} has no {string.Join(", ", missing)} column. It needs a "
                + $"comma-separated header row: {string.Join(",", columns)}");
        }

        var rows = new List<Dictionary<string, string>>();
        for (var index = 1; index < lines.Length; index++)
        {
            var values = SplitCsvLine(lines[index]);
            var lineNumber = index + 1;

            // A value holding an unquoted comma splits in two.
            if (values.Count > headers.Count)
            {
                throw new ArgumentException(
                    $"{name} line {lineNumber} has more values than its header. Put double "
                    + "quotes around any value that contains a comma, such as \"Douglas County, OR\".");
            }

            // Clearing cells in Excel can leave rows of bare commas behind.
            if (values.All(string.IsNullOrWhiteSpace))
                continue;

            var row = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            for (var i = 0; i < headers.Count; i++)
            {
                row[headers[i]] = i < values.Count ? values[i] : string.Empty;
            }

            row["line"] = lineNumber.ToString(System.Globalization.CultureInfo.InvariantCulture);
            rows.Add(row);
        }

        return rows;
    }

    /// <summary>
    /// Checks every row before anything is created, and reports every problem at once.
    /// </summary>
    /// <remarks>
    /// FIPS codes come back padded and amounts come back as plain numbers, so the rest
    /// of the workflow can read them directly.
    /// </remarks>
    internal static void CheckInputs(
        List<Dictionary<string, string>> stateRows,
        List<Dictionary<string, string>> countyRows,
        List<Dictionary<string, string>> eventRows)
    {
        var problems = new List<string>();

        var modelsByFile = new Dictionary<string, HashSet<string>>();
        foreach (var (fileName, rows) in new[] { ("state_based.csv", stateRows), ("county_based.csv", countyRows) })
        {
            modelsByFile[fileName] = [];
            foreach (var row in rows)
            {
                var where = $"{fileName} line {row["line"]}";
                var fips = PaddedFips(row["fips"]);
                if (fips is null)
                {
                    problems.Add($"{where}: '{row["fips"]}' is not a state or county FIPS code.");
                }
                else
                {
                    row["fips"] = fips;
                }

                problems.AddRange(NameProblems(where, "model_name", row["model_name"]));
                modelsByFile[fileName].Add(row["model_name"]);
            }
        }

        // Each file is grouped on its own, so a name in both would make two regions,
        // or two copies of one.
        foreach (var name in modelsByFile["state_based.csv"].Intersect(modelsByFile["county_based.csv"]).Order())
        {
            problems.Add(
                $"model_name '{name}' is in both state_based.csv and county_based.csv. "
                + "Give the counties a model_name of their own.");
        }

        if (stateRows.Count == 0 && countyRows.Count == 0)
        {
            problems.Add("state_based.csv and county_based.csv are both empty, so there is no region.");
        }

        if (eventRows.Count == 0)
        {
            problems.Add("demo_events.csv is empty, so there is no event to analyze.");
        }

        var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var row in eventRows)
        {
            var where = $"demo_events.csv line {row["line"]}";
            problems.AddRange(NameProblems(where, "Name", row["Name"]));
            if (!names.Add(row["Name"]))
            {
                problems.Add($"{where}: the Name '{row["Name"]}' is already used. Event titles must be unique.");
            }

            if (!EventTypes.Contains(row["Type"].ToLowerInvariant()))
            {
                problems.Add($"{where}: Type '{row["Type"]}' is not Industry Output or Commodity Output.");
            }

            if (row["Code"].Length == 0 || !row["Code"].All(char.IsAsciiDigit))
            {
                problems.Add($"{where}: Code '{row["Code"]}' is not a whole number.");
            }

            // Excel writes a Currency cell as "$1,000,000", so the symbol and the
            // separators are dropped before reading the number.
            var amount = row["Value"].Replace("$", "").Replace(",", "").Trim();
            if (double.TryParse(amount, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out _))
            {
                row["Value"] = amount;
            }
            else
            {
                problems.Add($"{where}: Value '{row["Value"]}' is not an amount in dollars.");
            }
        }

        if (problems.Count > 0)
        {
            throw new ArgumentException(
                "Fix these in the input files, then run again. Nothing was created.\n  "
                + string.Join("\n  ", problems));
        }
    }

    /// <summary>Returns a FIPS code at full length, or null if it is not one.</summary>
    /// <remarks>
    /// Excel drops leading zeros, so Alabama's <c>01000</c> can arrive as
    /// <c>1000</c>. A state code is two digits and a county code five, so a one- or
    /// four-digit code is unambiguous and is padded back.
    /// </remarks>
    internal static string? PaddedFips(string code)
    {
        if (code.Length is not (1 or 2 or 4 or 5) || !code.All(char.IsAsciiDigit))
            return null;

        return code.Length <= 2 ? code.PadLeft(2, '0') : code.PadLeft(5, '0');
    }

    /// <summary>What is wrong with a name that becomes part of a title, if anything.</summary>
    private static IEnumerable<string> NameProblems(string where, string column, string name)
    {
        if (name.Length == 0)
        {
            yield return $"{where}: {column} is empty.";
            yield break;
        }

        var rejected = name.Where(c => Config.DisallowedTitleCharacters.Contains(c)).Distinct().Order().ToList();
        if (rejected.Count > 0)
        {
            yield return $"{where}: {column} '{name}' contains {string.Join(" ", rejected)}, "
                         + "which IMPLAN does not allow in a title.";
        }
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

    /// <summary>Looks up every row's region, grouped by model name, in file order.</summary>
    private static Dictionary<string, List<Region>> MembersByModel(
        IEnumerable<Dictionary<string, string>> rows,
        RegionLookup lookup)
    {
        return rows
            .GroupBy(r => r["model_name"])
            .ToDictionary(g => g.Key, g => g.Select(r => lookup.Find(r["fips"])).ToList());
    }

    /// <summary>Turns each model's regions into one built region.</summary>
    private static List<Region> BuildModels(
        ApiClient client,
        Models.Identifiers ids,
        Dictionary<string, List<Region>> membersByModel)
    {
        var built = new List<Region>();

        foreach (var (modelName, members) in membersByModel)
        {
            // Naming the region for the scheme and dataset means the same input file
            // can be run against several data years without a name collision.
            var description =
                $"{Config.TitlePrefix} {modelName} {ids.AggregationSchemeId}-{ids.DatasetId}";

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
            // There is no need to look for an existing region first: the API does
            // it. A name you already have, sent with the same regions in any order,
            // returns that region instead of building it again, so a re-run reuses
            // last run's regions. Sent with different regions, it is refused with a
            // 422 saying the name is taken, so give a changed set of regions a new
            // model_name.
            var combined = Regions.BuildCombinedRegion(client, ids.AggregationSchemeId,
                new CombineRegionRequest
                {
                    Description = description,
                    HashIds = members.Select(m => m.HashId).ToList(),
                });

            // GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
            built.Add(Regions.WaitForRegionBuild(client, combined.HashId));
            ConsoleLog.Info("    ready as {0}", combined.HashId);
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
            var value = double.Parse(row["Value"], System.Globalization.CultureInfo.InvariantCulture);
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
