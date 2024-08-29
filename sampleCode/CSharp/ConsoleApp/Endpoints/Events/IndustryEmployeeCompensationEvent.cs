namespace ConsoleApp.Endpoints.Events;

public record class IndustryEmployeeCompensationEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public required double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryEmployeeCompensation";
}