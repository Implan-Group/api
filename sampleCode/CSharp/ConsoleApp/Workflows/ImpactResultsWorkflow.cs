namespace ConsoleApp.Workflows;

public class ImpactResultsWorkflow : IWorkflow
{
    public static void Execute()
    {
        /* Once the Impact has finished, there are many ways to access its results  */
        long impactRunId = 12241;

        //var impactTotals = Results.GetImpactTotals(impactRunId);
        var dei = ImpactResults.CsvReports.GetDetailedEconomicIndicators(impactRunId);
        var sei = ImpactResults.CsvReports.GetSummaryEconomicIndicators(impactRunId);

        var dt = ImpactResults.CsvReports.GetDetailedTaxes(impactRunId);
        var st = ImpactResults.CsvReports.GetSummaryTaxes(impactRunId);

        var egp = ImpactResults.CsvReports.GetEstimatedGrowthPercentage(impactRunId);
        
        Debugger.Break();
    }
}