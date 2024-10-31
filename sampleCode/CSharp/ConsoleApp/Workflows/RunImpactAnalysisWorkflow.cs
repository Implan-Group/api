namespace ConsoleApp.Workflows;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

/// <summary>
/// This Example Workflow follows along with `api\impact\workflows\RunImpactAnalysis.md`
/// </summary>
public class RunImpactAnalysisWorkflow : IWorkflow
{
    /// <summary>
    /// This Project ID will be used to lookup Projects and their Impact Run Results
    /// </summary>
    public static Guid ProjectId { get; set; } = Guid.Empty;
    
    public static void Examples()
    {
        /* Once a Project has been created and Events and Groups have been added,
         * the Impact Analysis can be run in order to produce results
         */

        /* In order to run an Impact, you first need to find the Project
         * There are several ways to search through all the Projects that your User has access to
         * You're looking for the Project's Id -- a unique Guid to reference the Project
         * or the LastImpactRunId, used to lookup the results
         */
        
        // If you want to look at all Projects that you created
        Project[] projects = ProjectEndpoints.GetProjects();
        
        // If you want to look at all Projects that have been shared with you
        Project[] shared = ProjectEndpoints.GetSharedProjects();
        
        // If you want the details for a specific Project you need the Project Id
        Project project = ProjectEndpoints.GetProject(ProjectId);
        
        // Once you have located the Project Id for the Project you can run an Analysis on that Project
        long impactRunId = ImpactEndpoints.RunImpact(ProjectId);
        
        /* Once you have the Impact Run Id, you can query the system to see when it completes
         * Since this can take a while, it is recommended to create a polling loop to check the status every few minutes until it returns `Complete`
         */
        while (true)
        {
            // Get the current status
            string status = ImpactEndpoints.GetImpactStatus(impactRunId);

            // If it is 'Complete', then results can be queried
            if (string.Equals(status, "\"Complete\"", StringComparison.OrdinalIgnoreCase))
                break;

            // If it has not yet completed, give it more time to process
            Thread.Sleep(TimeSpan.FromSeconds(10));
        }
        
        /* If the Impact seems to be taking an unusually long time to run or you want to make changes, you can also Cancel a running Impact Analysis
        bool cancelled = Impacts.CancelImpact(impactRunId: 00000);
        */
        
        
        // Once the `status` of an Impact Run is `Complete`, the results of that Impact can be retrieved
        // Some of the Reports return CSV data, simply save the returned text into a file with the .csv extension
        // and open with Excel / Sheets
        
        // Reports about Economic Indicators
        string detailedEconomicIndicators = ImpactResultEndpoints.CsvReports.GetDetailedEconomicIndicators(impactRunId);
        string summaryEconomicIndicators = ImpactResultEndpoints.CsvReports.GetSummaryEconomicIndicators(impactRunId);
        
        // Reports about Taxes
        string detailedTaxes = ImpactResultEndpoints.CsvReports.GetDetailedTaxes(impactRunId);
        string summaryTaxes = ImpactResultEndpoints.CsvReports.GetSummaryTaxes(impactRunId);
        
        // For Estimated Growth Percentage, we need to specify additional filters
        ImpactResultEndpoints.CsvReports.EstimatedGrowthPercentageFilter estimatedGrowthPercentageFilter = new()
        {
            // Dollar Year always has to be specified, the other properties are optional
            DollarYear = 2024,
        };
        string estimatedGrowthPercentage = ImpactResultEndpoints.CsvReports.GetEstimatedGrowthPercentage(impactRunId, estimatedGrowthPercentageFilter);

        
        /* There are many other types of Reports and Results to retrieve, see the
         * main Impact Readme at https://github.com/Implan-Group/api/blob/main/impact/readme.md
         * for more information
         */
        return;
    }
}
