using System.Diagnostics;
using System.Net;
using RestSharp.Serializers.Json;

namespace Implan.ApiSamples.Services;

/// <summary>
/// The body the API returns with any error, per RFC 9457.
/// </summary>
/// <remarks>
/// <see cref="TraceId"/> is the one to quote when reporting a problem to IMPLAN
/// support: it identifies the exact request in their logs.
/// </remarks>
public sealed record ProblemDetails
{
    public int Status { get; init; }
    public string Title { get; init; } = "Request failed";
    public string Detail { get; init; } = string.Empty;
    public string? TraceId { get; init; }
    public string? Type { get; init; }
    public string? Instance { get; init; }

    /// <summary>Reads problem details out of a response, whatever shape it arrived in.</summary>
    public static ProblemDetails FromResponse(RestResponse response)
    {
        var fallbackTitle = response.StatusDescription ?? "Request failed";

        if (!string.IsNullOrWhiteSpace(response.Content))
        {
            try
            {
                using var document = JsonDocument.Parse(response.Content);
                var root = document.RootElement;
                if (root.ValueKind == JsonValueKind.Object)
                {
                    return new ProblemDetails
                    {
                        Status = (int)response.StatusCode,
                        Title = ReadString(root, "title") ?? fallbackTitle,
                        Detail = ReadString(root, "detail") ?? string.Empty,
                        TraceId = ReadString(root, "traceId"),
                        Type = ReadString(root, "type"),
                        Instance = ReadString(root, "instance"),
                    };
                }
            }
            catch (JsonException)
            {
                // Not JSON: a gateway error page, or an empty body. Fall through and
                // use the raw text so the reader is not left with nothing.
            }
        }

        var text = (response.Content ?? string.Empty).Trim();
        return new ProblemDetails
        {
            Status = (int)response.StatusCode,
            Title = fallbackTitle,
            Detail = text.Length > 1000 ? text[..1000] : text,
        };
    }

    private static string? ReadString(JsonElement element, string name)
    {
        return element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;
    }

    /// <summary>One readable block, for a console message or a support ticket.</summary>
    public string Describe()
    {
        var lines = new List<string> { $"{Status} {Title}" };
        if (!string.IsNullOrWhiteSpace(Detail))
            lines.Add($"  {Detail}");
        if (!string.IsNullOrWhiteSpace(TraceId))
            lines.Add($"  traceId: {TraceId}");
        return string.Join(Environment.NewLine, lines);
    }
}

/// <summary>
/// Thrown when the API answers with an error.
/// </summary>
/// <remarks>
/// Catch this to handle an expected failure, for example a 409 when a title is
/// already taken. <c>Problem.Status</c> is the status code and
/// <c>Problem.Detail</c> is the API's explanation.
/// </remarks>
public sealed class ImplanApiException : Exception
{
    public ImplanApiException(Method method, string url, ProblemDetails problem)
        : base($"{method.ToString().ToUpperInvariant()} {url}{Environment.NewLine}{problem.Describe()}")
    {
        Problem = problem;
        Url = url;
    }

    public ProblemDetails Problem { get; }
    public string Url { get; }
    public int StatusCode => Problem.Status;
}

/// <summary>
/// A list of query parameters, allowing the same name more than once.
/// </summary>
/// <remarks>
/// A dictionary would be the obvious choice and is the wrong one here. Several of
/// this API's filters are repeated parameters rather than one comma-separated
/// value: filtering on two regions means <c>regions=Oregon&amp;regions=Wisconsin</c>.
/// A dictionary keyed by name would keep only the last, and would do it silently.
/// </remarks>
public sealed class Query : List<KeyValuePair<string, string>>
{
    /// <summary>Adds a parameter, ignoring it when the value is null.</summary>
    public Query With(string name, string? value)
    {
        if (value is not null)
            Add(new KeyValuePair<string, string>(name, value));
        return this;
    }

    /// <summary>Adds a parameter whose value is a number.</summary>
    public Query With(string name, int? value)
    {
        return With(name, value?.ToString());
    }

    /// <summary>Adds the same parameter once for each value.</summary>
    public Query WithEach(string name, IEnumerable<string> values)
    {
        foreach (var value in values)
            Add(new KeyValuePair<string, string>(name, value));
        return this;
    }
}

/// <summary>
/// Keeps a family of requests under a published per-minute limit.
/// </summary>
/// <remarks>
/// The API publishes limits per group of endpoints, and exceeding one earns a
/// <c>429 Too Many Requests</c> and, if you keep going, a temporary ban. The bulk
/// workflows switch this on so a loop over thousands of regions stays polite; the
/// short workflows do not need it.
///
/// Limits are on the wiki home page: https://github.com/Implan-Group/api/wiki
/// </remarks>
public sealed class RateLimiter
{
    private readonly Queue<DateTime> _timestamps = new();
    private readonly int _requestsPerMinute;

