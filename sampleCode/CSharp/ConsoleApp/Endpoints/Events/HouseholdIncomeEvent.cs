namespace ConsoleApp.Endpoints.Events;

public record class HouseholdIncomeEvent : Event
{
    public required int HouseholdIncomeCode { get; set; }
    public required double? Value { get; set; }

    public override string ImpactEventType => "HouseholdIncome";
}