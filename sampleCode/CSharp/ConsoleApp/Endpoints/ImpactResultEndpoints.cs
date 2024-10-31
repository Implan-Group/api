namespace ConsoleApp.Endpoints;

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
