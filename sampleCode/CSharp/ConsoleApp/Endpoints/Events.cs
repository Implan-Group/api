using System.ComponentModel;
using System.Diagnostics.CodeAnalysis;

namespace ConsoleApp.Endpoints;

public record class Event
{
    /// <summary>
    /// The specific Impact Event Type for this event. 
    /// </summary>
    public virtual string ImpactEventType => "Empty";

    /// <summary>
    /// Unique-per-Project description of this Event
    /// </summary>
    public required string Title { get; set; }

    /// <summary>
    /// Unique identifier for this Event
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Unique identifier for the Project this Event belongs to
    /// </summary>
    public Guid ProjectId { get; set; }

    /// <summary>
    /// Additional Tags to associate with this Event
    /// </summary>
    public string[] Tags { get; set; } = [];
}

public enum MarginType
{
    ProducerPrice,
    PurchaserPrice
}

public sealed record class IndustryOutputEvent : Event
{
    public override string ImpactEventType => "IndustryOutput";

    /// <summary>
    /// Total output value of this Industry Output Event
    /// </summary>
    public required double? Output { get; set; }

    /// <summary>
    /// Total employment value
    /// </summary>
    public double? Employment { get; set; }

    /// <summary>
    /// Total employee compensation
    /// </summary>
    public double? EmployeeCompensation { get; set; }

    /// <summary>
    /// Total proprietor compensation
    /// </summary>
    public double? ProprietorIncome { get; set; }

    /// <summary>
    /// The Industry's Code (see <see cref="IndustryCodes"/>)
    /// </summary>
    public int IndustryCode { get; set; }

    /// <summary>
    ///  The Dataset Id (see <see cref="DataSets"/>)
    /// </summary>
    public int? DatasetId { get; set; }

    public MarginType? MarginType { get; set; }
    public double? Percentage { get; set; }
}

public record class IndustryEmploymentEvent : Event
{
    public double? Output { get; set; }
    public required double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryEmployment";
}

public record class IndustryEmployeeCompensationEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public required double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryEmployeeCompensation";
}

public record class IndustryProprietorIncomeEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public required double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryProprietorIncome";
}


public enum SpendingPatternValueType
{
    IntermediateExpenditure,
    Output
}

public sealed record class SpendingPatternCommodity
{
    public double? Coefficient { get; set; }
    public int CommodityCode { get; set; }
    public string CommodityDescription { get; set; }
    public bool IsSamValue { get; set; }
    public bool IsUserCoefficient { get; set; }
    public double LocalPurchasePercentage { get; set; } = 1.0d; // 100%
}

public sealed record class IndustryImpactAnalysisEvent : Event
{
    public required int IndustryCode { get; set; }
    public double? IntermediateInputs { get; set; }
    public double? TotalEmployment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public double? WageAndSalaryEmployment { get; set; }
    public double? ProprietorEmployment { get; set; }
    public double? TotalLaborIncome { get; set; }
    public double? OtherPropertyIncome { get; set; }
    public double? TaxOnProductionAndImports { get; set; }
    public double? LocalPurchasePercentage { get; set; } = 1.0;
    public double? TotalOutput { get; set; }
    public bool IsSam { get; set; }
    public int? SpendingPatternDatasetId { get; set; }
    public SpendingPatternValueType SpendingPatternValueType { get; set; }
    public SpendingPatternCommodity[] SpendingPatternCommodities { get; set; } = [];

    public override string ImpactEventType => "IndustryImpactAnalysis";
}

/// <summary>
/// Endpoints related to Impact Events
/// </summary>
public class Events
{
    public static string[] GetEventsTypes(Guid projectGuid)
    {
        var request = new RestRequest("api/v1/impact/project/{projectGuid}/eventtype");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        string? c = Rest.GetResponseContent(request);
        string[] response = Rest.GetResponseData<string[]>(request).ThrowIfNull();
        return response;
    }

    public static Event? GetEvent(Guid projectGuid, Guid eventGuid)
    {
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
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Event[]>(request).ThrowIfNull();
    }

    // Though there are 17? different Impact Event Types, there is technically only one endpoint to add them
    // They are split up here for clarity of input Model

    public static IndustryOutputEvent AddEvent(Guid projectGuid, IndustryOutputEvent industryOutputEvent)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(industryOutputEvent);

        return Rest.GetResponseData<IndustryOutputEvent>(request).ThrowIfNull();
    }
    
    public static IndustryImpactAnalysisEvent AddEvent(Guid projectGuid, IndustryImpactAnalysisEvent industryImpactAnalysisEvent)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(industryImpactAnalysisEvent);

        IndustryImpactAnalysisEvent @event = Rest.GetResponseData<IndustryImpactAnalysisEvent>(request).ThrowIfNull();
        return @event;
    }
}