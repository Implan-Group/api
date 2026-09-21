namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Event endpoints, including event types, specifications, and spending patterns.
/// </summary>
/// <remarks>
/// An Event is a change to an economy: an industry producing more, a household
/// earning more, a government spending. What an event needs depends on its type, so
/// the flow is usually: ask the Project which types it accepts, read any
/// specification codes that type needs, then create the event.
///
/// Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
/// </remarks>
public static class Events
{
    /// <summary>
    /// Lists the event types this Project accepts.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}/eventtype  (wiki: Get Event Types)
    ///
    /// The list depends on the Project's Aggregation Scheme. An international scheme
    /// accepts the international impact-analysis types and refuses the domestic
    /// ones, and the reverse. Reading this list is cheaper than discovering the rule
    /// from a 422.
    /// </remarks>
    public static List<string> GetEventTypes(ApiClient client, Guid projectId)
    {
        return client.GetJson<List<string>>($"/api/v1/impact/project/{projectId}/eventtype");
    }

    /// <summary>
    /// Lists the specification codes valid for one event type in this Project.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}/eventtype/{eventType}/specification
    /// (wiki: Get Event Specifications)
    ///
    /// Some event types take an industry code; others take a code from a fixed list.
    /// Household Income is the clearest example, where the codes are income brackets
    /// such as <c>10002 - Households 15-30k</c>.
    /// </remarks>
    public static List<Specification> GetEventSpecifications(
        ApiClient client,
        Guid projectId,
        string eventType)
    {
        return client.GetJson<List<Specification>>(
            $"/api/v1/impact/project/{projectId}/eventtype/{eventType}/specification");
    }

    /// <summary>
    /// Reads a default spending pattern and the commodities in it.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/{spendingPatternType}/{specificationCode}
    /// (wiki: Spending Pattern by Id)
    ///
    /// This is what you read, edit, and send back when you want an event to spend
    /// money through a supply chain you have adjusted. <c>Institution</c> patterns
    /// need a <paramref name="regionHashId"/>, because government and household
    /// spending varies by place. Omitting <paramref name="datasetId"/> uses the
    /// newest data year.
    /// </remarks>
    public static List<SpendingPatternCommodity> GetSpendingPattern(
        ApiClient client,
        int aggregationSchemeId,
        int specificationCode,
        SpendingPatternType patternType = SpendingPatternType.Industry,
        int? datasetId = null,
        string? regionHashId = null)
    {
        var query = new Query()
            .With("datasetId", datasetId)
            .With("regionHashId", regionHashId);

        var path = $"/api/v1/impact/spending-patterns/{aggregationSchemeId}"
                   + $"/{patternType}/{specificationCode}";

        // The shape varies a little by pattern type: some return the commodity array
        // directly, others wrap it. Read it as a document and take whichever it is.
        var text = client.GetText(path, query);
        using var document = JsonDocument.Parse(text);
        var root = document.RootElement;

        if (root.ValueKind == JsonValueKind.Array)
        {
            return JsonSerializer.Deserialize<List<SpendingPatternCommodity>>(text, Json.Options) ?? [];
        }

        foreach (var name in new[] { "commodities", "spendingPatternCommodities" })
        {
            if (root.TryGetProperty(name, out var array) && array.ValueKind == JsonValueKind.Array)
            {
                return JsonSerializer.Deserialize<List<SpendingPatternCommodity>>(
                    array.GetRawText(), Json.Options) ?? [];
            }
        }

        return [];
    }

    /// <summary>
    /// Adds an Event to a Project and returns it fully populated.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/project/{projectId}/event  (wiki: Create Event)
    ///
    /// Leave the id unset; it is generated and returned, and it is the id you
    /// reference from a Group. The response comes back with everything IMPLAN
    /// estimated from what you supplied, so re-assign rather than keeping the object
    /// you sent.
    ///
    /// A 400 means the event failed validation, usually a duplicate title or a field
    /// that does not belong to the type. A 422 means the type is not valid in this
    /// Project's Aggregation Scheme.
    /// </remarks>
    public static ImpactEvent CreateEvent(ApiClient client, Guid projectId, ImpactEvent impactEvent)
    {
        var text = client.PostText($"/api/v1/impact/project/{projectId}/event", impactEvent);
        using var document = JsonDocument.Parse(text);
        return EventFactory.FromJson(document.RootElement);
    }

    /// <summary>
    /// Lists every Event in a Project.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)
    ///
    /// The list mixes types, so each item is deserialized according to its own
    /// <c>impactEventType</c>.
    /// </remarks>
    public static List<ImpactEvent> GetEvents(ApiClient client, Guid projectId)
    {
        var text = client.GetText($"/api/v1/impact/project/{projectId}/event");
        using var document = JsonDocument.Parse(text);
        return EventFactory.ListFromJson(document.RootElement);
    }

    /// <summary>
    /// Reads one Event.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}/event/{eventId}  (wiki: Get Event)
    /// </remarks>
    public static ImpactEvent GetEvent(ApiClient client, Guid projectId, Guid eventId)
    {
        var text = client.GetText($"/api/v1/impact/project/{projectId}/event/{eventId}");
        using var document = JsonDocument.Parse(text);
        return EventFactory.FromJson(document.RootElement);
    }

    /// <summary>
    /// Removes an Event from a Project.
    /// </summary>
    /// <remarks>
    /// DELETE /api/v1/impact/project/{projectId}/event/{eventId}
    /// (wiki: Delete Event)
    /// </remarks>
    public static void DeleteEvent(ApiClient client, Guid projectId, Guid eventId)
    {
        client.Delete($"/api/v1/impact/project/{projectId}/event/{eventId}");
    }
}

