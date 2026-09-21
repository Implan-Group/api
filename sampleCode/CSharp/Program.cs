using Implan.ApiSamples.Endpoints;
using Implan.ApiSamples.Workflows;

namespace Implan.ApiSamples;

/// <summary>
/// The entry point: picks one workflow and runs it.
/// </summary>
/// <remarks>
/// Run one workflow at a time:
///
///     dotnet run -- authentication
///     dotnet run -- identifiers
///     dotnet run -- create-project
///     dotnet run -- run-impact-analysis --project-id &lt;guid&gt;
///
/// <c>dotnet run -- --list</c> prints every workflow with a one-line description.
///
/// Each workflow is a file in <c>Workflows/</c>, written to be read top to bottom.
/// Start with <c>authentication</c>, then <c>identifiers</c>, then follow the
/// numbered order.
///
/// Before the first run, copy <c>.env.example</c> to <c>.env</c> and put your IMPLAN
/// username and password in it. See README.md.
/// </remarks>
public static class Program
{
    /// <summary>
    /// Every workflow, in the order of the set.
    /// </summary>
    /// <remarks>
    /// The key is what you type on the command line; the value is what <c>--list</c>
    /// prints. Keeping the names identical to the Python and R samples means a
    /// workflow can be compared across languages by name.
    /// </remarks>
    private static readonly (string Name, string Description)[] Workflows =
    [
        ("authentication", "1  Get a bearer token, cache it, and verify it"),
        ("identifiers", "2  Resolve the current scheme, dataset, and industry codes"),
        ("regions", "3  Walk the region hierarchy and find regions by name"),
        ("combine-regions", "4  Combine two counties and wait for the model to build"),
        ("create-project", "5  Create a project with two events and one group"),
        ("multi-event-to-multi-group", "6  The same events across three states"),
        ("run-impact-analysis", "7  Run a project and download the five standard reports"),
        ("bulk-from-csv", "8  Build regions, projects, and runs from CSV input files"),
        ("regional-exports", "9  Download a regional data export for many regions"),
        ("import-events", "10 Fill a project from an IMPLAN Event Template workbook"),
        ("mrio-project", "11 Multi-regional analysis, with spillover between regions"),
        ("advanced-events", "12 Contribution and spending-pattern events, with tags"),
    ];

    /// <summary>
    /// Returns an exit code, so a scheduler or a CI job can tell what went wrong.
    /// </summary>
    /// <remarks>
    /// 0 success, 2 authentication, 3 the API refused the request, 4 a problem in
    /// the input or the account, 130 interrupted.
    /// </remarks>
    public static int Main(string[] args)
    {
        var options = CommandLineOptions.Parse(args);

        if (options.ShowList || options.Workflow is null)
        {
            PrintWorkflows();
            return 0;
        }

        if (!Workflows.Any(w => w.Name == options.Workflow))
        {
            ConsoleLog.Info("Unknown workflow '{0}'.", options.Workflow);
            ConsoleLog.Info();
            PrintWorkflows();
            return 4;
        }

        ConsoleLog.Info("IMPLAN Impact API sample: {0}", options.Workflow);
        ConsoleLog.Info("API: {0}", Config.BaseUrl);
        ConsoleLog.Debug($"Starting workflow {options.Workflow} against {Config.BaseUrl}");

        try
        {
            Dispatch(options);
        }
        catch (AuthenticationException error)
        {
            // Credentials or subscription. The message says which.
            ConsoleLog.Info();
            ConsoleLog.Info("Authentication failed.");
            ConsoleLog.Info(error.Message);
            return 2;
        }
        catch (ImplanApiException error)
        {
            // The API refused the request and said why. Quote the traceId to support.
            ConsoleLog.Info();
            ConsoleLog.Info("The API returned an error.");
            ConsoleLog.Info(error.Message);
            ConsoleLog.Info();
            ConsoleLog.Info("Full request and response detail: {0}", ConsoleLog.LogFilePath);
            return 3;
        }
        catch (Exception error) when (error is FileNotFoundException
                                          or KeyNotFoundException
                                          or ArgumentException
                                          or InvalidOperationException
                                          or TimeoutException)
        {
            // Everything the workflows raise deliberately: a missing input file, a
            // region or industry that is not in this dataset, a run that failed.
            ConsoleLog.Info();
            ConsoleLog.Info(error.Message);
            return 4;
        }
        catch (OperationCanceledException)
        {
            ConsoleLog.Info();
            ConsoleLog.Info("Stopped. Anything already created is still in your IMPLAN account.");
            return 130;
        }

        return 0;
    }

