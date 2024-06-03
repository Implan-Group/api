namespace ConsoleApp.Endpoints;

public static class ImpactResults
{
    public static dynamic GetImpactTotals(long impactRunId)
    {
        // GET {{api_domain}}api/v1/impact/results/{{runId}}
        var request = new RestRequest("api/v1/impact/results/{impactRunId}");
        request.Method = Method.Get;
        request.AddUrlSegment("impactRunId", impactRunId);

        var response = Rest.GetResponse(request);
        
        Debugger.Break();
        throw new NotImplementedException();
    }

    /// <summary>
    /// These reports return csv-formatted data!
    /// </summary>
    public static class CsvReports
    {
        public static string GetDetailedEconomicIndicators(long impactRunId)
        {
            //  [HttpGet("external/api/v1/impact/results/ExportDetailEconomicIndicators/{runId}")]
            var request = new RestRequest("api/v1/impact/results/ExportDetailEconomicIndicators/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            return Rest.GetResponseContent(request).ThrowIfNull();
        }
        
        public static string GetSummaryEconomicIndicators(long impactRunId)
        {
            //[HttpGet("external/api/v1/impact/results/SummaryEconomicIndicators/{runId}")]
            var request = new RestRequest("api/v1/impact/results/SummaryEconomicIndicators/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            return Rest.GetResponseContent(request).ThrowIfNull();
        }

        public static string GetDetailedTaxes(long impactRunId)
        {
            //[HttpGet("external/api/v1/impact/results/DetailedTaxes/{runId}")]
            var request = new RestRequest("api/v1/impact/results/DetailedTaxes/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            return Rest.GetResponseContent(request).ThrowIfNull();
        }
        
        public static string GetSummaryTaxes(long impactRunId)
        {
            // [HttpGet("external/api/v1/impact/results/SummaryTaxes/{runId}")]
            var request = new RestRequest("api/v1/impact/results/SummaryTaxes/{impactRunId}");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);

            return Rest.GetResponseContent(request).ThrowIfNull();
        }


        public static string GetEstimatedGrowthPercentage(long impactRunId)
        {
            //    [HttpGet("external/api/v1/impact/results/estimated-growth-percentage/{runId}")]
            var request = new RestRequest("api/v1/impact/results/EstimatedGrowthPercentage/{impactRunId}");
            // request.AddHeader("accept", "text/csv");
            // request.AddHeader("content-type", "text/csv");
            request.Method = Method.Get;
            request.AddUrlSegment("impactRunId", impactRunId);
            //request.

            var data = Rest.GetResponse(request);
            Debugger.Break();

            throw new NotImplementedException();
        }
    }
}