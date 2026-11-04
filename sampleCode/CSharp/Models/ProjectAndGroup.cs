namespace Implan.ApiSamples.Models;

/// <summary>
/// One impact analysis project.
/// </summary>
/// <remarks>
/// A Project is the container for one analysis. It fixes the Aggregation Scheme and
/// Household Set at creation, and everything inside it has to be consistent with
/// that choice.
///
/// Leave <see cref="Id"/> unset when creating; the API generates it and returns it.
/// <see cref="Title"/> must be unique for your account and must avoid an ampersand
/// and the characters <c>| ; % * ? ! = ' " ^ #</c>.
///
/// <see cref="LastImpactRunId"/> is filled in after the project has been run, and
/// is the run whose results you read.
///
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// </remarks>
public sealed class Project
{
    public string Title { get; set; } = string.Empty;
    public int AggregationSchemeId { get; set; }
    public int HouseholdSetId { get; set; }
    public Guid? Id { get; set; }

    /// <summary>
    /// Multi-regional input-output analysis, which traces effects between the
    /// project's regions instead of treating each in isolation. See the MrioProject
    /// workflow.
    /// </summary>
    public bool IsMrio { get; set; }

    /// <summary>The folder this project sits in, or null for the top level.</summary>
    public int? FolderId { get; set; }

    public long? LastImpactRunId { get; set; }

    [JsonExtensionData]
    public Dictionary<string, JsonElement> Extra { get; set; } = [];

    /// <summary>One line naming the project, for the console.</summary>
    public string Describe() => $"{Title}  id={Id}";
}

/// <summary>
/// A folder in IMPLAN Cloud, used to keep a batch of projects together.
/// </summary>
/// <remarks>
/// Note the type of <see cref="Id"/>. A folder reports its own id as a string,
/// while <see cref="Project.FolderId"/> and a folder's own <see cref="ParentId"/>
/// refer to the same value as an integer. The string is canonical, so
/// <see cref="FolderIdForProject"/> does the conversion in one place rather than
/// leaving it to every caller.
/// </remarks>
public sealed class Folder
{
    public string Title { get; set; } = string.Empty;
    public string? Id { get; set; }
    public int? ParentId { get; set; }

    /// <summary>This folder's id in the integer form a Project expects.</summary>
    [JsonIgnore]
    public int? FolderIdForProject =>
        int.TryParse(Id, out var parsed) ? parsed : null;
}

/// <summary>
/// The link between a Group and one of the Project's Events.
/// </summary>
/// <remarks>
/// <see cref="ScalingFactor"/> multiplies the event's values inside this group. It
/// is a multiplier and not a percentage: 1 leaves the event alone, 0.55 more than
/// halves it, and 5000 analyzes it five thousand times over. Two decimal places are
/// kept.
///
/// Group and event scaling compound, so an event scaled 3000 inside a group scaled
/// 5 is analyzed at 15000. Scale at one level or the other, not both. To leave an
/// event out of a group, remove it rather than scaling it to zero.
/// </remarks>
public sealed class GroupEvent
{
    public Guid EventId { get; set; }
    public double ScalingFactor { get; set; } = 1.0;
}

/// <summary>
/// One region and dollar year, with the events that apply to it.
/// </summary>
/// <remarks>
/// An Event says what changed. A Group pairs one region and one dollar year with
/// the events that apply there. Running the same events in three states means three
/// groups, which is the MultiEventToMultiGroup workflow.
///
/// Supply exactly one region identifier: <see cref="HashId"/>, <see cref="Urid"/>,
/// <see cref="UserModelId"/>, or <see cref="ModelId"/>. HashId is the one to use.
///
/// <see cref="DollarYear"/> has no server-side default, and a group saved without
/// one produces an impact run that never attaches, so always set it. The samples
/// use the current calendar year.
///
/// Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
/// </remarks>
public sealed class Group
{
    public string Title { get; set; } = string.Empty;
    public Guid? Id { get; set; }
    public Guid? ProjectId { get; set; }

    // Exactly one of these four identifies the region. HashId is preferred.
    public string? HashId { get; set; }
    public long? Urid { get; set; }
    public int? UserModelId { get; set; }
    public int? ModelId { get; set; }

    public int? DollarYear { get; set; }
    public int? DatasetId { get; set; }
    public double ScalingFactor { get; set; } = 1.0;

    public List<GroupEvent> GroupEvents { get; set; } = [];

    [JsonExtensionData]
    public Dictionary<string, JsonElement> Extra { get; set; } = [];

    /// <summary>One line naming the group, for the console.</summary>
    public string Describe() =>
        $"{Title}  id={Id}  hashId={HashId}  events={GroupEvents.Count}";
}
