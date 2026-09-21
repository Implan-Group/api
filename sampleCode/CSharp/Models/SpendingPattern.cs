namespace Implan.ApiSamples.Models;

/// <summary>
/// Which family of spending pattern to read.
/// </summary>
/// <remarks>
/// <c>Institution</c> patterns additionally require a region, because government
/// and household spending varies by where it happens.
/// </remarks>
public enum SpendingPatternType
{
    Industry,
    Institution,
    Custom,
    Household,
}

/// <summary>
/// One commodity within a spending pattern, and the share spent on it.
/// </summary>
/// <remarks>
/// A spending pattern is a list of commodities with the share of a dollar that goes
/// to each. IMPLAN supplies a default pattern for every industry and institution,
/// and you can read it, change individual coefficients, and send it back as part of
/// an event.
///
/// <see cref="Coefficient"/> is that share, from 0 to 1, and the coefficients
/// across a pattern sum to 1. Change one and set
/// <see cref="IsUserCoefficient"/> so IMPLAN knows the value is yours rather than
/// its own.
///
/// <see cref="LocalPurchasePercentage"/> is how much of this commodity is bought
/// inside the region. Leave it at 1.0 to assume everything is local, or set
/// <see cref="IsSamValue"/> to have IMPLAN substitute the region's own trade data,
/// which is usually the more defensible choice.
///
/// Wiki: Spending Patterns
/// https://github.com/Implan-Group/api/wiki/Spending-Patterns
/// </remarks>
public sealed class SpendingPatternCommodity
{
    public int CommodityCode { get; set; }
    public string CommodityDescription { get; set; } = string.Empty;
    public double? Coefficient { get; set; }
    public bool IsSamValue { get; set; }
    public bool IsUserCoefficient { get; set; }
    public double LocalPurchasePercentage { get; set; } = 1.0;

    /// <summary>One line naming the commodity and its share, for the console.</summary>
    public string Describe()
    {
        var share = Coefficient is null ? string.Empty : Coefficient.Value.ToString("F6");
        return $"{CommodityCode,5}  {share,10}  {CommodityDescription}";
    }
}
