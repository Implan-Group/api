namespace Implan.ApiSamples.Tests;

/// <summary>What the response models read, including fields they have never seen.</summary>
public sealed class DeserializationTests
{
    [Fact]
    public void Deserialize_ReadsCamelCaseFields()
    {
        var region = Json.Deserialize<Region>("""{"isMrioAllowed":true,"m49Code":"840"}""")!;

        Assert.True(region.IsMrioAllowed);
        Assert.Equal("840", region.M49Code);
    }

    [Fact]
    public void EventFactory_KnownType_ReadsDeclaredFieldsAndKeepsUnknownOnes()
    {
        using var document = JsonDocument.Parse(
            $$"""{"impactEventType":"{{EventTypes.IndustryOutput}}","industryCode":1,"brandNewField":42}""");

        var industryOutput = Assert.IsType<IndustryOutputEvent>(EventFactory.FromJson(document.RootElement));
        Assert.Equal(1, industryOutput.IndustryCode);
        Assert.Equal(42, industryOutput.Extra["brandNewField"].GetInt32());
    }

    [Fact]
    public void EventFactory_UnknownType_ReadsAsAPlainEvent()
    {
        using var document = JsonDocument.Parse("""{"impactEventType":"SomethingNew","weird":true}""");

        var impactEvent = Assert.IsType<ImpactEvent>(EventFactory.FromJson(document.RootElement));
        Assert.Equal("SomethingNew", impactEvent.ImpactEventType);
        Assert.True(impactEvent.Extra["weird"].GetBoolean());
    }

    [Fact]
    public void Deserialize_Region_ReadsBuildStatusAndKeepsUnknownFields()
    {
        var region = Json.Deserialize<Region>(
            """{"hashId":"x","modelBuildStatus":"Complete","somethingAddedLater":1}""")!;

        Assert.True(region.IsBuilt);
        Assert.False(region.IsUserDefined);
        Assert.True(region.Extra.ContainsKey("somethingAddedLater"));
    }

    [Fact]
    public void Describe_UserDefinedRegion_SaysItIsYours()
    {
        var region = Json.Deserialize<Region>(
            """{"hashId":"x","description":"Two counties","userModelId":42}""")!;

        Assert.True(region.IsUserDefined);
        Assert.Contains("yours, userModelId=42", region.Describe());
    }

    [Fact]
    public void Deserialize_Group_ReadsNestedGroupEvents()
    {
        var group = Json.Deserialize<Group>(
            $$"""{"title":"g","groupEvents":[{"eventId":"{{Guid.NewGuid()}}","scalingFactor":0.5}]}""")!;

        Assert.Equal(0.5, Assert.Single(group.GroupEvents).ScalingFactor);
    }
}
