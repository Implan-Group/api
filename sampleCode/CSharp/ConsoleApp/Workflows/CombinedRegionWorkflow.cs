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

        // These are from Aggregation Scheme 8, DataSet 96
        string hashId_1 = "W1aQl9wzxj";     // Lane County, OR      URID:1857994
        string hashId_2 = "Rgxp4eA3xK";     // Douglas County, OR   URID:1857642
        
        // Create the request payload
        // Note: Specify either HashIds or Urids, not both
        CombineRegionRequest combineRegionPayload = new CombineRegionRequest()
        {
            // The description for this Combined Region must be Unique
            Description = $"Workflow - Combine Regions - {Guid.NewGuid()}",
            HashIds = [hashId_1, hashId_2],
            //Urids = [1857994,1857642],
        };
        
        // Send the request to be build
        Region combinedRegion = Regions.CombineRegions(aggregationSchemeId, combineRegionPayload);
       
        // It may take a while for a Region to build (especially for more complex ones)
        // To wait for this, you can use a small polling loop:
        do
        {
            // Find the user model being built
            var userRegions = Regions.GetUserRegions(combinedRegion.AggregationSchemeId, combinedRegion.DatasetId);
            var userRegion = userRegions.FirstOrDefault(r => r.HashId == combinedRegion.HashId);
            string? status = userRegion?.ModelBuildStatus;
            
            // New, Complete, Error
            // If it is 'Complete' the model build is done
            if (string.Equals(status, "Complete", StringComparison.OrdinalIgnoreCase))
                break;

            // Give the build 30 more seconds to process
            Thread.Sleep(TimeSpan.FromSeconds(30));
        } while (true);
        
        // Now that the Regions have been Combined, you have the HashId of the combined region
        CreateProjectWorkflow.Examples();   // <- How to create a Project with Events, Groups, and Regions
    }
}