    /// <param name="requestsPerMinute">The published limit for this family of endpoints.</param>
    public RateLimiter(int requestsPerMinute)
    {
        _requestsPerMinute = requestsPerMinute;
    }

    /// <summary>Blocks until another request would be within the limit.</summary>
    public void Wait()
    {
        var now = DateTime.UtcNow;
        while (_timestamps.Count > 0 && (now - _timestamps.Peek()).TotalSeconds >= 60)
            _timestamps.Dequeue();

        if (_timestamps.Count >= _requestsPerMinute)
        {
            var wait = TimeSpan.FromSeconds(60) - (now - _timestamps.Peek()) + TimeSpan.FromMilliseconds(100);
            if (wait > TimeSpan.Zero)
            {
                ConsoleLog.Debug(
                    $"Rate limit: waiting {wait.TotalSeconds:F1}s to stay under {_requestsPerMinute}/min");
                Thread.Sleep(wait);
            }
        }

        _timestamps.Enqueue(DateTime.UtcNow);
    }
}

/// <summary>
/// Sends authenticated requests to the Impact API.
/// </summary>
/// <remarks>
/// One class responsible for everything that is the same on every call: attaching
/// the bearer token, logging the exchange, turning an error response into an
/// exception you can read, backing off when the API asks you to, and refreshing an
/// expired token once before giving up.
///
/// Errors deserve a word. Every failure from this API comes back as a
/// problem-details document with a title, a detail, and a traceId. Those three are
/// the difference between "something went wrong" and knowing what to fix, so this
/// client throws them rather than letting a failed call return null and break
/// somewhere else with a confusing message.
///
/// Wiki: Requests - https://github.com/Implan-Group/api/wiki/Requests
/// Wiki: Responses - https://github.com/Implan-Group/api/wiki/Responses
/// </remarks>
public sealed class ApiClient
{
    /// <summary>
    /// Statuses worth trying again. 429 means the rate limit was hit; the 5xx family
    /// here means the service was briefly unavailable rather than that the request
    /// was wrong.
    /// </summary>
    private static readonly HashSet<HttpStatusCode> RetryStatuses =
    [
        HttpStatusCode.TooManyRequests,
        HttpStatusCode.BadGateway,
        HttpStatusCode.ServiceUnavailable,
        HttpStatusCode.GatewayTimeout,
    ];

    private const int MaxAttempts = 4;

    private readonly RestClient _client;
    private readonly Func<string> _tokenProvider;
    private readonly Func<string>? _tokenRefresher;
    private readonly Random _jitter = new();

    public ApiClient(Func<string> tokenProvider, Func<string>? tokenRefresher = null)
    {
        _tokenProvider = tokenProvider;
        _tokenRefresher = tokenRefresher;

        var options = new RestClientOptions(Config.BaseUrl)
        {
            Timeout = Config.RequestTimeout,
            AutomaticDecompression = DecompressionMethods.All,
            // Errors are turned into ImplanApiException below, which carries the
            // problem details. Letting RestSharp throw first would lose them.
            ThrowOnAnyError = false,
        };

        _client = new RestClient(options, configureSerialization: s => s.UseSystemTextJson(Json.Options));
    }

    /// <summary>Set by the bulk workflows; null means no client-side throttling.</summary>
    public RateLimiter? RateLimiter { get; set; }

    /// <summary>GETs a JSON document and deserializes it.</summary>
    public T GetJson<T>(string path, Query? query = null, object? body = null)
    {
        var response = Send(Method.Get, path, query, body);
        return Deserialize<T>(response);
    }

    /// <summary>
    /// GETs a text document, which for this API means a CSV report.
    /// </summary>
    /// <remarks>
    /// Write the result to a file with a <c>.csv</c> extension and it opens in Excel
    /// or Sheets.
    /// </remarks>
    public string GetText(string path, Query? query = null, object? body = null)
    {
        return Send(Method.Get, path, query, body).Content ?? string.Empty;
    }

    /// <summary>POSTs a JSON body and deserializes the response.</summary>
    public T PostJson<T>(string path, object? body = null)
    {
        return Deserialize<T>(Send(Method.Post, path, query: null, body));
    }

