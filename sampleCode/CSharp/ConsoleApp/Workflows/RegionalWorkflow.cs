namespace ConsoleApp.Workflows;

public class RegionalWorkflow : IWorkflow
{
    public static void Execute()
    {
        /* Region Information can be looked up in a variety of ways.
         * In order of common use: HashId, Urid, ModelId, and UserModelId can all be acquired through
         * these endpoints.
         * In the future, HashId is going to be the only supported Regional Identifier
         *
         * An AggregationSchemeId and DataSetId are both required to examine region information,
         * see AggregationSchemeWorkflow and DataSetWorkflow for further details.
         */
        int aggregationSchemeId = 8;    // Implan 546 Unaggregated
        int dataSetId = 96;             // 2022
            
        // A RegionType is often an optional filter that can be applied to region lookups
        string[] regionTypes = Regions.GetRegionTypes();
        
        // You can start with the Top-Level Region for a given AggregationScheme + DataSet
        // This is often just the Country that contains all further sub-regions
        Region topLevelRegion = Regions.GetTopLevelRegion(aggregationSchemeId, dataSetId);
        
        // You can also dig into all the sub-regions (with optional RegionType filter)
        Region[] childRegions = Regions.GetRegionChildren(aggregationSchemeId, dataSetId, regionType: "County");

        // And also access your Combined + Customized Regions
        Region[] userRegions = Regions.GetUserRegions(aggregationSchemeId, dataSetId);
    }
}