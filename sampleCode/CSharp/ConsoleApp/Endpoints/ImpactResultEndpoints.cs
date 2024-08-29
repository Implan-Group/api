namespace ConsoleApp.Endpoints;

public enum ImpactType
{
    Direct = 1,
    Indirect = 2,
    Induced = 3        
}

public static class ImpactResultEndpoints
{
    /// <summary>
    /// These reports return csv-formatted data!
    /// To open them, save the results in a file with a `.csv` extension and open with Excel or Sheets
    /// </summary>
    public static class CsvReports
    {
        public static string GetDetailedEconomicIndicators(long impactRunId)
        {
            RestRequest request = new RestRequest("api/v1/impact/results/ExportDetailEconomicIndicators/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            string csv = Rest.GetResponseContent(request).ThrowIfNull();
            return csv;
        }
        
        public static string GetSummaryEconomicIndicators(long impactRunId)
        {
            RestRequest request = new RestRequest("api/v1/impact/results/SummaryEconomicIndicators/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            string csv = Rest.GetResponseContent(request).ThrowIfNull();
            return csv;
        }

        public static string GetDetailedTaxes(long impactRunId)
        {
            RestRequest request = new RestRequest("api/v1/impact/results/DetailedTaxes/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            string csv = Rest.GetResponseContent(request).ThrowIfNull();
            return csv;
        }
        
        public static string GetSummaryTaxes(long impactRunId)
        {
            RestRequest request = new RestRequest("api/v1/impact/results/SummaryTaxes/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            string csv = Rest.GetResponseContent(request).ThrowIfNull();
            return csv;
        }

      
        public class EstimatedGrowthPercentageFilter
        {
            public required int DollarYear { get; set; }

            public string[] Regions { get; set; } = [];
            public ImpactType[] Impacts { get; set; } = [];
            public string[] GroupNames { get; set; } = [];
            public string[] EventNames { get; set; } = [];
            public string[] EventTags { get; set; } = [];
        }

        public static string GetEstimatedGrowthPercentage(long impactRunId, EstimatedGrowthPercentageFilter filter)
        {
            RestRequest request = new RestRequest("api/v1/impact/results/EstimatedGrowthPercentage/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);
            request.AddJsonBody(filter);

            string csv = Rest.GetResponseContent(request).ThrowIfNull();
            return csv;
        }
    }
}