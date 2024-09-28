using ConsoleApp.Regions;

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
        AggregationScheme[] aggregationSchemes = AggregationSchemeEndpoints.GetAggregationSchemes();
        // Choose the one you would like to use
        int aggregationSchemeId = 8; // 8 = Implan 546 Unaggregated
        
        
        // Get a list of all valid Data Sets for the Aggregation Scheme
        DataSet[] datasets = DataSetEndpoints.GetDataSets(aggregationSchemeId);
        // Choose the one you would like to use -- must be compatible with your chosen HouseholdSetId
        int dataSetId = 96; // 96 = 2022 Data
        
        
        /* Now that you have an Aggregation Scheme + Dataset picked out, there are various ways that Regions
         * can be explored
         */
        // See these examples for ways to find Region(s) -- You will require an Aggregation Scheme Id and Dataset Id
        RegionalWorkflow.Examples();
        
        // For this example, we're going to search through the Child Regions of the US for a few particular counties.
        Region[] regions = RegionEndpoints.GetRegionChildren(aggregationSchemeId, dataSetId, regionType: "County");
        // Convert to a dictionary so that we can quickly search by Description
        Dictionary<string, Region> descriptionToRegionDict = new Dictionary<string, Region>(StringComparer.OrdinalIgnoreCase);
        foreach (Region region in regions)
        {
            descriptionToRegionDict.Add(region.Description, region);
        }

        // Find the HashId for the first county we want to combine
        string hashId1 = descriptionToRegionDict["Lane County, OR"].HashId;     // W1aQl9wzxj
        // Find the other HashId
        string hashId2 = descriptionToRegionDict["Douglas County, OR"].HashId;  // Rgxp4eA3xK
        
        
        /* Combine Regions
         * Once you have found the HashIds of the Regions you wish to combine (using the endpoints above),
         * you can combine them together into a single Region         
         */
        
        // Create the request payload
        // Note: Specify either HashIds or Urids, not both
        CombineRegionRequest combineRegionPayload = new CombineRegionRequest()
        {
            // Region Description must be unique and can only contain alphanumeric characters and spaces
            Description = $"Combined Region - {DateTime.Now:yyyyMMdd_HHmmss}",
            HashIds = [hashId1, hashId2],
            //Urids = [1857994,1857642],
        };
        
        // Send the combine region request
        Region combinedRegion = RegionEndpoints.CombineRegions(aggregationSchemeId, combineRegionPayload);
       
        
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
            Region[] userRegions = RegionEndpoints.GetUserRegions(combinedRegion.AggregationSchemeId, combinedRegion.DatasetId);
            // Find the one that has a matching HashId
            Region? region = userRegions.FirstOrDefault(r => r.HashId == combinedRegion.HashId);
            
            // Check the status -- if it is `Complete`, the Build is done
            if (string.Equals(region?.ModelBuildStatus, "Complete", StringComparison.OrdinalIgnoreCase))
                break;
            
            // Otherwise, wait a little bit and try again
            Thread.Sleep(TimeSpan.FromSeconds(30));
            
        } while (true);
        
        
        /* Once the ModelBuildStatus is `complete`, the Region is ready to use */
    }
}
