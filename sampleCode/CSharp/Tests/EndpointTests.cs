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
    public void SumEffects_SplitsDirectFromTheRestAndSkipsTheTotalsRow()
    {
        const string Report =
            "GroupName, EventName, ModelName, Impact, Employment, LaborIncome, ValueAdded, Output, TagName\r\n" +
            "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),1 - Direct,10.5,100,200,1000,\r\n" +
            "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),2 - Indirect,1.25,10,20,300,\r\n" +
            "\"Smith, Inc (2024)\",Restaurants,Oregon (2024),3 - Induced,0.25,5,10,200,\r\n" +
            "Totals,,,,12,115,230,1500,\r\n";

        var totals = ImpactResults.SumEffects(Report);

        Assert.Equal(new ImpactResults.EffectTotals(1000, 500, 12), totals);
    }

    [Fact]
    public void SumEffects_ReportWithoutAnImpactColumn_SaysSo()
    {
        var error = Assert.Throws<InvalidDataException>(
            () => ImpactResults.SumEffects("GroupName,Output,Employment\r\nOregon (2024),1000,10\r\n"));

        Assert.Contains("Impact", error.Message);
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
