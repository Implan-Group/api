# Workflow 10: ImportEvents.
#
# Goal: fill a project from the official IMPLAN Event Template workbook.
#
# Most analysts already keep their events in a spreadsheet. IMPLAN publishes an
# Event Template for exactly that, and the same file the Upload Template button
# takes in IMPLAN Cloud can be posted to the API. One upload can create events,
# groups, and the assignments between them, which is a lot less code than one
# call per event.
#
# The template is strict, and the rules are worth knowing before you fill one in:
#
#   - Use the template that matches your Project's Industry Set. There is one for
#     US 528, US 546, Canada 235, Canada 236, and International, and they are not
#     interchangeable.
#   - Each event type has its own sheet, and the sheet has to be the right one.
#   - Formats matter. A cell the blank template shows as 100% means 100%, not
#     100.
#   - Do not leave an event with no value, and do not leave a formula in a cell.
#   - Keep an import to about 500 events.
#
# A rejected template answers 400 with the validation detail, which is the useful
# part: it names what to fix.
#
# Wiki: Import Events - https://github.com/Implan-Group/api/wiki/Import-Events
# Support: Using the Event Template
# https://support.implan.com/hc/en-us/articles/360040713754


# Where to download the blank templates, by Industry Set.
BLANK_TEMPLATES <- list(
  list(name = "US 528", url = "https://support.implan.com/hc/article_attachments/31846310653723"),
  list(name = "US 546", url = "https://support.implan.com/hc/article_attachments/28726382924059"),
  list(name = "Canada 235", url = "https://support.implan.com/hc/article_attachments/34805745157147"),
  list(name = "Canada 236", url = "https://support.implan.com/hc/article_attachments/49510601287323"),
  list(name = "International", url = "https://support.implan.com/hc/article_attachments/28726664391451")
)


# Checks the workbook is there, and explains how to make one if it is not.
require_workbook <- function(path) {
  if (file.exists(path)) {
    return(path)
  }

  lines <- c(
    sprintf("No Event Template workbook at %s.", path),
    "",
    "This workflow uploads a filled copy of IMPLAN's own template rather than a",
    "generated file, because the format is strict and a generated one would be",
    "rejected. To make one:",
    "",
    "  1. Download the blank template that matches your Industry Set:"
  )

  for (template in BLANK_TEMPLATES) {
    lines <- c(lines, sprintf("       %-14s %s", template$name, template$url))
  }

  lines <- c(
    lines,
    "",
    "  2. Fill in the sheet for the event type you want. The Industry sheet is",
    "     the simplest: an Event Name, a Specification (the industry code), and",
    "     one value such as Output.",
    "  3. Optionally fill the Groups sheet with a FIPS code and dollar year, and",
    "     the Group Events sheet to assign events to groups.",
    sprintf("  4. Save it as %s", path),
    "",
    "Full instructions, including every column on every sheet:",
    "  https://support.implan.com/hc/en-us/articles/360040713754"
  )

  stop(paste(lines, collapse = "\n"), call. = FALSE)
}


import_events_workflow <- function(workbook = NULL) {
  # The filled template to upload. It is not shipped, because a valid workbook
  # has to be made from IMPLAN's own blank template rather than generated.
  path <- if (is.null(workbook)) {
    file.path(data_directory(), "event_template.xlsx")
  } else {
    workbook
  }

  # Step 1. Check the input before doing anything that creates an account object.
  log_heading("Step 1: find the filled Event Template")
  require_workbook(path)
  log_info("  %s (%d KB)", path, as.integer(file.size(path) / 1024))

  client <- create_client()

  # Step 2. Resolve identifiers. The template family has to match the Industry
  # Set this project ends up on, so the resolved set is printed as a reminder.
  log_heading("Step 2: resolve the identifiers")
  ids <- resolve_identifiers(client, MAP_CODES[["US"]])
  log_info("")
  log_info(
    "  Your workbook must be the template for Industry Set %s (%s).",
    ids$industry_set$id, ids$industry_set$description
  )
  log_info("  A template for a different set will be rejected.")

  # Step 3. An empty project for the import to land in.
  log_heading("Step 3: create the Project")

  # POST /api/v1/impact/project  (wiki: Create Project)
  project <- create_project(client, new_project(
    title = unique_title("Import Events"),
    aggregation_scheme_id = ids$aggregation_scheme_id,
    household_set_id = ids$household_set_id
  ))
  log_info("  %s", describe(project))

  # Step 4. Upload. The file goes as multipart form data in a field named
  # `excelFile`.
  log_heading("Step 4: upload the template")
  tryCatch(
    # POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)
    import_event_template(client, project$id, path),
    implan_api_error = function(condition) {
      if (condition$status == 400L) {
        # This is the informative failure. The body names the sheet, the row, and
        # what is wrong with it.
        log_info("")
        log_info("  The template was rejected. IMPLAN's validation says:")
        log_info("  %s", describe(condition$problem))
        log_info("")
        log_info("  Common causes: the wrong template for this Industry Set, a value")
        log_info("  written as 100 where the template wants 100%, an event with no")
        log_info("  value at all, or a formula left in a cell.")
      }
      stop(condition)
    }
  )
  log_info("  accepted")

  # Step 5. Read back what the import created. The upload answers with a status
  # rather than the objects, so this is how you find out what you got.
  log_heading("Step 5: read back the Events and Groups")

  # GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)
  imported_events <- get_events(client, project$id)
  log_info("  %d events:", length(imported_events))
  for (event in imported_events) {
    log_info("    %s", describe(event))
  }

  # GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
  imported_groups <- get_groups(client, project$id)
  log_info("  %d groups:", length(imported_groups))
  for (group in imported_groups) {
    log_info("    %s", describe(group))
  }

  any_attached <- any(vapply(
    imported_groups,
    function(group) length(group$group_events) > 0L,
    logical(1)
  ))

  # Three outcomes, and each needs a different next step. A template that fills
  # only the event sheets is the common case rather than a mistake: plenty of
  # analysts keep their events in the workbook and choose the regions afterwards.
  if (length(imported_groups) == 0L) {
    log_info("")
    log_info("  The import created events but no groups, which means the Groups")
    log_info("  sheet was left blank. The events are real and the Project is fine.")
    log_info("  It simply has nowhere to run them yet, because a Group is what")
    log_info("  pairs a region and a dollar year with the events.")
    log_info("  Add one with the Create Group endpoint, the way the CreateProject")
    log_info("  workflow does, or fill the Groups and Group Events sheets and")
    log_info("  import again into a new Project.")
  } else if (!any_attached) {
    log_info("")
    log_info("  The groups have no events attached. That happens when the Group")
    log_info("  Events sheet was left blank: the import does not pair them up on")
    log_info("  its own. Fill that sheet, or attach the events with the Create")
    log_info("  Group endpoint.")
  }

  log_heading("Done")
  log_info("Project id: %s", project$id)
  log_info("Events:     %d", length(imported_events))
  log_info("Groups:     %d", length(imported_groups))
  if (isTRUE(any_attached)) {
    log_info("")
    log_info("It is ready to run:")
    log_info("  Rscript main.R run-impact-analysis --project-id %s", project$id)
  } else {
    log_info("")
    log_info("It cannot be run yet. See the note above.")
  }

  invisible(project)
}
