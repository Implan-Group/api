namespace Implan.ApiSamples.Tests;

/// <summary>What the request models send.</summary>
public sealed class SerializationTests
{
    [Fact]
    public void Serialize_UsesCamelCasePropertyNames()
    {
        var json = Json.Serialize(new Group { HashId = "abc" });

        Assert.Contains("\"hashId\":\"abc\"", json);
    }

    [Fact]
    public void Serialize_GroupWithHashId_SendsNoOtherRegionIdentifier()
    {
        var json = Json.Serialize(new Group
        {
            Title = "g",
            HashId = "abc",
            DollarYear = 2026,
            GroupEvents = [new GroupEvent { EventId = Guid.NewGuid() }, new GroupEvent { EventId = Guid.NewGuid() }],
        });

        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        Assert.Equal("abc", root.GetProperty("hashId").GetString());
        Assert.False(root.TryGetProperty("urid", out _));
        Assert.False(root.TryGetProperty("userModelId", out _));
        Assert.Equal(2, root.GetProperty("groupEvents").GetArrayLength());
    }

    [Fact]
    public void Serialize_OneGroupEvent_IsStillAnArray()
    {
        var json = Json.Serialize(new Group
        {
            Title = "g",
            HashId = "abc",
            GroupEvents = [new GroupEvent { EventId = Guid.NewGuid() }],
        });

        Assert.Contains("\"groupEvents\":[{", json);
    }

    [Fact]
    public void Serialize_OneTag_IsStillAnArray()
    {
        var json = Json.Serialize(new IndustryOutputEvent
        {
            Title = "t",
            IndustryCode = 1,
            Output = 1,
            Tags = ["spending"],
        });

        Assert.Contains("\"tags\":[\"spending\"]", json);
    }

    [Theory]
    [InlineData("regions")]
    [InlineData("impacts")]
    [InlineData("groupNames")]
    [InlineData("eventNames")]
    [InlineData("eventTags")]
    public void Serialize_GrowthRequest_KeepsEveryFilterArrayEvenEmpty(string name)
    {
        var json = Json.Serialize(new ImpactResultsExportRequest { DollarYear = 2026 });

        Assert.Contains($"\"{name}\":[]", json);
    }

    [Fact]
    public void Serialize_CombineRegionRequest_SendsHashIdsAsAnArray()
    {
        var json = Json.Serialize(new CombineRegionRequest { Description = "d", HashIds = ["a", "b"] });

        Assert.Contains("\"hashIds\":[\"a\",\"b\"]", json);
    }
}
