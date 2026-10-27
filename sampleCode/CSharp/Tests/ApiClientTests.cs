using Implan.ApiSamples.Tests.Support;

namespace Implan.ApiSamples.Tests;

/// <summary>
/// The HTTP client: bodies, query strings, logging, errors, token refresh, retries,
/// and a host that never answers.
/// </summary>
public sealed class ApiClientTests
{
    private readonly LogFileFixture _log;

    public ApiClientTests(LogFileFixture log)
    {
        _log = log;
    }

    [Fact]
    public void GetText_WithABody_StaysAGetAndSendsJson()
    {
        var (client, handler) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, "Display Code\r\n1", "text/csv"));

        var text = ImpactResults.GetEstimatedGrowthPercentage(
            client, 1, new ImpactResultsExportRequest { DollarYear = 2026 });

        var sent = Assert.Single(handler.Sent);
        Assert.Equal(HttpMethod.Get, sent.Method);
        Assert.Equal("application/json", sent.ContentType);
        Assert.Contains("\"eventTags\":[]", sent.Body);
        Assert.Equal("Display Code\r\n1", text);
    }

    [Fact]
    public void GetText_WithRepeatedFilter_SendsRepeatedParameters()
    {
        var (client, handler) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, "GroupName\r\n", "text/csv"));
        var filters = new ResultFilters { Year = 2026, Regions = ["Oregon (2024)", "Wisconsin (2024)"] };

        ImpactResults.GetSummaryEconomicIndicators(client, 1, filters);

        var query = WebUtility.UrlDecode(Assert.Single(handler.Sent).Uri?.Query ?? string.Empty);
        Assert.Contains("regions=Oregon (2024)&regions=Wisconsin (2024)", query);
    }

    [Fact]
    public void Exchange_IsLoggedWithTheTokenRedacted()
    {
        var (client, _) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, "[]"));

        client.GetText("/api/v1/region/RegionTypes");

        var log = _log.ReadAll();
        Assert.Contains("RegionTypes", log);
        Assert.Contains("Authorization: <redacted>", log);
        Assert.DoesNotContain("not.a.real.token", log);
    }

    [Fact]
    public void ErrorResponse_ThrowsWithItsProblemDetails()
    {
        const string problem =
            """{"title":"Project not found","detail":"No Project was found.","traceId":"00-abc-01"}""";
        var (client, _) = Scripted.Client(
            Scripted.Answer(HttpStatusCode.NotFound, problem, "application/problem+json"));

        var error = Assert.Throws<ImplanApiException>(() => client.GetText("/api/v1/impact/project/x"));

        Assert.Equal(404, error.StatusCode);
        Assert.Equal("Project not found", error.Problem.Title);
        Assert.Equal("00-abc-01", error.Problem.TraceId);
    }

    /// <remarks>
    /// RestSharp marks every status other than 2xx and 404 as a failed request, so a
    /// client that read that flag would report these as "could not reach the API".
    /// </remarks>
    [Theory]
    [InlineData(HttpStatusCode.BadRequest)]
    [InlineData(HttpStatusCode.Conflict)]
    [InlineData(HttpStatusCode.UnprocessableEntity)]
    public void ClientError_IsAnApiErrorNotATransportError(HttpStatusCode status)
    {
        var (client, _) = Scripted.Client(Scripted.Answer(status, """{"title":"Refused"}"""));

        var error = Assert.Throws<ImplanApiException>(() => client.GetText("/x"));

        Assert.Equal((int)status, error.StatusCode);
    }

    [Fact]
    public void Unauthorized_RefreshesTheTokenOnceAndRetries()
    {
        var refreshes = 0;
        var (client, _) = Scripted.ClientWithRefresh(
            () =>
            {
                refreshes++;
                return Scripted.FakeToken;
            },
            Scripted.Answer(HttpStatusCode.Unauthorized),
            Scripted.Answer(HttpStatusCode.OK, """{"ok":true}"""));

        Assert.Equal("""{"ok":true}""", client.GetText("/x"));
        Assert.Equal(1, refreshes);
    }

    [Fact]
    public void Unauthorized_Twice_ThrowsWithoutRefreshingAgain()
    {
        var refreshes = 0;
        var (client, _) = Scripted.ClientWithRefresh(
            () =>
            {
                refreshes++;
                return Scripted.FakeToken;
            },
            Scripted.Answer(HttpStatusCode.Unauthorized),
            Scripted.Answer(HttpStatusCode.Unauthorized));

        var error = Assert.Throws<ImplanApiException>(() => client.GetText("/x"));

        Assert.Equal(401, error.StatusCode);
        Assert.Equal(1, refreshes);
    }

    [Fact]
    public void PostFile_RetriedAfterUnauthorized_SendsTheWholeFileAgain()
    {
        const string Workbook = "stand-in workbook bytes";
        var path = Path.GetTempFileName();
        File.WriteAllText(path, Workbook);
        try
        {
            var (client, handler) = Scripted.ClientWithRefresh(
                () => Scripted.FakeToken,
                Scripted.Answer(HttpStatusCode.Unauthorized),
                Scripted.Answer(HttpStatusCode.OK, """{"ok":true}"""));

            client.PostFile("/x", "excelFile", path);

            Assert.Equal(2, handler.Sent.Count);
            Assert.All(handler.Sent, sent => Assert.Contains(Workbook, sent.Body));
        }
        finally
        {
            File.Delete(path);
        }
    }

    [Fact]
    public void ServiceUnavailable_IsRetriedWhenTheApiSaysWhen()
    {
        var (client, handler) = Scripted.Client(
            Scripted.Answer(HttpStatusCode.ServiceUnavailable, retryAfter: "0"),
            Scripted.Answer(HttpStatusCode.OK, "[]"));

        Assert.Equal("[]", client.GetText("/x"));
        Assert.Equal(2, handler.Sent.Count);
    }

    [Fact]
    public void UnreachableHost_ThrowsTransportException()
    {
        var (client, _) = Scripted.Client(Scripted.Unreachable());

        Assert.Throws<ImplanTransportException>(() => client.GetText("/x"));
    }
}
