namespace ConsoleApp.Endpoints.Events;

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