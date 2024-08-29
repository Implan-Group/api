namespace ConsoleApp.Endpoints.Events;

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
    /// The Industry's Code (see <see cref="IndustryCodeEndpoints"/>)
    /// </summary>
    public int IndustryCode { get; set; }

    /// <summary>
    ///  The Dataset Id (see <see cref="DataSetEndpoints"/>)
    /// </summary>
    public int? DatasetId { get; set; }

    public MarginType? MarginType { get; set; }
    public double? Percentage { get; set; }
}