    /// <summary>Runs the chosen workflow, passing it whatever options apply to it.</summary>
    private static void Dispatch(CommandLineOptions options)
    {
        switch (options.Workflow)
        {
            case "authentication":
                AuthenticationWorkflow.Run();
                break;

            case "identifiers":
                IdentifiersWorkflow.Run();
                break;

            case "regions":
                RegionsWorkflow.Run();
                break;

            case "combine-regions":
                CombineRegionsWorkflow.Run();
                break;

            case "create-project":
                CreateProjectWorkflow.Run(options.MapCode);
                break;

            case "multi-event-to-multi-group":
                MultiEventToMultiGroupWorkflow.Run(options.ProjectId);
                break;

            case "run-impact-analysis":
                RunImpactAnalysisWorkflow.Run(options.ProjectId);
                break;

            case "bulk-from-csv":
                BulkFromCsvWorkflow.Run();
                break;

            case "regional-exports":
                RegionalExportsWorkflow.Run(
                    regionType: options.RegionType,
                    exportName: options.ExportName,
                    limit: options.Limit);
                break;

            case "import-events":
                ImportEventsWorkflow.Run(options.Workbook);
                break;

            case "mrio-project":
                MrioProjectWorkflow.Run();
                break;

            case "advanced-events":
                AdvancedEventsWorkflow.Run();
                break;

            default:
                // Main checks the name against the list first, so this cannot happen.
                throw new ArgumentException($"Unknown workflow '{options.Workflow}'.");
        }
    }

    private static void PrintWorkflows()
    {
        ConsoleLog.Info("IMPLAN Impact API sample workflows");
        ConsoleLog.Info();
        foreach (var (name, description) in Workflows)
            ConsoleLog.Info($"  {name,-28} {description}");

        ConsoleLog.Info();
        ConsoleLog.Info("Run one with:  dotnet run -- <name>");
        ConsoleLog.Info();
        ConsoleLog.Info("Options:");
        ConsoleLog.Info("  --project-id <guid>   an existing project, for the workflows that take one");
        ConsoleLog.Info("  --map-code <code>     US, CAN, or INTL (create-project)");
        ConsoleLog.Info("  --region-type <type>  Country, State, Msa, County, CongressionalDistrict,");
        ConsoleLog.Info("                        or Zipcode (regional-exports)");
        ConsoleLog.Info("  --export-name <name>  which regional data export to download");
        ConsoleLog.Info("  --limit <n>           how many regions to process, or 0 for all");
        ConsoleLog.Info("  --workbook <path>     a filled Event Template workbook (import-events)");
        ConsoleLog.Info();
        ConsoleLog.Info("Details for every workflow:  README.md and ../../CLAUDE.md");
    }
}

/// <summary>
/// The command line, parsed.
/// </summary>
/// <remarks>
/// Hand-written rather than taken from a package, because the samples keep their
/// dependencies to one and because a reader should not have to learn an argument
/// library to follow them. The shape matches the Python and R samples:
/// one workflow name, then optional <c>--name value</c> pairs.
/// </remarks>
internal sealed class CommandLineOptions
{
    /// <summary>Which workflow to run. Null means none was named.</summary>
    public string? Workflow { get; private set; }

    /// <summary>True for <c>--list</c>, which prints the workflows and exits.</summary>
    public bool ShowList { get; private set; }

    /// <summary>An existing project, for the workflows that can start from one.</summary>
    public Guid? ProjectId { get; private set; }

    /// <summary>Which country's data to use. Only CreateProject reads it.</summary>
    public MapCode MapCode { get; private set; } = MapCode.US;

    /// <summary>Which regions to export. Only RegionalExports reads it.</summary>
    public RegionType RegionType { get; private set; } = RegionType.Msa;

    /// <summary>Which regional data export to download.</summary>
    public string ExportName { get; private set; } = RegionalDataExports.RegionOverviewIndustries;

    /// <summary>How many regions to process. Null means all of them.</summary>
    public int? Limit { get; private set; } = 10;

    /// <summary>Path to a filled Event Template workbook.</summary>
    public string? Workbook { get; private set; }

    public static CommandLineOptions Parse(string[] args)
    {
        var options = new CommandLineOptions();

        for (var index = 0; index < args.Length; index++)
        {
            var argument = args[index];

            switch (argument)
            {
                case "--list":
                case "-l":
                case "--help":
                case "-h":
                    options.ShowList = true;
                    break;

                case "--project-id":
                    options.ProjectId = Guid.Parse(NextValue(args, ref index, argument));
                    break;

                case "--map-code":
                    options.MapCode = Enum.Parse<MapCode>(NextValue(args, ref index, argument), ignoreCase: true);
                    break;

                case "--region-type":
                    options.RegionType = Enum.Parse<RegionType>(NextValue(args, ref index, argument), ignoreCase: true);
                    break;

                case "--export-name":
                    options.ExportName = NextValue(args, ref index, argument);
                    break;

                case "--limit":
                    // 0 means no cap, which is how the Python sample spells it too.
                    var limit = int.Parse(NextValue(args, ref index, argument));
                    options.Limit = limit > 0 ? limit : null;
                    break;

                case "--workbook":
                    options.Workbook = NextValue(args, ref index, argument);
                    break;

                default:
                    if (argument.StartsWith('-'))
                        throw new ArgumentException($"Unknown option '{argument}'. Run with --list to see the options.");

                    options.Workflow ??= argument;
                    break;
            }
        }

        return options;
    }

    /// <summary>Reads the value that follows an option, and advances past it.</summary>
    private static string NextValue(string[] args, ref int index, string option)
    {
        if (index + 1 >= args.Length)
            throw new ArgumentException($"{option} needs a value after it.");

        index++;
        return args[index];
    }
}
