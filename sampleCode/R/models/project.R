# Projects and folders: how analyses are organized.
#
# A Project is the container for one analysis. It fixes the Aggregation Scheme
# and Household Set at creation, and everything inside it, every Event and every
# Group, has to be consistent with that choice.
#
# Wiki: Projects - https://github.com/Implan-Group/api/wiki/Projects


# One impact analysis project.
#
# Leave `id` unset when creating; the API generates it and returns it. `title`
# must be unique for your account and must avoid an ampersand and the characters
# | ; % * ? ! = ' " ^ #.
#
# `aggregation_scheme_id` and `household_set_id` cannot be changed afterwards,
# and the household set has to be one of the scheme's `household_set_ids`.
new_project <- function(title,
                        aggregation_scheme_id,
                        household_set_id,
                        is_mrio = FALSE,
                        folder_id = NULL) {
  structure(
    list(
      title = title,
      aggregation_scheme_id = aggregation_scheme_id,
      household_set_id = household_set_id,
      # Multi-regional input-output analysis, which traces effects between the
      # project's regions instead of treating each in isolation. See the
      # MrioProject workflow.
      is_mrio = is_mrio,
      # The folder this project sits in, or NULL for the top level.
      folder_id = folder_id
    ),
    class = c("implan_project", "implan_model", "list")
  )
}


# Reads a project from a response.
#
# `last_impact_run_id` is filled in after the project has been run, and is the
# run whose results you read.
project_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(
      title = "",
      aggregation_scheme_id = NA_integer_,
      household_set_id = NA_integer_,
      id = NULL,
      is_mrio = FALSE,
      folder_id = NULL,
      last_impact_run_id = NULL
    ),
    class_name = "implan_project"
  )
}


# One line naming the project, for the console.
describe.implan_project <- function(x, ...) {
  sprintf("%s  id=%s", x$title, field_or(x, "id", "(none)"))
}


# A folder in IMPLAN Cloud, used to keep a batch of projects together.
folder_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(title = "", id = NULL, parent_id = NULL),
    class_name = "implan_folder"
  )
}


# This folder's id in the integer form a Project's `folder_id` expects.
#
# Note the types. A folder reports its own id as a string, while a project's
# `folderId` and a folder's own `parentId` refer to the same value as an integer.
# The string is canonical, so the conversion happens here rather than at every
# call site.
folder_id_for_project <- function(folder) {
  if (is.null(folder$id)) NULL else as.integer(folder$id)
}


describe.implan_folder <- function(x, ...) {
  sprintf("%s  id=%s", x$title, field_or(x, "id", "(none)"))
}
