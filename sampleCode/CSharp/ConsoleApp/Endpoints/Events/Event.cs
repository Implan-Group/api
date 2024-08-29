namespace ConsoleApp.Endpoints.Events;

/// <summary>
/// The base class for all Events, the properties here are shared with all Impact Event Types
/// </summary>
public record class Event
{
    /// <summary>
    /// The specific Impact Event Type for this event. 
    /// </summary>
    public virtual string ImpactEventType => "Empty";

    /// <summary>
    /// Unique-per-Project description of this Event
    /// </summary>
    public required string Title { get; set; }

    /// <summary>
    /// Unique identifier for this Event
    /// </summary>
    public Guid Id { get; set; }

    /// <summary>
    /// Unique identifier for the Project this Event belongs to
    /// </summary>
    public Guid ProjectId { get; set; }

    /// <summary>
    /// Additional Tags to associate with this Event
    /// </summary>
    public string[] Tags { get; set; } = [];
}