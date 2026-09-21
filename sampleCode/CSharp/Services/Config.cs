namespace Implan.ApiSamples.Services;

/// <summary>
/// Configuration shared by every workflow: where the API lives, where credentials
/// come from, where files are written, and the two conventions (a title prefix, and
/// a dollar year) that the workflows apply to everything they create.
/// </summary>
/// <remarks>
/// Credentials are read from a <c>.env</c> file next to the project. That file is
/// gitignored and must never be committed. Copy <c>.env.example</c> to <c>.env</c>
/// and fill in the two values.
///
/// Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started
/// </remarks>
public static class Config
{
    private static readonly Dictionary<string, string> EnvFileValues = new(StringComparer.OrdinalIgnoreCase);

    static Config()
    {
        SampleRoot = FindSampleRoot();
        LoadEnvFile(Path.Combine(SampleRoot, ".env"));
    }

    /// <summary>
    /// The folder holding the project file. Every other path is derived from it, so
    /// the samples behave the same whether they are started from the source folder
    /// or from <c>bin/</c>.
    /// </summary>
    public static string SampleRoot { get; }

    /// <summary>
    /// The host serving the API. Authentication is at <c>/api/auth</c>; everything
    /// else is under <c>/api/v1/</c>.
    /// </summary>
    public static string BaseUrl => Read("IMPLAN_API_URL") ?? "https://api.implan.com";

    /// <summary>Your IMPLAN sign-in, the same one you use at app.implan.com.</summary>
    public static string? Username => Read("IMPLAN_USERNAME");

    /// <summary>Your IMPLAN password.</summary>
    public static string? Password => Read("IMPLAN_PASSWORD");

    /// <summary>
    /// Where the bearer token is cached between runs. A token is good for 24 hours,
    /// and asking for a new one on every run risks a temporary ban, so the samples
    /// always reuse this file while the token in it still works.
    /// </summary>
    public static string TokenCachePath => Path.Combine(SampleRoot, "implan_auth.jwt");

    /// <summary>Request and response logs, one file per day.</summary>
    public static string LogDirectory => Path.Combine(SampleRoot, "logs");

    /// <summary>Exported CSV reports and other downloads.</summary>
    public static string ReportsDirectory => Path.Combine(SampleRoot, "reports");

    /// <summary>Input files that ship with the samples.</summary>
    public static string DataDirectory => Path.Combine(SampleRoot, "data");

    /// <summary>
    /// Everything these samples create in your IMPLAN account is named with this
    /// prefix, so you can find it later and delete it.
    /// </summary>
    public const string TitlePrefix = "ImpactApi Sample";

    public static readonly TimeSpan ImpactTimeout = TimeSpan.FromMinutes(15);
    public static readonly TimeSpan ImpactPollInterval = TimeSpan.FromSeconds(15);
    public static readonly TimeSpan RegionBuildTimeout = TimeSpan.FromMinutes(10);
    public static readonly TimeSpan RegionBuildPollInterval = TimeSpan.FromSeconds(15);

    /// <summary>
    /// How long to wait for one HTTP request. The gateway itself gives up at 30
    /// seconds, so anything longer than this is a network problem rather than a
    /// slow endpoint.
    /// </summary>
    public static readonly TimeSpan RequestTimeout = TimeSpan.FromSeconds(60);

    /// <summary>
    /// The dollar year the samples use, which is the current calendar year.
    /// </summary>
    /// <remarks>
    /// Dollar Year is the year results are expressed in; Data Year is the year of
    /// the underlying IMPLAN dataset. They are different and often differ. Every
    /// Group the samples create carries this explicitly, because the API has no
    /// default: a Group saved without a dollar year produces an impact run that
    /// never attaches.
    ///
    /// Support: Which Year Is It Anyway? Data Year, Model Year, and Dollar Year
    /// https://support.implan.com/hc/en-us/articles/360039290593
    /// </remarks>
    public static int CurrentDollarYear => DateTime.Now.Year;

    /// <summary>
    /// Builds a title that is unique per run and easy to find in IMPLAN Cloud.
    /// </summary>
    /// <remarks>
    /// Titles must be unique for your user, and the API rejects an ampersand and
    /// the characters <c>| ; % * ? ! = ' " ^ #</c>, so keep <paramref name="label"/>
    /// to plain words.
    /// </remarks>
    public static string UniqueTitle(string label)
    {
        return $"{TitlePrefix} - {label} - {DateTime.Now:yyyyMMdd-HHmmss}";
    }

    /// <summary>
    /// Returns the username and password, or explains exactly what is missing.
    /// </summary>
    /// <remarks>
    /// Every workflow calls this before its first request, so a missing
    /// <c>.env</c> fails immediately with a useful message rather than as a
    /// confusing 401 later.
    /// </remarks>
    public static (string Username, string Password) RequireCredentials()
    {
        if (string.IsNullOrWhiteSpace(Username) || string.IsNullOrWhiteSpace(Password))
        {
            throw new InvalidOperationException(
                "IMPLAN credentials are not set." + Environment.NewLine
                + $"Copy {Path.Combine(SampleRoot, ".env.example")} to "
                + $"{Path.Combine(SampleRoot, ".env")} and fill in IMPLAN_USERNAME and"
                + " IMPLAN_PASSWORD, or set them as environment variables.");
        }

        return (Username!, Password!);
    }

    /// <summary>
    /// Reads a setting, preferring a real environment variable over the .env file so
    /// that a shell or a CI system can override the file.
    /// </summary>
    private static string? Read(string name)
    {
        var fromEnvironment = Environment.GetEnvironmentVariable(name);
        if (!string.IsNullOrWhiteSpace(fromEnvironment))
            return fromEnvironment;

        return EnvFileValues.TryGetValue(name, out var value) && !string.IsNullOrWhiteSpace(value)
            ? value
            : null;
    }

    /// <summary>
    /// Walks up from the running assembly to the folder holding the project file.
    /// </summary>
    /// <remarks>
    /// A built executable lives in <c>bin/Debug/net10.0/</c>, several levels below
    /// the source. Finding the project file rather than assuming a depth means the
    /// samples locate their .env, data, logs, and reports the same way however they
    /// were started.
    /// </remarks>
    private static string FindSampleRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (directory.GetFiles("*.csproj").Length > 0)
                return directory.FullName;
            directory = directory.Parent;
        }

        // Not found, which happens for a published single-file build. The folder the
        // executable sits in is then the right answer anyway.
        return AppContext.BaseDirectory;
    }

    /// <summary>
    /// Reads a .env file into memory.
    /// </summary>
    /// <remarks>
    /// Deliberately small rather than a package: the format needed here is
    /// <c>KEY=value</c>, one per line, with <c>#</c> comments and optional quotes.
    /// </remarks>
    private static void LoadEnvFile(string path)
    {
        if (!File.Exists(path))
            return;

        foreach (var rawLine in File.ReadAllLines(path))
        {
            var line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#'))
                continue;

            var separator = line.IndexOf('=');
            if (separator <= 0)
                continue;

            var key = line[..separator].Trim();
            var value = line[(separator + 1)..].Trim().Trim('"', '\'');
            EnvFileValues[key] = value;
        }
    }
}
