namespace ConsoleApp.Workflows;

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
        string[] regionTypes = Regions.GetRegionTypes();
        /* Common Region Types:
         * `country`, `state`, `msa`, `county`, `Congressional District`, `zipcode`
         */
        
        // You can start with the Top-Level Region for a given AggregationScheme + DataSet
        // This is often just the Country that contains all further sub-regions
        Region topLevelRegion = Regions.GetTopLevelRegion(aggregationSchemeId, dataSetId);
        
        // You can also dig into all the sub-regions (with optional RegionType filter)
        Region[] childRegions = Regions.GetRegionChildren(aggregationSchemeId, dataSetId, regionType: "County");

        // And also access your Combined + Customized Regions
        Region[] userRegions = Regions.GetUserRegions(aggregationSchemeId, dataSetId);
    }
}