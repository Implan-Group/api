namespace ConsoleApp.Workflows;

public class CombinedRegionWorkflow : IWorkflow
{
    /// <summary>
    /// This Example Workflow follows along with `api\impact\workflows\CombineRegions.md`
    /// </summary>
    public static void Examples()
    {
        /* Not all economic models are built for Regions by default, or sometimes you may want to combine regions.
         * Combining regions is used to create a custom group of counties, ZIP codes, MSAs, and/or states and 
         * treat them as one economic region that can be studied.
         */
        
        
        // To find Regions to combine, first you must have an Aggregation Scheme and a Dataset
        
        
        // Get a list of all valid Aggregation Schemes
        var aggregationSchemes = AggregationSchemes.GetAggregationSchemes();
        // Choose the one you would like to use
        int aggregationSchemeId = 8; // 8 = Implan 546 Unaggregated
        
        
        // Get a list of all valid Data Sets for the Aggregation Scheme
        var datasets = DataSets.GetDataSets(aggregationSchemeId);
        // Choose the one you would like to use -- must be compatible with your chosen HouseholdSetId
        int dataSetId = 96; // 96 = 2022 Data
        
        
        /* Now that you have an Aggregation Scheme + Dataset picked out, there are various ways that Regions
         * can be explored
         */
        
        // See these examples for ways to find Region(s) -- You will require an Aggregation Scheme Id and Dataset Id
        RegionalWorkflow.Examples();
        
        
        /* Combine Regions
         * Once you have found the HashIds of the Regions you wish to combine (using the endpoints above),
         * you can combine them together into a single Region         
         */

        // These examples are from Aggregation Scheme 8, DataSet 96
        string hashId1 = "W1aQl9wzxj";     // Lane County, OR
        string hashId2 = "Rgxp4eA3xK";     // Douglas County, OR
        
        // Create the request payload
        // Note: Specify either HashIds or Urids, not both
        CombineRegionRequest combineRegionPayload = new CombineRegionRequest()
        {
            // The description for this Combined Region must be Unique
            Description = $"Workflow - Combine Regions - {Guid.NewGuid()}",
            HashIds = [hashId1, hashId2],
            //Urids = [1857994,1857642],
        };
        
        // Send the combine region request
        Region combinedRegion = Regions.CombineRegions(aggregationSchemeId, combineRegionPayload);
       
        
        /* Complicated and numerous Regions may take a while to fully process (Build) in our system
         * The `ModelBuildStatus` property on the returned Region will indicate whether that build
         * has completed.
         *
         * You can use a polling loop to wait for that completion:
         */
        do
        {
            // Get the Region's information again
            
            // TODO: This endpoint does not yet exist
            //var region = Regions.GetRegion(
            //    combinedRegion.AggregationSchemeId,
            //    combinedRegion.DatasetId,
            //    combinedRegion.HashId);
            
            // Get a list of all User Regions (which includes Customized + Combined)
            var userRegions = Regions.GetUserRegions(combinedRegion.AggregationSchemeId, combinedRegion.DatasetId);
            // Find the one that has a matching HashId
            var region = userRegions.FirstOrDefault(r => r.HashId == combinedRegion.HashId);
            
            // Check the status -- if it is `Complete`, the Build is done
            if (string.Equals(region?.ModelBuildStatus, "Complete", StringComparison.OrdinalIgnoreCase))
                break;
            
            // Otherwise, wait a little bit and try again
            Thread.Sleep(TimeSpan.FromSeconds(30));
            
        } while (true);
        
        
        /* Once the ModelBuildStatus is `complete`, the Region is ready to use */
    }
}