namespace ConsoleApp.Endpoints.Events;

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

/// <summary>
/// Endpoints related to Impact Events
/// </summary>
public static class EventEndpoints
{
    public static string[] GetEventsTypes(Guid projectGuid)
    {
        var request = new RestRequest("api/v1/impact/project/{projectGuid}/eventtype");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        string? c = Rest.GetResponseContent(request);
        string[] response = Rest.GetResponseData<string[]>(request).ThrowIfNull();
        return response;
    }

    public static Event? GetEvent(Guid projectGuid, Guid eventGuid)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event/{eventGuid}");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);
        request.AddUrlSegment("eventGuid", eventGuid);

        return Rest.GetResponseData<Event>(request);
    }

    public static TEvent? GetEvent<TEvent>(Guid projectGuid, Guid eventGuid)
        where TEvent : Event
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event/{eventGuid}");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);
        request.AddUrlSegment("eventGuid", eventGuid);
        return Rest.GetResponseData<TEvent>(request);
    }

    public static Event[] GetEvents(Guid projectGuid)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectGuid}/event");
        request.Method = Method.Get;
        request.AddUrlSegment("projectGuid", projectGuid);

        return Rest.GetResponseData<Event[]>(request).ThrowIfNull();
    }

    
    // Though there are 17? different Impact Event Types, there is technically only one endpoint to add them
    // They are split up here for clarity of input Model

    public static IndustryOutputEvent AddEvent(Guid projectGuid, IndustryOutputEvent industryOutputEvent)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(industryOutputEvent);

        return Rest.GetResponseData<IndustryOutputEvent>(request).ThrowIfNull();
    }
    
    public static IndustryImpactAnalysisEvent AddEvent(Guid projectGuid, IndustryImpactAnalysisEvent industryImpactAnalysisEvent)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(industryImpactAnalysisEvent);

        IndustryImpactAnalysisEvent @event = Rest.GetResponseData<IndustryImpactAnalysisEvent>(request).ThrowIfNull();
        return @event;
    }
    
    public static HouseholdIncomeEvent AddEvent(Guid projectGuid, HouseholdIncomeEvent householdIncomeEvent)
    {
        RestRequest request = new RestRequest("api/v1/impact/project/{projectId}/event");
        request.Method = Method.Post;
        request.AddUrlSegment("projectId", projectGuid);
        request.AddJsonBody(householdIncomeEvent);

        HouseholdIncomeEvent @event = Rest.GetResponseData<HouseholdIncomeEvent>(request).ThrowIfNull();
        return @event;
    }
}
