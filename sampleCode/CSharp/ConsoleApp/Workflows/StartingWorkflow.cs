namespace ConsoleApp.Workflows;

public class StartingWorkflow : IWorkflow
{
    public static void Examples()
    {
/* To build a new Project, we need to start by with the Aggregation Scheme
 GET {{api_domain}}api/v1/aggregationschemes?industrySetId={{industrySetId}}
  */

        AggregationScheme[] aggSchemes = AggregationSchemes.GetAggregationSchemes();
// Note: the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries
        int aggregationSchemeId = 8;


/* Once you have chosen an Aggregation Scheme, you can use it to retrieve valid Data Sets
 */

        DataSet[] dataSets = DataSets.GetDataSets(8);
// Note: The 2022 DataSetId is 96
        int dataSetId = 87; //96;

// The householdsetid comes from the dataset?
// NO!< We take from agg scheme and verify in endpoint!


    }
}