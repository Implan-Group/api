using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 10: ImportEvents.
/// </summary>
/// <remarks>
/// Goal: fill a project from the official IMPLAN Event Template workbook.
///
/// Most analysts already keep their events in a spreadsheet. IMPLAN publishes an
/// Event Template for exactly that, and the same file the Upload Template button
/// takes in IMPLAN Cloud can be posted to the API. One upload can create events,
/// groups, and the assignments between them, which is a lot less code than one call
/// per event.
///
/// The template is strict, and the rules are worth knowing before you fill one in:
///
///   - Use the template that matches your Project's Industry Set. There is one for
///     US 528, US 546, Canada 235, Canada 236, and International, and they are not
///     interchangeable.
///   - Each event type has its own sheet, and the sheet has to be the right one.
///   - Formats matter. A cell the blank template shows as <c>100%</c> means
///     <c>100%</c>, not <c>100</c>.
///   - Do not leave an event with no value, and do not leave a formula in a cell.
///   - Keep an import to about 500 events.
///
/// A rejected template answers 400 with the validation detail, which is the useful
/// part: it names what to fix.
///
/// Wiki: Import Events - https://github.com/Implan-Group/api/wiki/Import-Events
/// Support: Using the Event Template
/// https://support.implan.com/hc/en-us/articles/360040713754
/// </remarks>
public static class ImportEventsWorkflow
{
    /// <summary>
    /// Where to download the blank templates, by Industry Set.
    /// </summary>
    private static readonly (string Name, string Url)[] BlankTemplates =
    [
        ("US 528", "https://support.implan.com/hc/article_attachments/31846310653723"),
        ("US 546", "https://support.implan.com/hc/article_attachments/28726382924059"),
        ("Canada 235", "https://support.implan.com/hc/article_attachments/34805745157147"),
        ("Canada 236", "https://support.implan.com/hc/article_attachments/49510601287323"),
        ("International", "https://support.implan.com/hc/article_attachments/28726664391451"),
    ];

