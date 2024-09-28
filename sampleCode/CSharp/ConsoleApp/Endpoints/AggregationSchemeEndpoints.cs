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

public sealed record class AggregationScheme
{
    public int Id { get; set; }
    public string Description { get; set; }
    public int IndustrySetId { get; set; }
    public int[] HouseholdSetIds { get; set; }
    public string MapCode { get; set; }
    public string Status { get; set; }
}

/// <remarks>the default Aggregation Scheme ID is 8: Unaggregated 546 Industries</remarks>
public static class AggregationSchemeEndpoints
{
    public static AggregationScheme[] GetAggregationSchemes(int? industrySetId = null)
    {
        //GET {api_domain}api/v1/aggregationschemes?industrySetId={industrySetId}
        RestRequest request = new RestRequest("api/v1/aggregationSchemes");
        request.Method = Method.Get;
        if (industrySetId is not null)
        {
            request.AddParameter("industrySetId", industrySetId.Value);
        }
        
        return Rest.GetResponseData<AggregationScheme[]>(request);
    }
}
