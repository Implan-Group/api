using Implan.ApiSamples.Tests.Support;
using Xunit.Sdk;
using Xunit.v3;

// One log file for the whole test run, set before any test logs anything.
[assembly: AssemblyFixture(typeof(LogFileFixture))]

// The log file path is static state in ConsoleLog, so the tests run one at a time.
// There are few enough that it costs nothing noticeable.
[assembly: Parallelization(Mode = ParallelMode.None)]

namespace Implan.ApiSamples.Tests.Support;

/// <summary>
/// Points the samples' log at a temporary file for the test run, and deletes it
/// afterwards, so the tests can read what was logged without writing into
/// <c>logs/</c>.
/// </summary>
public sealed class LogFileFixture : IDisposable
{
    public LogFileFixture()
    {
        LogPath = Path.Combine(Path.GetTempPath(), $"implan-tests-{Guid.NewGuid():N}.txt");
        ConsoleLog.UseLogFile(LogPath);
    }

    public string LogPath { get; }

    /// <summary>Everything logged so far, or an empty string if nothing has been.</summary>
    public string ReadAll()
    {
        return File.Exists(LogPath) ? File.ReadAllText(LogPath) : string.Empty;
    }

    public void Dispose()
    {
        if (File.Exists(LogPath))
            File.Delete(LogPath);
    }
}
