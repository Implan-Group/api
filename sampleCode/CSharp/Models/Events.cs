namespace Implan.ApiSamples.Models;

/// <summary>
/// The event types the API accepts.
/// </summary>
/// <remarks>
/// Not every type is valid in every Project: the international types are only valid
/// in an international Aggregation Scheme, and <c>IndustryImpactAnalysis</c> and
/// <c>IndustryProprietorIncome</c> are not valid in one. Ask the Project which
/// types it accepts with <c>Endpoints.Events.GetEventTypes</c> rather than assuming.
///
/// Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
/// </remarks>
public static class EventTypes
{
    public const string IndustryOutput = "IndustryOutput";
    public const string IndustryEmployment = "IndustryEmployment";
    public const string IndustryEmployeeCompensation = "IndustryEmployeeCompensation";
    public const string IndustryProprietorIncome = "IndustryProprietorIncome";
    public const string CommodityOutput = "CommodityOutput";
    public const string LaborIncome = "LaborIncome";
    public const string HouseholdIncome = "HouseholdIncome";
    public const string IndustryContributionAnalysis = "IndustryContributionAnalysis";
    public const string IndustryImpactAnalysis = "IndustryImpactAnalysis";
    public const string IndustrySpendingPattern = "IndustrySpendingPattern";
    public const string InstitutionalSpendingPattern = "InstitutionalSpendingPattern";
}

/// <summary>
/// Whether a value is the price the producer received or the buyer paid.
/// </summary>
/// <remarks>
/// Only retail and wholesale industries, and commodities sold through them, can be
/// margined. Setting PurchaserPrice on anything else is reverted to ProducerPrice
/// before the impact runs.
///
/// Support: Margins - https://support.implan.com/hc/en-us/articles/115009506007
/// </remarks>
public enum MarginType
{
    ProducerPrice,
    PurchaserPrice,
}

/// <summary>
/// How a spending-pattern event's value should be read.
/// </summary>
/// <remarks>
/// <c>IntermediateExpenditure</c> spends the whole value across the pattern's
/// commodities. <c>Output</c> multiplies it by the industry's gross absorption
/// first, so only the portion actually spent on intermediate inputs flows through.
/// </remarks>
public enum SpendingPatternValueType
{
    IntermediateExpenditure,
    Output,
}

/// <summary>
/// Fields shared by every event type.
/// </summary>
/// <remarks>
/// An Event says what changed, a Group says where and when, and an Impact Run
/// combines them. Every event carries <see cref="ImpactEventType"/>, and that value
/// decides which other fields the API expects, so these are one class per type
/// rather than one class with every field on it.
///
/// Leave <see cref="Id"/> unset when creating: the API generates it and returns it.
/// <see cref="Title"/> must be unique among the Project's events and must avoid an
/// ampersand and the characters <c>| ; % * ? ! = ' " ^ #</c>.
///
/// <see cref="Tags"/> are free text and are how results get filtered later; see the
/// AdvancedEvents workflow. Updating an event merges tags rather than replacing
/// them, so a tag can be added but not removed through an update.
/// </remarks>
public class ImpactEvent
{
    public virtual string ImpactEventType { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public Guid? Id { get; set; }
    public Guid? ProjectId { get; set; }
    public List<string> Tags { get; set; } = [];

    /// <summary>Anything the API returned that this model does not declare.</summary>
    [JsonExtensionData]
    public Dictionary<string, JsonElement> Extra { get; set; } = [];

    /// <summary>One line naming the event, for the console.</summary>
    public string Describe() => $"{Title}  [{ImpactEventType}]  id={Id}";
}

/// <summary>
/// A change in what an industry produces, stated in dollars of output.
/// </summary>
/// <remarks>
/// The most common event type and the right default when you know a dollar figure
/// and the industry that earned it. Supply any one of output, employment, employee
/// compensation, or proprietor income; IMPLAN estimates the rest from the
/// industry's averages for the region.
///
/// Support: Industry Events
/// https://support.implan.com/hc/en-us/articles/360051441834-Industry-Events
/// </remarks>
public sealed class IndustryOutputEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.IndustryOutput;
    public int IndustryCode { get; set; }
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }

    // Margins apply to retail and wholesale industries only.
    public MarginType? MarginType { get; set; }
    public double? Percentage { get; set; }

    /// <summary>The data year the margins come from, when margins are applied.</summary>
    public int? DatasetId { get; set; }
}

