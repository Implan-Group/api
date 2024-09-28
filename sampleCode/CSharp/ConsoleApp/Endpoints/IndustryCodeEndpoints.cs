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

public sealed record class IndustryCode
{
    public int Id { get; set; }
    public int Code { get; set; }
    public string Description { get; set; }
}

public static class IndustryCodeEndpoints
{
    public static IndustryCode[] GetIndustryCodes(int? aggregationSchemeId = null, int? industrySetId = null)
    {
        RestRequest request;
        
        // There are different routes depending on whether or not we have an Aggregation Scheme
        if (aggregationSchemeId is null)
        {
            request = new RestRequest("api/v1/IndustryCodes");
        }
        else
        {
            request = new RestRequest("api/v1/IndustryCodes/{aggregationSchemeId}");
            request.AddUrlSegment("aggregationSchemeId", aggregationSchemeId.Value);
        }

        if (industrySetId is not null)
        {
            request.AddParameter("industrySetId", industrySetId.Value);
        }

        return Rest.GetResponseData<IndustryCode[]>(request).ThrowIfNull();
    }
}
