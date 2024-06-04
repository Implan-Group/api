namespace ConsoleApp.Workflows;

public class CombinedRegionWorkflow : IWorkflow
{
    public static void Examples()
    {
        // See the RegionalWorkflow Examples for various ways to search Regions in order to find the HashId(s)
        // We also require the Aggregation Scheme Id for those regions
        RegionalWorkflow.Examples();

        int aggregationSchemeId = 8;        // Default
        
        /* Combine Regions */

        string hashId_1 = "W1aQl9wzxj";     // Lane County, OR
        string hashId_2 = "Rgxp4eA3xK";     // Douglas County, OR
        
        // Create the request payload
        // Note: Specify either HashIds or Urids, not both
        CombineRegionRequest combineRegionPayload = new CombineRegionRequest()
        {
            // The description for this Combined Region must be Unique
            Description = $"Workflow - Combine Regions - {Guid.NewGuid()}",
            HashIds = [hashId_1, hashId_2],
        };
        
        // Send the request to be build
        var result = Regions.CombineRegions(aggregationSchemeId, combineRegionPayload);
        
        // It may take a while for a Region to build (especially for more complex ones)
        // To wait for this, you can use a small polling loop:
        do
        {
            // Get the current status by getting the region again
            Region region = Regions.GetRegion(result.AggregationSchemeId, result.DatasetId, result.HashId);

            // New, Complete, Error
            // If it is 'Complete' the model build is done
            if (string.Equals(region.ModelBuildStatus, "Complete", StringComparison.OrdinalIgnoreCase))
                break;

            // Give the build 30 more seconds to process
            Thread.Sleep(TimeSpan.FromSeconds(30));
        } while (true);
        
        // Now that the Regions have been Combined, you have the HashId of the combined region
        CreateProjectWorkflow.Examples();   // <- How to create a Project with Events, Groups, and Regions
    }
}