/// <summary>
/// A change in demand for a commodity rather than for an industry's output.
/// </summary>
/// <remarks>
/// Use this when you know what was bought rather than who produced it. IMPLAN
/// decides which industries supply the commodity locally.
/// </remarks>
public sealed class CommodityOutputEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.CommodityOutput;
    public int CommodityCode { get; set; }
    public double? Output { get; set; }
    public MarginType? MarginType { get; set; }
}

/// <summary>
/// A change in income for one household income bracket.
/// </summary>
/// <remarks>
/// <see cref="HouseholdIncomeCode"/> is a specification code, not an industry code.
/// Read the valid ones from <c>Endpoints.Events.GetEventSpecifications</c>; they
/// look like <c>10002 - Households 15-30k</c>.
///
/// Support: Household Income Events
/// https://support.implan.com/hc/en-us/articles/360052212413
/// </remarks>
public sealed class HouseholdIncomeEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.HouseholdIncome;
    public int HouseholdIncomeCode { get; set; }
    public double? Value { get; set; }
}

/// <summary>
/// The contribution an existing industry already makes to a region.
/// </summary>
/// <remarks>
/// A different question from an impact. An impact asks what would change if new
/// activity arrived; a contribution asks how much of the current economy rests on
/// an industry that is already there. The analysis constrains the industry from
/// buying from itself so its own output is not counted twice.
///
/// Set <see cref="Output"/> to a dollar figure, or set
/// <see cref="IsOutputPercentage"/> and give Output as a share of the industry's
/// regional output from 0 to 1.
///
/// Support: ICA: Introduction to Industry Contribution Analysis
/// https://support.implan.com/hc/en-us/articles/360025854654
/// </remarks>
public sealed class IndustryContributionAnalysisEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.IndustryContributionAnalysis;
    public int IndustryCode { get; set; }
    public double? Output { get; set; }
    public bool IsOutputPercentage { get; set; }
}

/// <summary>
/// An industry event where you know the production function, not just a total.
/// </summary>
/// <remarks>
/// Where an Industry Output event gives IMPLAN one number and lets it estimate the
/// rest, this type lets you state employment, compensation, proprietor income,
/// taxes, and intermediate inputs yourself. Use it when you have the operating
/// statement for the thing being modeled, such as a hospital or a university.
///
/// Support: Industry Impact Analysis (Detailed) Events
/// https://support.implan.com/hc/en-us/articles/4414451454491
/// </remarks>
public sealed class IndustryImpactAnalysisEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.IndustryImpactAnalysis;
    public int IndustryCode { get; set; }

    public double? IntermediateInputs { get; set; }
    public double? TotalOutput { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public double? TotalLaborIncome { get; set; }
    public double? OtherPropertyIncome { get; set; }
    public double? TaxOnProductionAndImports { get; set; }

    public double? WageAndSalaryEmployment { get; set; }
    public double? ProprietorEmployment { get; set; }
    public double? TotalEmployment { get; set; }

    /// <summary>
    /// Share of intermediate inputs bought inside the region, 0 to 1. Leave at 1.0
    /// when everything is local, or set <see cref="IsSam"/> to let IMPLAN use the
    /// region's own trade data instead.
    /// </summary>
    public double? LocalPurchasePercentage { get; set; } = 1.0;

    public bool IsSam { get; set; }

    /// <summary>Which data year's spending pattern the intermediate inputs flow through.</summary>
    public int? SpendingPatternDatasetId { get; set; }

    public SpendingPatternValueType SpendingPatternValueType { get; set; }
        = SpendingPatternValueType.IntermediateExpenditure;

    public List<SpendingPatternCommodity> SpendingPatternCommodities { get; set; } = [];

    // Returned by the API on read. Setting either employment flag requires
    // conversion data to exist for the Industry Set, so leave them alone unless you
    // know the region has it.
    public bool IsLocalEmployeeCompensation { get; set; }
    public bool IsFteEmployment { get; set; }
    public bool IsWageAndSalary { get; set; }
    public bool IsContributionAnalysis { get; set; }
}

