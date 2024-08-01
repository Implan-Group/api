namespace ConsoleApp.Endpoints.Events;

public sealed record class SpendingPatternCommodity
{
    public double? Coefficient { get; set; }
    public int CommodityCode { get; set; }
    public string CommodityDescription { get; set; }
    public bool IsSamValue { get; set; }
    public bool IsUserCoefficient { get; set; }
    public double LocalPurchasePercentage { get; set; } = 1.0d; // 100%
}