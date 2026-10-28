using Implan.ApiSamples.Tests.Support;

namespace Implan.ApiSamples.Tests;

/// <summary>The endpoints that answer in plain text rather than JSON, and the token from the auth endpoint.</summary>
public sealed class EndpointTests
{
    [Theory]
    [InlineData("Complete", "text/plain")]
    [InlineData("\"Complete\"", "application/json")]
    public void GetImpactStatus_ReadsTheStatusWithOrWithoutQuotes(string body, string contentType)
    {
        var (client, _) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, body, contentType));

        Assert.Equal(ImpactStatus.Complete, Impacts.GetImpactStatus(client, 1));
    }

    [Fact]
    public void GetImpactStatus_UnknownStatus_IsReportedNotGuessed()
    {
        var (client, _) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, "SomethingNew", "text/plain"));

        Assert.Equal(ImpactStatus.Unknown, Impacts.GetImpactStatus(client, 1));
    }

    [Fact]
    public void RunImpact_ReadsABareRunId()
    {
        var (client, _) = Scripted.Client(Scripted.Answer(HttpStatusCode.OK, "30542"));

        Assert.Equal(30542L, Impacts.RunImpact(client, Guid.NewGuid()));
    }

    /// <remarks>
    /// RestSharp asks for JSON by default, and the auth endpoint answers that with the
    /// token as a JSON string, quotes included.
    /// </remarks>
    [Theory]
    [InlineData("\"Bearer abc.def\"", "Bearer abc.def")]
    [InlineData("Bearer abc.def", "Bearer abc.def")]
    [InlineData(" \"abc.def\"\n", "Bearer abc.def")]
    [InlineData("  ", "")]
    public void NormalizeToken_UnwrapsQuotesAndKeepsTheBearerPrefix(string content, string expected)
    {
        Assert.Equal(expected, Auth.NormalizeToken(content));
    }
}
