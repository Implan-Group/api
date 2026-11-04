using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 1: Authentication.
/// </summary>
/// <remarks>
/// Goal: get a bearer token, cache it, and prove it works.
///
/// Every other workflow depends on this one. Run it first, and run it again
/// whenever you want to check that your credentials and subscription are in order
/// without creating anything in your account.
///
/// The point of the workflow is the caching. A token lasts 24 hours, and asking for
/// a new one on every run is unnecessary, unsupported, and can get an account
/// temporarily banned. So: read the cached token, verify it cheaply, and only
/// authenticate when there is nothing usable on disk.
///
/// Wiki: Authentication - https://github.com/Implan-Group/api/wiki/Authentication
/// </remarks>
public static class AuthenticationWorkflow
{
    public static void Run()
    {
        // Step 1. Check that credentials are available before touching the network,
        // so a missing .env fails with an explanation rather than a 401.
        ConsoleLog.Heading("Step 1: read credentials");
        var (username, _) = Config.RequireCredentials();
        ConsoleLog.Info("  signing in as {0}", username);
        ConsoleLog.Info("  credentials came from {0}", Path.Combine(Config.SampleRoot, ".env"));

        // Step 2. Get a token. This reuses the cached one when it still works and
        // only calls POST /api/auth when it does not, which is the pattern to copy.
        ConsoleLog.Heading("Step 2: get a bearer token");
        var hadCache = File.Exists(Config.TokenCachePath);
        Auth.GetBearerToken();
        ConsoleLog.Info(hadCache
            ? "  a cached token was already on disk and was checked before reuse"
            : "  no cached token, so one was requested and saved");
        ConsoleLog.Info("  token cache: {0}", Config.TokenCachePath);
        ConsoleLog.Info("  the token itself is never printed or logged");

        // Step 3. Make one real authenticated call. Region Types is the cheapest
        // endpoint in the API, which is why it is the one used to test a token.
        ConsoleLog.Heading("Step 3: confirm the token is accepted");
        var client = Auth.CreateClient();

        // GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
        var regionTypes = Regions.GetRegionTypes(client);
        ConsoleLog.Info("  the API answered with {0} region types:", regionTypes.Count);
        ConsoleLog.Info("    {0}", string.Join(", ", regionTypes));

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Authentication works. Every other workflow can now run.");
        ConsoleLog.Info("Run this workflow again and step 2 will reuse the cached token.");
        ConsoleLog.Info("Full request and response detail: {0}", ConsoleLog.LogFilePath);
    }
}
