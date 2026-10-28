using Implan.ApiSamples.Workflows;

namespace Implan.ApiSamples.Tests;

/// <summary>BulkFromCsv's input files: read strictly, and checked before anything is created.</summary>
public sealed class BulkInputTests
{
    private static readonly string[] RegionColumns = ["fips", "region_description", "model_name"];

    private static List<Dictionary<string, string>> Read(string text)
    {
        var path = Path.GetTempFileName();
        File.WriteAllText(path, text);
        try
        {
            return BulkFromCsvWorkflow.ReadCsv(path, RegionColumns);
        }
        finally
        {
            File.Delete(path);
        }
    }

    private static Dictionary<string, string> Region(string fips, string modelName, int line = 2)
    {
        return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["fips"] = fips, ["region_description"] = "", ["model_name"] = modelName, ["line"] = line.ToString(),
        };
    }

    private static Dictionary<string, string> Event(
        string name, string code = "1", string type = "Industry Output", string value = "1000", int line = 2)
    {
        return new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            ["Name"] = name, ["Code"] = code, ["Type"] = type, ["Value"] = value, ["line"] = line.ToString(),
        };
    }

    [Fact]
    public void ReadCsv_UnquotedComma_IsReportedWithItsLine()
    {
        var error = Assert.Throws<ArgumentException>(() =>
            Read("fips,region_description,model_name\n41019,Douglas County, OR,MyModel\n"));

        Assert.Contains("line 2", error.Message);
        Assert.Contains("double quotes", error.Message);
    }

    [Fact]
    public void ReadCsv_QuotedComma_IsOneValue()
    {
        var rows = Read("fips,region_description,model_name\n41019,\"Douglas County, OR\",MyModel\n");

        Assert.Equal("MyModel", rows[0]["model_name"]);
    }

    [Fact]
    public void ReadCsv_SemicolonFile_IsReportedAsNotCommaSeparated()
    {
        var error = Assert.Throws<ArgumentException>(() =>
            Read("fips;region_description;model_name\n41019;Douglas;MyModel\n"));

        Assert.Contains("comma-separated", error.Message);
    }

    [Fact]
    public void ReadCsv_RowsOfBareCommas_AreSkipped()
    {
        var rows = Read("fips,region_description,model_name\n41019,Douglas,MyModel\n,,\n,,\n");

        Assert.Single(rows);
    }

    [Fact]
    public void CheckInputs_GoodRows_PassAndAreNormalized()
    {
        List<Dictionary<string, string>> states = [Region("1000", "South"), Region("1", "South", line: 3)];
        List<Dictionary<string, string>> events = [Event("Output", value: "$1,000,000")];

        BulkFromCsvWorkflow.CheckInputs(states, [], events);

        Assert.Equal(["01000", "01"], states.Select(r => r["fips"]));
        Assert.Equal("1000000", events[0]["Value"]);
    }

    [Fact]
    public void CheckInputs_ReportsEveryProblemAtOnce()
    {
        List<Dictionary<string, string>> states = [Region("ABC", "Lane & Douglas")];
        List<Dictionary<string, string>> counties = [Region("41019", "Lane & Douglas")];
        List<Dictionary<string, string>> events =
        [
            Event("Food", type: "Household Income"),
            Event("Food", code: "x", value: "lots", line: 3),
        ];

        var error = Assert.Throws<ArgumentException>(() =>
            BulkFromCsvWorkflow.CheckInputs(states, counties, events));

        Assert.Contains("'ABC' is not a state or county FIPS code", error.Message);
        Assert.Contains("contains &", error.Message);
        Assert.Contains("is in both state_based.csv and county_based.csv", error.Message);
        Assert.Contains("is not Industry Output or Commodity Output", error.Message);
        Assert.Contains("'Food' is already used", error.Message);
        Assert.Contains("Code 'x' is not a whole number", error.Message);
        Assert.Contains("Value 'lots' is not an amount", error.Message);
    }

    [Fact]
    public void CheckInputs_NeedsARegionAndAnEvent()
    {
        var error = Assert.Throws<ArgumentException>(() =>
            BulkFromCsvWorkflow.CheckInputs([], [], []));

        Assert.Contains("both empty", error.Message);
        Assert.Contains("demo_events.csv is empty", error.Message);
    }

    [Fact]
    public void UniqueTitle_DropsCharactersImplanRejects()
    {
        Assert.StartsWith("ImpactApi Sample - Prince Georges County - ", Config.UniqueTitle("Prince George's County"));
    }
}
