using Implan.ApiSamples.Tests.Support;

namespace Implan.ApiSamples.Tests;

/// <summary>Resolving identifiers from an existing Project rather than from today's defaults.</summary>
public sealed class IdentifierTests
{
    // A Project on an older Industry Set: scheme 8 is not the current default.
    private const string OlderScheme =
        """{"id":8,"description":"546 Unaggregated","industrySetId":8,"householdSetIds":[1],"mapCode":"US","status":"Complete"}""";

    private const string IndustrySets =
        """[{"id":8,"description":"546 Industries","isDefault":false,"activeStatus":true,"defaultAggregationSchemeId":8},"""
        + """{"id":12,"description":"528 Industries","isDefault":true,"activeStatus":true,"defaultAggregationSchemeId":14}]""";

    private const string SchemeDatasets =
        """[{"id":86,"description":"2021","isDefault":false},{"id":87,"description":"2022","isDefault":true}]""";

    [Fact]
    public void ResolveForProject_UsesTheProjectsOwnScheme()
    {
        var (client, handler) = Scripted.Client(
            Scripted.Answer(HttpStatusCode.OK, OlderScheme),
            Scripted.Answer(HttpStatusCode.OK, IndustrySets),
            Scripted.Answer(HttpStatusCode.OK, SchemeDatasets));
        var project = new Project { Title = "Older", AggregationSchemeId = 8, HouseholdSetId = 3 };

        var ids = Endpoints.Identifiers.ResolveForProject(client, project);

        Assert.Equal(8, ids.AggregationSchemeId);
        Assert.Equal(8, ids.IndustrySet.Id);
        Assert.Equal(87, ids.DatasetId);
        Assert.Equal(3, ids.HouseholdSetId);
        Assert.Equal(MapCode.US, ids.MapCode);
        Assert.EndsWith("/api/v1/aggregationSchemes/8", handler.Sent[0].Uri!.AbsolutePath);
        Assert.EndsWith("/api/v1/datasets/8", handler.Sent[2].Uri!.AbsolutePath);
    }

    [Fact]
    public void ResolveForProject_TakesTheMapCodeFromTheScheme()
    {
        var canadian = OlderScheme.Replace("\"id\":8,", "\"id\":9,").Replace("\"US\"", "\"CAN\"");
        var (client, _) = Scripted.Client(
            Scripted.Answer(HttpStatusCode.OK, canadian),
            Scripted.Answer(HttpStatusCode.OK, IndustrySets),
            Scripted.Answer(HttpStatusCode.OK, SchemeDatasets));
        var project = new Project { Title = "Canadian", AggregationSchemeId = 9, HouseholdSetId = 1 };

        var ids = Endpoints.Identifiers.ResolveForProject(client, project);

        Assert.Equal(MapCode.CAN, ids.MapCode);
    }
}