    /// <summary>POSTs a JSON body and returns the raw response text.</summary>
    /// <remarks>
    /// A few endpoints answer with a bare number or a sentence rather than an
    /// object: <c>RunImpact</c> returns a run id, and <c>CancelImpact</c> returns a
    /// confirmation.
    /// </remarks>
    public string PostText(string path, object? body = null)
    {
        return Send(Method.Post, path, query: null, body).Content ?? string.Empty;
    }

    /// <summary>POSTs a file as multipart form data, for the Event Template upload.</summary>
    public string PostFile(string path, string fieldName, string filePath)
    {
        var request = new RestRequest(path, Method.Post);
        request.AddFile(fieldName, filePath);
        return Execute(request).Content ?? string.Empty;
    }

    /// <summary>PUTs a JSON body and returns the raw response text.</summary>
    public string PutText(string path, object? body = null)
    {
        return Send(Method.Put, path, query: null, body).Content ?? string.Empty;
    }

    /// <summary>DELETEs a resource. The API returns no body worth reading.</summary>
    public void Delete(string path)
    {
        Send(Method.Delete, path);
    }

    private RestResponse Send(
        Method method,
        string path,
        Query? query = null,
        object? body = null)
    {
        var request = new RestRequest(path, method);

        if (query is not null)
        {
            foreach (var (name, value) in query)
            {
                // Added rather than set, so a filter with several values becomes a
                // repeated parameter, which is the shape this API expects for
                // `regions`, `eventTags`, and the rest.
                request.AddQueryParameter(name, value);
            }
        }

        if (body is not null)
        {
            // Allowed on a GET, which sounds wrong but is what a few of this API's
            // report endpoints require. See ImpactResults.GetEstimatedGrowthPercentage.
            request.AddJsonBody(body);
        }

        return Execute(request);
    }

    private RestResponse Execute(RestRequest request)
    {
        for (var attempt = 1; attempt <= MaxAttempts; attempt++)
        {
            RateLimiter?.Wait();

            // Added per attempt rather than once, so a token refreshed mid-run is
            // picked up by the retry.
            request.AddOrUpdateHeader("Authorization", _tokenProvider());

            var timer = Stopwatch.StartNew();
            var response = _client.Execute(request);
            timer.Stop();

            ConsoleLog.LogExchange(_client, request, response, timer.Elapsed);

            if (response.IsSuccessful)
                return response;

            var problem = ProblemDetails.FromResponse(response);

            // An expired token looks like a 401. Refresh once and try again; if the
            // second attempt also fails, the credentials or the subscription are the
            // problem, not the token.
            if (response.StatusCode == HttpStatusCode.Unauthorized && _tokenRefresher is not null && attempt == 1)
            {
                ConsoleLog.Debug("401 received; refreshing the bearer token and retrying");
                _tokenRefresher();
                continue;
            }

            if (RetryStatuses.Contains(response.StatusCode) && attempt < MaxAttempts)
            {
                var delay = RetryDelay(response, attempt);
                ConsoleLog.Info(
                    "  {0} from the API; waiting {1:F0}s and trying again (attempt {2} of {3})",
                    (int)response.StatusCode, delay.TotalSeconds, attempt + 1, MaxAttempts);
                Thread.Sleep(delay);
                continue;
            }

            throw new ImplanApiException(request.Method, _client.BuildUri(request).ToString(), problem);
        }

        throw new UnreachableException("The retry loop always returns or throws.");
    }

    /// <summary>
    /// How long to wait before trying again.
    /// </summary>
    /// <remarks>
    /// The API's <c>Retry-After</c> header wins when it is present. Otherwise back
    /// off exponentially with a little randomness, so a batch of parallel scripts
    /// does not retry in lockstep.
    /// </remarks>
    private TimeSpan RetryDelay(RestResponse response, int attempt)
    {
        var retryAfter = response.Headers?
            .FirstOrDefault(h => string.Equals(h.Name, "Retry-After", StringComparison.OrdinalIgnoreCase))?
            .Value?.ToString();

        if (double.TryParse(retryAfter, out var seconds))
            return TimeSpan.FromSeconds(seconds);

        return TimeSpan.FromSeconds(Math.Min(60, Math.Pow(2, attempt) + _jitter.NextDouble()));
    }

    private static T Deserialize<T>(RestResponse response)
    {
        if (string.IsNullOrWhiteSpace(response.Content))
        {
            throw new InvalidOperationException(
                $"The API returned an empty body where a {typeof(T).Name} was expected.");
        }

        return JsonSerializer.Deserialize<T>(response.Content, Json.Options)
               ?? throw new InvalidOperationException(
                   $"The API's response could not be read as a {typeof(T).Name}.");
    }
}
