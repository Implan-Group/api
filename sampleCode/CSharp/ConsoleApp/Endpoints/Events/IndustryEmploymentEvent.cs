namespace ConsoleApp.Endpoints.Events;

public record class IndustryEmploymentEvent : Event
{
    public double? Output { get; set; }
    public required double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryEmployment";
}