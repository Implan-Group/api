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

public sealed record class IndustrySet
{
    public int Id { get; set; }
    public string Description { get; set; }
    public int? DefaultAggregationSchemeId { get; set; }
    public bool? ActiveStatus { get; set; }
    public bool? IsDefault { get; set; }
    public int? MapTypeId { get; set; }
    public bool IsNaicsCompatible { get; set; }
}

public static class IndustrySetEndpoints
{
    public static IndustrySet? GetIndustrySet(int industrySetId)
    {
        RestRequest request = new RestRequest("api/v1/industry-sets/{industrySetId}");
        request.Method = Method.Get;
        request.AddUrlSegment("industrySetId", industrySetId);
        
        return Rest.GetResponseData<IndustrySet?>(request);
    }
    
    public static IndustrySet[] GetIndustrySets()
    {
        RestRequest request = new RestRequest("api/v1/industry-sets");
        request.Method = Method.Get;

        return Rest.GetResponseData<IndustrySet[]>(request).ThrowIfNull();
    }
}
