namespace ConsoleApp.Endpoints.Events;

public record class IndustryProprietorIncomeEvent : Event
{
    public double? Output { get; set; }
    public double? Employment { get; set; }
    public double? EmployeeCompensation { get; set; }
    public required double? ProprietorIncome { get; set; }
    public int IndustryCode { get; set; }

    public override string ImpactEventType => "IndustryProprietorIncome";
}