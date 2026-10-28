namespace Implan.ApiSamples.Tests.Support;

/// <summary>One request as the stand-in network saw it.</summary>
public sealed record SentRequest(HttpMethod Method, Uri? Uri, string? ContentType, string? Body);

/// <summary>
/// Stands in for the network: answers each request with the next scripted outcome.
/// </summary>
/// <remarks>
/// <see cref="ApiClient"/> takes an optional <see cref="HttpMessageHandler"/>, which
/// RestSharp uses in place of the real one, so every test runs the client's own
/// retry, refresh, logging, and error handling. An outcome that throws is how a host
/// that never answered looks to RestSharp.
/// </remarks>
public sealed class ScriptedHandler : HttpMessageHandler
{
    private readonly Queue<Func<HttpResponseMessage>> _outcomes;

    public ScriptedHandler(IEnumerable<Func<HttpResponseMessage>> outcomes)
    {
        _outcomes = new Queue<Func<HttpResponseMessage>>(outcomes);
    }

    public List<SentRequest> Sent { get; } = [];

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var body = request.Content is null
            ? null
            : await request.Content.ReadAsStringAsync(cancellationToken);

        Sent.Add(new SentRequest(
            request.Method,
            request.RequestUri,
            request.Content?.Headers.ContentType?.MediaType,
            body));

        return _outcomes.Dequeue()();
    }

    protected override HttpResponseMessage Send(HttpRequestMessage request, CancellationToken cancellationToken)
    {
        return SendAsync(request, cancellationToken).GetAwaiter().GetResult();
    }
}

/// <summary>Scripted answers, and clients that receive them.</summary>
public static class Scripted
{
    /// <summary>A token-shaped value that must never show up in the log.</summary>
    public const string FakeToken = "Bearer not.a.real.token";

    /// <summary>An answer with this status and body.</summary>
    public static Func<HttpResponseMessage> Answer(
        HttpStatusCode status,
        string body = "",
        string contentType = "application/json",
        string? retryAfter = null)
    {
        return () =>
        {
            var response = new HttpResponseMessage(status)
            {
                Content = new StringContent(body, System.Text.Encoding.UTF8, contentType),
            };

            if (retryAfter is not null)
                response.Headers.TryAddWithoutValidation("Retry-After", retryAfter);

            return response;
        };
    }

    /// <summary>No answer at all: the connection is refused.</summary>
    public static Func<HttpResponseMessage> Unreachable()
    {
        return () => throw new HttpRequestException("No connection could be made.");
    }

    /// <summary>A client whose requests get these answers, in order, and never refreshes its token.</summary>
    public static (ApiClient Client, ScriptedHandler Handler) Client(params Func<HttpResponseMessage>[] outcomes)
    {
        return ClientWithRefresh(refresher: null, outcomes);
    }

    /// <summary>A client whose requests get these answers, in order, refreshing with <paramref name="refresher"/>.</summary>
    public static (ApiClient Client, ScriptedHandler Handler) ClientWithRefresh(
        Func<string>? refresher,
        params Func<HttpResponseMessage>[] outcomes)
    {
        var handler = new ScriptedHandler(outcomes);
        var client = new ApiClient(() => FakeToken, refresher, handler);
        return (client, handler);
    }
}
