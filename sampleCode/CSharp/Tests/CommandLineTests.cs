namespace Implan.ApiSamples.Tests;

/// <summary>The command line, and the small helpers the workflows lean on.</summary>
public sealed class CommandLineTests
{
    [Fact]
    public void Parse_RegionalExportsOptions()
    {
        var options = CommandLineOptions.Parse(["regional-exports", "--region-type", "County", "--limit", "0"]);

        Assert.Equal("regional-exports", options.Workflow);
        Assert.Equal(RegionType.County, options.RegionType);
        Assert.Null(options.Limit);
    }

    [Fact]
    public void Parse_ProjectIdAndTheDefaultMapCode()
    {
        var projectId = Guid.NewGuid();

        var options = CommandLineOptions.Parse(["run-impact-analysis", "--project-id", projectId.ToString()]);

        Assert.Equal(projectId, options.ProjectId);
        Assert.Equal(MapCode.US, options.MapCode);
    }

    [Fact]
    public void Parse_UnknownOption_Throws()
    {
        Assert.Throws<ArgumentException>(() => CommandLineOptions.Parse(["regions", "--nope"]));
    }

    [Fact]
    public void SafeFileName_ReplacesCharactersWindowsRejects()
    {
        Assert.Equal(
            "Louisville_Jefferson County, KY-IN MSA",
            ImpactResults.SafeFileName("Louisville/Jefferson County, KY-IN MSA"));
    }

    [Fact]
    public void UniqueTitle_CarriesThePrefix()
    {
        Assert.StartsWith("ImpactApi Sample - Label - ", Config.UniqueTitle("Label"));
    }
}
