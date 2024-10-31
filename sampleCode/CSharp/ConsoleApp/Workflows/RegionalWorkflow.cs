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

public class RegionalWorkflow : IWorkflow
{
    /// <summary>
    /// Regional Models can be searched for in a variety of ways.
    /// An Aggregation Scheme + Dataset must be chosen before filtering Regions
    /// </summary>
    public static void Examples()
    {
        /* Regions can be referenced by several identifiers (in order of most to least common):
         * HashId, Urid, ModelId, and UserModelId
         * All of which can be included in the returned Region Model
         * In the future, HashId is going to be the only supported Regional Identifier and currently is the most commonly used.
         */
        
        int aggregationSchemeId = 8;    // Implan 546 Unaggregated
        int dataSetId = 96;             // 2022
            
        // A RegionType is often an optional filter that can be applied to region lookups
        string[] regionTypes = RegionEndpoints.GetRegionTypes();
        /* Common Region Types:
         * `country`, `state`, `msa`, `county`, `Congressional District`, `zipcode`
         */
        
        // You can start with the Top-Level Region for a given AggregationScheme + DataSet
        // This is often just the Country that contains all further sub-regions
        Region topLevelRegion = RegionEndpoints.GetTopLevelRegion(aggregationSchemeId, dataSetId);
        
        // You can also dig into all the sub-regions (with optional RegionType filter)
        Region[] childRegions = RegionEndpoints.GetRegionChildren(aggregationSchemeId, dataSetId);

        // And also access your Combined + Customized Regions
        Region[] userRegions = RegionEndpoints.GetUserRegions(aggregationSchemeId, dataSetId);
        
        
        /* Search Regions Example
         * For this example, we're going to store all State Regions in a Dictionary / Map so that we can easily
         * look them up via their Name.
         */
        
        // Start by getting all Regions that have a RegionType of `State`
        Region[] regions = RegionEndpoints.GetRegionChildren(aggregationSchemeId, dataSetId, regionType: "State");
        
        // Convert to a dictionary (with case-insensitive keys)
        Dictionary<string, Region> descriptionToRegionDict = new Dictionary<string, Region>(StringComparer.OrdinalIgnoreCase);
        foreach (Region region in regions)
        {
            descriptionToRegionDict.Add(region.Description, region);
        }

        // Lookup a few states by their names
        Region ohio = descriptionToRegionDict["Ohio"];
        Region northCarolina = descriptionToRegionDict["North Carolina"];
    }
}
