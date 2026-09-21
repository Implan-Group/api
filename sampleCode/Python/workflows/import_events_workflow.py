"""Workflow 10: ImportEvents.

Goal: fill a project from the official IMPLAN Event Template workbook.

Most analysts already keep their events in a spreadsheet. IMPLAN publishes an Event
Template for exactly that, and the same file the Upload Template button takes in
IMPLAN Cloud can be posted to the API. One upload can create events, groups, and
the assignments between them, which is a lot less code than one call per event.

The template is strict, and the rules are worth knowing before you fill one in:

  - Use the template that matches your Project's Industry Set. There is one for
    US 528, US 546, Canada 235, Canada 236, and International, and they are not
    interchangeable.
  - Each event type has its own sheet, and the sheet has to be the right one.
  - Formats matter. A cell the blank template shows as `100%` means `100%`, not
    `100`.
  - Do not leave an event with no value, and do not leave a formula in a cell.
  - Keep an import to about 500 events.

A rejected template answers 400 with the validation detail, which is the useful
part: it names what to fix.

Wiki: Import Events - https://github.com/Implan-Group/api/wiki/Import-Events
Support: Using the Event Template
https://support.implan.com/hc/en-us/articles/360040713754
"""

from pathlib import Path

from endpoints import events, groups, identifiers, projects
from models.project import Project
from models.reference import MapCode
from utilities import auth, config, logging_setup
from utilities.rest import ImplanApiError

# The filled template to upload. This is not shipped, because a valid workbook has
# to be made from IMPLAN's own blank template rather than generated; see the
# message in `_require_workbook` for where to get one.
DEFAULT_WORKBOOK = config.DATA_DIRECTORY / "event_template.xlsx"

# Where to download the blank templates, by Industry Set.
BLANK_TEMPLATES = {
    "US 528": "https://support.implan.com/hc/article_attachments/31846310653723",
    "US 546": "https://support.implan.com/hc/article_attachments/28726382924059",
    "Canada 235": "https://support.implan.com/hc/article_attachments/34805745157147",
    "Canada 236": "https://support.implan.com/hc/article_attachments/49510601287323",
    "International": "https://support.implan.com/hc/article_attachments/28726664391451",
}


def _require_workbook(path: Path) -> Path:
    """Check the workbook is there, and explain how to make one if it is not."""
    if path.exists():
        return path

    lines = [
        f"No Event Template workbook at {path}.",
        "",
        "This workflow uploads a filled copy of IMPLAN's own template rather than",
        "a generated file, because the format is strict and a generated one would",
        "be rejected. To make one:",
        "",
        "  1. Download the blank template that matches your Industry Set:",
    ]
    lines += [f"       {name:<14} {url}" for name, url in BLANK_TEMPLATES.items()]
    lines += [
        "",
        "  2. Fill in the sheet for the event type you want. The Industry sheet is",
        "     the simplest: an Event Name, a Specification (the industry code), and",
        "     one value such as Output.",
        "  3. Optionally fill the Groups sheet with a FIPS code and dollar year, and",
        "     the Group Events sheet to assign events to groups.",
        f"  4. Save it as {path}",
        "",
        "Full instructions, including every column on every sheet:",
        "  https://support.implan.com/hc/en-us/articles/360040713754",
    ]
    raise FileNotFoundError("\n".join(lines))


def run(workbook: Path | None = None) -> Project:
    """Create a project, upload a filled template into it, and read back the result."""
    logger = logging_setup.get_logger()

    # Step 1. Check the input before doing anything that creates an account object.
    logging_setup.heading("Step 1: find the filled Event Template")
    path = _require_workbook(workbook or DEFAULT_WORKBOOK)
    logger.info("  %s (%d KB)", path, path.stat().st_size // 1024)

    client = auth.create_client()

    # Step 2. Resolve identifiers. The template family has to match the Industry
    # Set this project ends up on, so the resolved set is printed as a reminder.
    logging_setup.heading("Step 2: resolve the identifiers")
    ids = identifiers.resolve(client, MapCode.US)
    logger.info("")
    logger.info(
        "  Your workbook must be the template for Industry Set %d (%s).",
        ids.industry_set.id,
        ids.industry_set.description,
    )
    logger.info("  A template for a different set will be rejected.")

    # Step 3. An empty project for the import to land in.
    logging_setup.heading("Step 3: create the Project")

    # POST /api/v1/impact/project  (wiki: Create Project)
    project = projects.create_project(
        client,
        Project(
            title=config.unique_title("Import Events"),
            aggregation_scheme_id=ids.aggregation_scheme_id,
            household_set_id=ids.household_set_id,
        ),
    )
    logger.info("  %s", project.describe())

    # Step 4. Upload. The file goes as multipart form data in a field named
    # `excelFile`.
    logging_setup.heading("Step 4: upload the template")
    try:
        # POST /api/v1/impact/project/import/{projectId}  (wiki: Import Events)
        projects.import_event_template(client, project.id, path)
    except ImplanApiError as error:
        if error.status_code == 400:
            # This is the informative failure. The body names the sheet, the row,
            # and what is wrong with it.
            logger.info("")
            logger.info("  The template was rejected. IMPLAN's validation says:")
            logger.info("  %s", error.problem.describe())
            logger.info("")
            logger.info("  Common causes: the wrong template for this Industry Set,")
            logger.info("  a value written as 100 where the template wants 100%%, an")
            logger.info("  event with no value at all, or a formula left in a cell.")
        raise
    logger.info("  accepted")

    # Step 5. Read back what the import created. The upload answers with a status
    # rather than the objects, so this is how you find out what you got.
    logging_setup.heading("Step 5: read back the Events and Groups")

    # GET /api/v1/impact/project/{projectId}/event  (wiki: Get Events)
    imported_events = events.get_events(client, project.id)
    logger.info("  %d events:", len(imported_events))
    for event in imported_events:
        logger.info("    %s", event.describe())

    # GET /api/v1/impact/project/{projectId}/group  (wiki: Groups)
    imported_groups = groups.get_groups(client, project.id)
    logger.info("  %d groups:", len(imported_groups))
    for group in imported_groups:
        logger.info("    %s", group.describe())

    # Three outcomes, and each needs a different next step. A template that fills
    # only the event sheets is the common case rather than a mistake: plenty of
    # analysts keep their events in the workbook and choose the regions later.
    any_attached = any(group.group_events for group in imported_groups)

    if not imported_groups:
        logger.info("")
        logger.info("  The import created events but no groups, which means the")
        logger.info("  Groups sheet was left blank. The events are real and the")
        logger.info("  Project is fine. It simply has nowhere to run them yet,")
        logger.info("  because a Group is what pairs a region and a dollar year")
        logger.info("  with the events.")
        logger.info("  Add one with the Create Group endpoint, the way the")
        logger.info("  CreateProject workflow does, or fill the Groups and Group")
        logger.info("  Events sheets and import again into a new Project.")
    elif not any_attached:
        logger.info("")
        logger.info("  The groups have no events attached. That happens when the")
        logger.info("  Group Events sheet was left blank: the import does not pair")
        logger.info("  them up on its own. Fill that sheet, or attach the events")
        logger.info("  with the Create Group endpoint.")

    logging_setup.heading("Done")
    logger.info("Project id: %s", project.id)
    logger.info("Events:     %d", len(imported_events))
    logger.info("Groups:     %d", len(imported_groups))
    if any_attached:
        logger.info("")
        logger.info("It is ready to run:")
        logger.info("  python main.py run-impact-analysis --project-id %s", project.id)
    else:
        logger.info("")
        logger.info("It cannot be run yet. See the note above.")
    return project