    public static Project Run(string? workbookPath = null)
    {
        // The filled template to upload. It is not shipped, because a valid workbook
        // has to be made from IMPLAN's own blank template rather than generated.
        var path = workbookPath ?? Path.Combine(Config.DataDirectory, "event_template.xlsx");

        // Step 1. Check the input before doing anything that creates an account object.
        ConsoleLog.Heading("Step 1: find the filled Event Template");
        RequireWorkbook(path);
        ConsoleLog.Info("  {0} ({1} KB)", path, new FileInfo(path).Length / 1024);

        var client = Auth.CreateClient();

        // Step 2. Resolve identifiers. The template family has to match the Industry
        // Set this project ends up on, so the resolved set is printed as a reminder.
        ConsoleLog.Heading("Step 2: resolve the identifiers");
        var ids = Endpoints.Identifiers.Resolve(client, MapCode.US);
        ConsoleLog.Info();
        ConsoleLog.Info("  Your workbook must be the template for Industry Set {0} ({1}).",
            ids.IndustrySet.Id, ids.IndustrySet.Description);
        ConsoleLog.Info("  A template for a different set will be rejected.");

        // Step 3. An empty project for the import to land in.
        ConsoleLog.Heading("Step 3: create the Project");

        // POST /api/v1/impact/project  (wiki: Create Project)
        var project = Projects.CreateProject(client, new Project
        {
            Title = Config.UniqueTitle("Import Events"),
            AggregationSchemeId = ids.AggregationSchemeId,
            HouseholdSetId = ids.HouseholdSetId,
        });
        ConsoleLog.Info("  {0}", project.Describe());

        var projectId = project.Id!.Value;

        // Step 4. Upload. The file goes as multipart form data in a field named
        // `excelFile`.
        ConsoleLog.Heading("Step 4: upload the template");
        try
        {
            // POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)
            Projects.ImportEventTemplate(client, projectId, path);
        }
        catch (ImplanApiException error) when (error.StatusCode == 400)
        {
            // This is the informative failure. The body names the sheet, the row,
            // and what is wrong with it.
            ConsoleLog.Info();
            ConsoleLog.Info("  The template was rejected. IMPLAN's validation says:");
            ConsoleLog.Info("  {0}", error.Problem.Describe());
            ConsoleLog.Info();
            ConsoleLog.Info("  Common causes: the wrong template for this Industry Set, a value");
            ConsoleLog.Info("  written as 100 where the template wants 100%, an event with no");
            ConsoleLog.Info("  value at all, or a formula left in a cell.");
            throw;
        }

        ConsoleLog.Info("  accepted");

        // Step 5. Read back what the import created. The upload answers with a
        // status rather than the objects, so this is how you find out what you got.
        ConsoleLog.Heading("Step 5: read back the Events and Groups");

        // GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)
        var importedEvents = Events.GetEvents(client, projectId);
        ConsoleLog.Info("  {0} events:", importedEvents.Count);
        foreach (var importedEvent in importedEvents)
            ConsoleLog.Info("    {0}", importedEvent.Describe());

        // GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
        var importedGroups = Groups.GetGroups(client, projectId);
        ConsoleLog.Info("  {0} groups:", importedGroups.Count);
        foreach (var group in importedGroups)
            ConsoleLog.Info("    {0}", group.Describe());

        // Three outcomes, and each needs a different next step. A template that
        // fills only the event sheets is the common case rather than a mistake:
        // plenty of analysts keep their events in the workbook and choose the
        // regions afterwards.
        var anyAttached = importedGroups.Any(g => g.GroupEvents.Count > 0);

        if (importedGroups.Count == 0)
        {
            ConsoleLog.Info();
            ConsoleLog.Info("  The import created events but no groups, which means the Groups");
            ConsoleLog.Info("  sheet was left blank. The events are real and the Project is fine.");
            ConsoleLog.Info("  It simply has nowhere to run them yet, because a Group is what");
            ConsoleLog.Info("  pairs a region and a dollar year with the events.");
            ConsoleLog.Info("  Add one with the Create Group endpoint, the way the CreateProject");
            ConsoleLog.Info("  workflow does, or fill the Groups and Group Events sheets and");
            ConsoleLog.Info("  import again into a new Project.");
        }
        else if (!anyAttached)
        {
            ConsoleLog.Info();
            ConsoleLog.Info("  The groups have no events attached. That happens when the Group");
            ConsoleLog.Info("  Events sheet was left blank: the import does not pair them up on");
            ConsoleLog.Info("  its own. Fill that sheet, or attach the events with the Create");
            ConsoleLog.Info("  Group endpoint.");
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Project id: {0}", projectId);
        ConsoleLog.Info("Events:     {0}", importedEvents.Count);
        ConsoleLog.Info("Groups:     {0}", importedGroups.Count);
        if (anyAttached)
        {
            ConsoleLog.Info();
            ConsoleLog.Info("It is ready to run:");
            ConsoleLog.Info("  dotnet run -- run-impact-analysis --project-id {0}", projectId);
        }
        else
        {
            ConsoleLog.Info();
            ConsoleLog.Info("It cannot be run yet. See the note above.");
        }

        return project;
    }

    /// <summary>
    /// Checks the workbook is there, and explains how to make one if it is not.
    /// </summary>
    private static void RequireWorkbook(string path)
    {
        if (File.Exists(path))
            return;

        var lines = new List<string>
        {
            $"No Event Template workbook at {path}.",
            string.Empty,
            "This workflow uploads a filled copy of IMPLAN's own template rather than a",
            "generated file, because the format is strict and a generated one would be",
            "rejected. To make one:",
            string.Empty,
            "  1. Download the blank template that matches your Industry Set:",
        };

        lines.AddRange(BlankTemplates.Select(t => $"       {t.Name,-14} {t.Url}"));
        lines.AddRange(
        [
            string.Empty,
            "  2. Fill in the sheet for the event type you want. The Industry sheet is",
            "     the simplest: an Event Name, a Specification (the industry code), and",
            "     one value such as Output.",
            "  3. Optionally fill the Groups sheet with a FIPS code and dollar year, and",
            "     the Group Events sheet to assign events to groups.",
            $"  4. Save it as {path}",
            string.Empty,
            "Full instructions, including every column on every sheet:",
            "  https://support.implan.com/hc/en-us/articles/360040713754",
        ]);

        throw new FileNotFoundException(string.Join(Environment.NewLine, lines));
    }
}
