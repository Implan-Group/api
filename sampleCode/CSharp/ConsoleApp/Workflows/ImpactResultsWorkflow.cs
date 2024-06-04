namespace ConsoleApp.Workflows;

public class ImpactResultsWorkflow : IWorkflow
{
    public static void Execute()
    {
        /* Once the Impact has been started you will have the Impact Run Id needed to pull results
         */
        long impactRunId = 12241;
        
        // In order to pull any results, the Impact must have been completed successfully
        // To wait for this, you can use a small polling loop:
        do
        {
            // Get the current status
            string status = Impacts.GetImpactStatus(impactRunId);

            // If it is 'Complete', then results can be queried
            if (string.Equals(status, "Complete", StringComparison.OrdinalIgnoreCase))
                break;

            // Give the impact 30 more seconds to process
            Thread.Sleep(TimeSpan.FromSeconds(30));
        } while (true);

        
        // Once you know the Impact has Completed, you can pull reports on that information in several formats.
        
        // CSV Exports (you'd want to save the results of these endpoints into a file with a `.csv` extension
        // and open them in Excel / Google Sheets
       
        var detailedEconomicIndicators = ImpactResults.CsvReports.GetDetailedEconomicIndicators(impactRunId);
        var summaryEconomicIndicators = ImpactResults.CsvReports.GetSummaryEconomicIndicators(impactRunId);
        
        var detailedTaxes = ImpactResults.CsvReports.GetDetailedTaxes(impactRunId);
        var summaryTaxes = ImpactResults.CsvReports.GetSummaryTaxes(impactRunId);

        // For Estimated Growth Percentage, we need to specify additional filters
        var estimatedGrowthPercentageFilter = new ImpactResults.CsvReports.EstimatedGrowthPercentageFilter()
        {
            // Dollar Year always has to be specified, the other properties are optional
            DollarYear = 2024,
        };
        var estimatedGrowthPercentage = ImpactResults.CsvReports.GetEstimatedGrowthPercentage(impactRunId, estimatedGrowthPercentageFilter);
        
        
        Debugger.Break();
    }
}