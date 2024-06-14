using System.ComponentModel;
using System.Diagnostics.CodeAnalysis;

namespace ConsoleApp.Endpoints;

/// <summary>
/// PHX-11909
/// </summary>
public enum ImpactEventType
{
    Empty = 0,
    [Description("Industry Output")] IndustryOutput = 1,

    [Description("Industry Employment")] IndustryEmployment = 2,

    [Description("Industry Employee Compensation")]
    IndustryEmployeeCompensation = 3,

    [Description("Industry Proprietor Income")]
    IndustryProprietorIncome = 4,

    [Description("Commodity Output")] CommodityOutput = 5,

    [Description("Labor Income")] LaborIncome = 6,

    [Description("Household Income")] HouseholdIncome = 7,

    [Description("2018 Industry Spending Pattern")]
    IndustrySpendingPattern2018 = 8,

    [Description("2018 Institutional Spending Pattern")]
    InstitutionalSpendingPattern2018 = 30,

    [Description("2019 Industry Spending Pattern")]
    IndustrySpendingPattern2019 = 9,

    [Description("2019 Institutional Spending Pattern")]
    InstitutionalSpendingPattern2019 = 40,

    [Description("Industry Spending Pattern")]
    IndustrySpendingPattern = 12,

    [Description("Institutional Spending Pattern")]
    InstitutionalSpendingPattern = 11,

    [Description("Industry Contribution Analysis")]
    IndustryContributionAnalysis = 20,

    [Description("Industry Impact Analysis (Detailed)")]
    IndustryImpactAnalysis = 10,

    [Description("Custom Spending Pattern")]
    CustomSpendingPattern = 13,

    [Description("Household Spending Pattern")]
    HouseholdSpendingPattern = 14,

    [Description("Industry Impact Analysis (Detailed)")]
    InternationalIndustryImpactAnalysis = 15,

    [Description("Industry Impact Analysis (Custom)")]
    CustomIndustryImpactAnalysis = 16,

    [Description("Industry Impact Analysis (Custom)")]
    CustomInternationalIndustryImpactAnalysis = 17,
}

public record class Event
{
    public virtual ImpactEventType ImpactEventType => ImpactEventType.Empty;
    public required string Title { get; set; }
    public Guid Id { get; set; }
    public Guid ProjectId { get; set; }
    public string[] Tags { get; set; } = [];
}

public enum MarginType
{
    ProducerPrice,
    PurchaserPrice
}

public record class IndustryOutputEvent : Event
{
    public required double? Output { get; set; }
    public double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }
    public MarginType? MarginType { get; set; }
    public double? Percentage { get; set; }
    public int? DatasetId { get; set; }

    public override ImpactEventType ImpactEventType => ImpactEventType.IndustryOutput;
}

public record class IndustryEmploymentEvent : Event
{
    public double? Output { get; set; }
    public required double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override ImpactEventType ImpactEventType => ImpactEventType.IndustryEmployment;
}

public record class IndustryEmployeeCompensationEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public required double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override ImpactEventType ImpactEventType => ImpactEventType.IndustryEmployeeCompensation;
}

public record class IndustryProprietorIncomeEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public required double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override ImpactEventType ImpactEventType => ImpactEventType.IndustryProprietorIncome;
}

public class Events
{
    public static Event? GetEvent(Guid projectGuid, Guid eventGuid)
    {
        // {{api_domain}}api/v1/impact/project/:projectGuid/event/:eventGuid
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event/{eventGuid}");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);
        request.AddUrlSegment("eventGuid", eventGuid);

        return Rest.GetResponseData<Event>(request);
    }

    public static TEvent? GetEvent<TEvent>(Guid projectGuid, Guid eventGuid)
        where TEvent : Event
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event/{eventGuid}");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);
        request.AddUrlSegment("eventGuid", eventGuid);
        return Rest.GetResponseData<TEvent>(request);
    }
    
    public static Event[] GetEvents(Guid projectGuid)
    {
        // {{api_domain}}api/v1/impact/project/:projectGuid/event
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Event[]>(request).ThrowIfNull();
    }
    
    // Though there are 17? different Impact Event Types, there is technically only one endpoint to add them
    // They are split up here for clarity of input Model
    
    public static IndustryOutputEvent AddEvent(Guid projectGuid, IndustryOutputEvent industryOutputEvent)
    {
        // [HttpPost("external/api/v1/impact/project/{projectId}/event")]
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(industryOutputEvent);
        
        return Rest.GetResponseData<IndustryOutputEvent>(request).ThrowIfNull();
    }
}