/// <summary>
/// An industry's purchases of goods and services, excluding labor.
/// </summary>
/// <remarks>
/// Use this to model a buyer rather than a producer: the event spends money through
/// an industry's supply chain without adding any direct output of its own. The
/// commodity list can be left empty to use IMPLAN's default pattern, or supplied
/// with edited coefficients, which is what the AdvancedEvents workflow does.
///
/// Support: Industry Spending Pattern Events
/// https://support.implan.com/hc/en-us/articles/360052212933
/// </remarks>
public sealed class IndustrySpendingPatternEvent : ImpactEvent
{
    public override string ImpactEventType { get; set; } = EventTypes.IndustrySpendingPattern;
    public int IndustryCode { get; set; }
    public double? Output { get; set; }

    public double? LocalPurchasePercentage { get; set; } = 1.0;
    public bool IsSam { get; set; }

    public int? SpendingPatternDatasetId { get; set; }
    public long? SpendingPatternRegionUrid { get; set; }

    public SpendingPatternValueType SpendingPatternValueType { get; set; }
        = SpendingPatternValueType.Output;

    public List<SpendingPatternCommodity> SpendingPatternCommodities { get; set; } = [];
}

/// <summary>
/// Builds the right event class from a response, whatever type it turns out to be.
/// </summary>
/// <remarks>
/// <c>GET /api/v1/impact/project/{projectId}/event</c> returns a mixed list, so the
/// type has to be read from each item before it can be deserialized. Types not
/// listed here deserialize to the base <see cref="ImpactEvent"/>, which carries the
/// shared fields and keeps everything else in <c>Extra</c>.
/// </remarks>
public static class EventFactory
{
    private static readonly Dictionary<string, Type> Types = new(StringComparer.OrdinalIgnoreCase)
    {
        [EventTypes.IndustryOutput] = typeof(IndustryOutputEvent),
        [EventTypes.CommodityOutput] = typeof(CommodityOutputEvent),
        [EventTypes.HouseholdIncome] = typeof(HouseholdIncomeEvent),
        [EventTypes.IndustryContributionAnalysis] = typeof(IndustryContributionAnalysisEvent),
        [EventTypes.IndustryImpactAnalysis] = typeof(IndustryImpactAnalysisEvent),
        [EventTypes.IndustrySpendingPattern] = typeof(IndustrySpendingPatternEvent),
    };

    /// <summary>Reads one event from a JSON element, choosing the class by its type.</summary>
    public static ImpactEvent FromJson(JsonElement element)
    {
        var typeName = element.TryGetProperty("impactEventType", out var value)
            ? value.GetString() ?? string.Empty
            : string.Empty;

        var target = Types.TryGetValue(typeName, out var known) ? known : typeof(ImpactEvent);
        var raw = element.GetRawText();

        return (ImpactEvent?)JsonSerializer.Deserialize(raw, target, Json.Options)
               ?? new ImpactEvent { ImpactEventType = typeName };
    }

    /// <summary>Reads a JSON array of mixed event types.</summary>
    public static List<ImpactEvent> ListFromJson(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Array)
            return [];

        return element.EnumerateArray().Select(FromJson).ToList();
    }
}
