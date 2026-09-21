using System.Net;
using RestSharp.Serializers.Json;

namespace Implan.ApiSamples.Services;

/// <summary>Thrown when a token cannot be obtained or the credentials are refused.</summary>
public sealed class AuthenticationException : Exception
{
    public AuthenticationException(string message)
        : base(message)
    {
    }
}

/// <summary>
/// Authentication and the token cache.
/// </summary>
/// <remarks>
/// The caching pattern every IMPLAN sample follows, in any language:
///
/// 1. If a cached token file exists, read it and verify it with one cheap call.
/// 2. If that works, use it. A token is valid for 24 hours.
/// 3. Only if there is no file, or the token in it has expired, post the
///    credentials and write the new token to the file.
///
/// The caching is not an optimization, it is a requirement. Authenticating on every
/// run is unnecessary, unsupported, and repeated requests in a short period can
/// earn a temporary ban on the account.
///
/// The token itself is never printed or logged. Treat it exactly as you would the
/// password that produced it.
///
/// Wiki: Authentication - https://github.com/Implan-Group/api/wiki/Authentication
/// Support: How to Use the IMPLAN API with R: Obtaining Your API Token
/// https://support.implan.com/hc/en-us/articles/48279952909467
/// </remarks>
public static class Auth
{
    /// <summary>
    /// A small, fast, always-available endpoint used only to answer "is this token
    /// still good?". It returns a handful of strings, so verifying costs almost
    /// nothing.
    /// </summary>
    private const string VerifyPath = "/api/v1/region/RegionTypes";

    private static string? _token;

    /// <summary>Returns the token saved by an earlier run, or null if there is not one.</summary>
    private static string? ReadCachedToken()
    {
        if (!File.Exists(Config.TokenCachePath))
            return null;

        var token = File.ReadAllText(Config.TokenCachePath).Trim();
        return string.IsNullOrWhiteSpace(token) ? null : token;
    }

    /// <summary>
    /// Saves a token for the next run.
    /// </summary>
    /// <remarks>
    /// The file is gitignored (<c>*.jwt</c>). It holds a live credential, so keep it
    /// out of source control, shared folders, and screenshots.
    /// </remarks>
    private static void WriteCachedToken(string token)
    {
        File.WriteAllText(Config.TokenCachePath, token);
    }

    /// <summary>Checks a cached token with one inexpensive authenticated request.</summary>
    private static bool IsTokenValid(string token)
    {
        try
        {
            var options = new RestClientOptions(Config.BaseUrl) { Timeout = Config.RequestTimeout };
            using var client = new RestClient(options);
            var request = new RestRequest(VerifyPath);
            request.AddHeader("Authorization", token);
            return client.Execute(request).StatusCode == HttpStatusCode.OK;
        }
        catch (Exception)
        {
            // Network trouble tells us nothing about the token. Treat it as invalid
            // so the caller takes the fresh-token path and gets a clearer error there.
            return false;
        }
    }

    /// <summary>
    /// Authenticates with username and password and returns a fresh bearer token.
    /// </summary>
    /// <remarks>
    /// POST /api/auth  (wiki: Authentication)
    ///
    /// The request body is a JSON object with lowercase <c>username</c> and
    /// <c>password</c>. The response body is the token, already carrying its
    /// <c>Bearer </c> prefix, so it goes into the <c>Authorization</c> header
    /// exactly as received.
    /// </remarks>
    public static string FetchNewToken()
    {
        var (username, password) = Config.RequireCredentials();

        var options = new RestClientOptions(Config.BaseUrl) { Timeout = Config.RequestTimeout };
        using var client = new RestClient(options, configureSerialization: s => s.UseSystemTextJson(Json.Options));

        var request = new RestRequest("/api/auth", Method.Post);
        request.AddJsonBody(new { username, password });

        var response = client.Execute(request);

        if (response.StatusCode == HttpStatusCode.OK)
        {
            var token = (response.Content ?? string.Empty).Trim();
            if (string.IsNullOrWhiteSpace(token))
                throw new AuthenticationException("The auth endpoint returned an empty token.");

            // The API already prefixes the token, but a proxy that trimmed it would
            // produce a confusing 401 later, so make sure of it here.
            if (!token.StartsWith("Bearer ", StringComparison.Ordinal))
                token = $"Bearer {token}";

            WriteCachedToken(token);
            ConsoleLog.Debug($"Authenticated and cached a new token at {Config.TokenCachePath}");
            return token;
        }

        var problem = ProblemDetails.FromResponse(response);

        if (response.StatusCode == HttpStatusCode.ServiceUnavailable)
        {
            // Two different causes, and the fix differs. See the support article
            // named in this class's remarks.
            throw new AuthenticationException(
                "The authentication service answered 503 Service Unavailable." + Environment.NewLine
                + "That is either a brief outage, in which case waiting a minute and" + Environment.NewLine
                + "running again usually works, or API access has not been enabled on" + Environment.NewLine
                + "your account, in which case your Customer Success Manager has to" + Environment.NewLine
                + "turn it on. Repeat 503s point to the second." + Environment.NewLine
                + problem.Describe());
        }

        if (response.StatusCode is HttpStatusCode.BadRequest
            or HttpStatusCode.Unauthorized
            or HttpStatusCode.Forbidden)
        {
            throw new AuthenticationException(
                "IMPLAN refused those credentials." + Environment.NewLine
                + "Check IMPLAN_USERNAME and IMPLAN_PASSWORD in your .env file; they are" + Environment.NewLine
                + "the same ones you use at app.implan.com, and your subscription must" + Environment.NewLine
                + "include API access." + Environment.NewLine
                + problem.Describe());
        }

        throw new AuthenticationException($"Could not authenticate.{Environment.NewLine}{problem.Describe()}");
    }

    /// <summary>Returns a usable bearer token, reusing the cached one while it works.</summary>
    public static string GetBearerToken()
    {
        var cached = ReadCachedToken();
        if (cached is not null)
        {
            if (IsTokenValid(cached))
            {
                ConsoleLog.Debug("Reusing the cached bearer token");
                return cached;
            }

            ConsoleLog.Debug("The cached token has expired; requesting a new one");
        }

        return FetchNewToken();
    }

    /// <summary>
    /// Builds the API client the workflows use.
    /// </summary>
    /// <remarks>
    /// The client asks for the token lazily and can refresh it once if a request
    /// comes back 401 mid-run, which matters for a bulk workflow that runs for
    /// longer than the token's lifetime.
    /// </remarks>
    public static ApiClient CreateClient()
    {
        return new ApiClient(
            tokenProvider: () => _token ??= GetBearerToken(),
            tokenRefresher: () => _token = FetchNewToken());
    }
}
