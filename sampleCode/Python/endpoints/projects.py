"""Project and folder endpoints.

A Project is the container for one analysis: it fixes the Aggregation Scheme and
Household Set, and holds the Events and Groups. Folders group projects in IMPLAN
Cloud and are worth using when a script creates many of them.

Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects
"""

from models.project import Folder, Project
from utilities.rest import ApiClient


def create_project(client: ApiClient, project: Project) -> Project:
    """Create a Project and return it with its generated id.

    POST /api/v1/impact/project  (wiki: Create Project)

    Leave `project.id` unset. The title must be unique for your account, and the
    Household Set must be one the Aggregation Scheme allows, which is why the
    samples take it from the resolved scheme rather than assuming 1.

    A 409 here means the title is already taken.
    """
    payload = client.post_json("/api/v1/impact/project", json_body=project.to_api())
    return Project.from_api(payload)


def get_project(client: ApiClient, project_id: str) -> Project:
    """Read one Project.

    GET /api/v1/impact/project/{projectId}  (wiki: Get Project)

    `last_impact_run_id` on the result is the run whose results you read, and is
    the reliable way to find out which run a project actually started.
    """
    payload = client.get_json(f"/api/v1/impact/project/{project_id}")
    return Project.from_api(payload)


def get_projects(client: ApiClient) -> list[Project]:
    """List the Projects you created.

    GET /api/v1/impact/project  (wiki: Get Projects)
    """
    payload = client.get_json("/api/v1/impact/project")
    return Project.list_from_api(payload)


def get_shared_projects(client: ApiClient) -> list[Project]:
    """List the Projects other people have shared with you.

    GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
    """
    payload = client.get_json("/api/v1/impact/project/shared")
    return Project.list_from_api(payload)


def delete_project(client: ApiClient, project_id: str) -> None:
    """Delete a Project and everything in it.

    DELETE /api/v1/impact/project/{projectId}  (wiki: Delete Project)

    This is how you clean up after running the samples. It cannot be undone.
    """
    client.delete(f"/api/v1/impact/project/{project_id}")


def import_event_template(client: ApiClient, project_id: str, workbook_path) -> object:
    """Import Events into a Project from a filled IMPLAN Event Template.

    POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)

    The workbook is sent as multipart form data in a field named `excelFile`. It is
    the same file the Upload Template button takes in IMPLAN Cloud, and the same
    strict rules apply: the template family has to match the Project's Industry
    Set, every sheet has its own required columns, and a cell showing `100%` in the
    blank template means `100%` and not `100`.

    A 400 carries the validation detail, which is the useful part when a template
    is rejected.

    Support: Using the Event Template
    https://support.implan.com/hc/en-us/articles/360040713754
    """
    return client.post_file(
        f"/api/v1/impact/project/import/{project_id}",
        field_name="excelFile",
        file_path=workbook_path,
    )


def get_folders(client: ApiClient) -> list[Folder]:
    """List your top-level folders.

    GET /api/v1/impact/folder  (wiki: Projects, folders section)
    """
    payload = client.get_json("/api/v1/impact/folder")
    return Folder.list_from_api(payload)


def create_folder(client: ApiClient, title: str) -> Folder:
    """Create a folder.

    POST /api/v1/impact/folder  (wiki: Projects, folders section)

    The title must be unique for your account.
    """
    payload = client.post_json(
        "/api/v1/impact/folder", json_body=Folder(title=title).to_api()
    )
    return Folder.from_api(payload)


def find_or_create_folder(client: ApiClient, title: str) -> Folder:
    """Return the folder with this title, creating it if it does not exist yet.

    Bulk workflows call this so a second run files its projects alongside the first
    instead of failing on a duplicate name.
    """
    for folder in get_folders(client):
        if folder.title == title:
            return folder
    return create_folder(client, title)
