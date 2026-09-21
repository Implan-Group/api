# Project and folder endpoints.
#
# A Project is the container for one analysis: it fixes the Aggregation Scheme
# and Household Set, and holds the Events and Groups. Folders group projects in
# IMPLAN Cloud and are worth using when a script creates many of them.
#
# Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects


# Creates a Project and returns it with its generated id.
#
# POST /api/v1/impact/project  (wiki: Create Project)
#
# Leave the project's `id` unset. The title must be unique for your account, and
# the Household Set must be one the Aggregation Scheme allows, which is why the
# samples take it from the resolved scheme rather than assuming 1.
#
# A 409 here means the title is already taken.
create_project <- function(client, project) {
  project_from_api(post_json(client, "/api/v1/impact/project", body = to_api(project)))
}


# Reads one Project.
#
# GET /api/v1/impact/project/{projectId}  (wiki: Get Project)
#
# `last_impact_run_id` on the result is the run whose results you read, and is
# the reliable way to find out which run a project actually started.
get_project <- function(client, project_id) {
  project_from_api(get_json(client, sprintf("/api/v1/impact/project/%s", project_id)))
}


# Lists the Projects you created.
#
# GET /api/v1/impact/project  (wiki: Get Projects)
get_projects <- function(client) {
  list_from_api(get_json(client, "/api/v1/impact/project"), project_from_api)
}


# Lists the Projects other people have shared with you.
#
# GET /api/v1/impact/project/shared  (wiki: Get Shared Projects)
get_shared_projects <- function(client) {
  list_from_api(get_json(client, "/api/v1/impact/project/shared"), project_from_api)
}


# Deletes a Project and everything in it.
#
# DELETE /api/v1/impact/project/{projectId}  (wiki: Delete Project)
#
# This is how you clean up after running the samples. It cannot be undone.
delete_project <- function(client, project_id) {
  delete_resource(client, sprintf("/api/v1/impact/project/%s", project_id))
}


# Imports Events into a Project from a filled IMPLAN Event Template.
#
# POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)
#
# The workbook is sent as multipart form data in a field named `excelFile`. It is
# the same file the Upload Template button takes in IMPLAN Cloud, and the same
# strict rules apply: the template family has to match the Project's Industry
# Set, every sheet has its own required columns, and a cell showing 100% in the
# blank template means 100% and not 100.
#
# A 400 carries the validation detail, which is the useful part when a template
# is rejected.
#
# Support: Using the Event Template
# https://support.implan.com/hc/en-us/articles/360040713754
import_event_template <- function(client, project_id, workbook_path) {
  post_file(
    client,
    sprintf("/api/v1/impact/project/import/%s", project_id),
    field_name = "excelFile",
    file_path = workbook_path
  )
}


# Lists your top-level folders.
#
# GET /api/v1/impact/folder  (wiki: Projects, folders section)
get_folders <- function(client) {
  list_from_api(get_json(client, "/api/v1/impact/folder"), folder_from_api)
}


# Creates a folder.
#
# POST /api/v1/impact/folder  (wiki: Projects, folders section)
#
# The title must be unique for your account.
create_folder <- function(client, title) {
  folder_from_api(post_json(client, "/api/v1/impact/folder", body = list(title = title)))
}


# Returns the folder with this title, creating it if it does not exist yet.
#
# Bulk workflows call this so a second run files its projects alongside the first
# instead of failing on a duplicate name.
find_or_create_folder <- function(client, title) {
  for (folder in get_folders(client)) {
    if (identical(folder$title, title)) {
      return(folder)
    }
  }
  create_folder(client, title)
}
