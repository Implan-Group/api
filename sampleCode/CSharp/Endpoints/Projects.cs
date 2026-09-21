namespace Implan.ApiSamples.Endpoints;

/// <summary>
/// Project and folder endpoints.
/// </summary>
/// <remarks>
/// A Project is the container for one analysis: it fixes the Aggregation Scheme and
/// Household Set, and holds the Events and Groups. Folders group projects in IMPLAN
/// Cloud and are worth using when a script creates many of them.
///
/// Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
/// </remarks>
public static class Projects
{
    /// <summary>
    /// Creates a Project and returns it with its generated id.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/project  (wiki: Create Project)
    ///
    /// Leave the id unset. The title must be unique for your account, and the
    /// Household Set must be one the Aggregation Scheme allows, which is why the
    /// samples take it from the resolved scheme rather than assuming 1.
    ///
    /// A 409 here means the title is already taken.
    /// </remarks>
    public static Project CreateProject(ApiClient client, Project project)
    {
        return client.PostJson<Project>("/api/v1/impact/project", project);
    }

    /// <summary>
    /// Reads one Project.
    /// </summary>
    /// <remarks>
    /// GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
    ///
    /// <c>lastImpactRunId</c> on the result is the run whose results you read, and
    /// is the reliable way to find out which run a project actually started.
    /// </remarks>
    public static Project GetProject(ApiClient client, Guid projectId)
    {
        return client.GetJson<Project>($"/api/v1/impact/project/{projectId}");
    }

    /// <summary>
    /// Lists the Projects you created.
    /// </summary>
    /// <remarks>GET /api/v1/impact/project  (wiki: Get Projects)</remarks>
    public static List<Project> GetProjects(ApiClient client)
    {
        return client.GetJson<List<Project>>("/api/v1/impact/project");
    }

    /// <summary>
    /// Lists the Projects other people have shared with you.
    /// </summary>
    /// <remarks>GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)</remarks>
    public static List<Project> GetSharedProjects(ApiClient client)
    {
        return client.GetJson<List<Project>>("/api/v1/impact/project/shared");
    }

    /// <summary>
    /// Deletes a Project and everything in it.
    /// </summary>
    /// <remarks>
    /// DELETE /api/v1/impact/project/{projectId}  (wiki: Delete Project)
    ///
    /// This is how you clean up after running the samples. It cannot be undone.
    /// </remarks>
    public static void DeleteProject(ApiClient client, Guid projectId)
    {
        client.Delete($"/api/v1/impact/project/{projectId}");
    }

    /// <summary>
    /// Imports Events into a Project from a filled IMPLAN Event Template.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)
    ///
    /// The workbook is sent as multipart form data in a field named
    /// <c>excelFile</c>. It is the same file the Upload Template button takes in
    /// IMPLAN Cloud, and the same strict rules apply: the template family has to
    /// match the Project's Industry Set, every sheet has its own required columns,
    /// and a cell showing <c>100%</c> in the blank template means <c>100%</c> and
    /// not <c>100</c>.
    ///
    /// A 400 carries the validation detail, which is the useful part when a template
    /// is rejected.
    ///
    /// Support: Using the Event Template
    /// https://support.implan.com/hc/en-us/articles/360040713754
    /// </remarks>
    public static string ImportEventTemplate(ApiClient client, Guid projectId, string workbookPath)
    {
        return client.PostFile($"/api/v1/impact/project/import/{projectId}", "excelFile", workbookPath);
    }

    /// <summary>
    /// Lists your top-level folders.
    /// </summary>
    /// <remarks>GET /api/v1/impact/folder  (wiki: Projects, folders section)</remarks>
    public static List<Folder> GetFolders(ApiClient client)
    {
        return client.GetJson<List<Folder>>("/api/v1/impact/folder");
    }

    /// <summary>
    /// Creates a folder.
    /// </summary>
    /// <remarks>
    /// POST /api/v1/impact/folder  (wiki: Projects, folders section)
    ///
    /// The title must be unique for your account.
    /// </remarks>
    public static Folder CreateFolder(ApiClient client, string title)
    {
        return client.PostJson<Folder>("/api/v1/impact/folder", new Folder { Title = title });
    }

    /// <summary>
    /// Returns the folder with this title, creating it if it does not exist yet.
    /// </summary>
    /// <remarks>
    /// Bulk workflows call this so a second run files its projects alongside the
    /// first instead of failing on a duplicate name.
    /// </remarks>
    public static Folder FindOrCreateFolder(ApiClient client, string title)
    {
        var existing = GetFolders(client)
            .FirstOrDefault(f => string.Equals(f.Title, title, StringComparison.Ordinal));

        return existing ?? CreateFolder(client, title);
    }
}
