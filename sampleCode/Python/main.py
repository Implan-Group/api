"""IMPLAN Impact API samples: the entry point.

Run one workflow at a time:

    python main.py authentication
    python main.py identifiers
    python main.py create-project
    python main.py run-impact-analysis --project-id <guid>

`python main.py --list` prints every workflow with a one-line description.

Each workflow is a file in `workflows/`, written to be read top to bottom. Start
with `authentication`, then `identifiers`, then follow the numbered order.

Before the first run, copy `.env.example` to `.env` and put your IMPLAN username
and password in it. See README.md.
"""

import argparse
import sys

from models.reference import MapCode
from models.region import RegionType
from utilities import config, logging_setup
from utilities.auth import AuthenticationError
from utilities.rest import ImplanApiError

# Every workflow, in the order of the set. The key is what you type on the command
# line; the description is what `--list` prints.
WORKFLOWS: dict[str, str] = {
    "authentication": "1  Get a bearer token, cache it, and verify it",
    "identifiers": "2  Resolve the current scheme, dataset, and industry codes",
    "regions": "3  Walk the region hierarchy and find regions by name",
    "combine-regions": "4  Combine two counties and wait for the model to build",
    "create-project": "5  Create a project with two events and one group",
    "multi-event-to-multi-group": "6  The same events across three states",
    "run-impact-analysis": "7  Run a project and download the five standard reports",
    "bulk-from-csv": "8  Build regions, projects, and runs from CSV input files",
    "regional-exports": "9  Download a regional data export for many regions",
    "import-events": "10 Fill a project from an IMPLAN Event Template workbook",
    "mrio-project": "11 Multi-regional analysis, with spillover between regions",
    "advanced-events": "12 Contribution and spending-pattern events, with tags",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="IMPLAN Impact API workflow samples.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run `python main.py --list` to see every workflow.",
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=sorted(WORKFLOWS),
        help="which workflow to run",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="list the workflows and exit",
    )
    parser.add_argument(
        "--project-id",
        help="an existing project, for the workflows that can use one",
    )
    parser.add_argument(
        "--map-code",
        choices=[code.value for code in MapCode],
        default=MapCode.US.value,
        help="which country's data to use (create-project)",
    )
    parser.add_argument(
        "--region-type",
        choices=[region_type.value for region_type in RegionType],
        default=RegionType.MSA.value,
        help="which regions to export (regional-exports)",
    )
    parser.add_argument(
        "--export-name",
        default="RegionOverviewIndustries",
        help="which regional data export to download (regional-exports)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="how many regions to process, or 0 for all (regional-exports)",
    )
    parser.add_argument(
        "--workbook",
        help="path to a filled Event Template workbook (import-events)",
    )
    return parser


def _print_workflows() -> None:
    print("IMPLAN Impact API sample workflows\n")
    for name, description in WORKFLOWS.items():
        print(f"  {name:<28} {description}")
    print("\nRun one with:  python main.py <name>")
    print("Details for every workflow:  ../README.md and ../../CLAUDE.md")


def _dispatch(args: argparse.Namespace) -> None:
    """Import and run the chosen workflow.

    The imports are inside each branch so that starting one workflow does not pay
    the cost of importing the other eleven, and so a mistake in one does not stop
    the others from running.
    """
    name = args.workflow

    if name == "authentication":
        from workflows import authentication_workflow

        authentication_workflow.run()

    elif name == "identifiers":
        from workflows import identifiers_workflow

        identifiers_workflow.run()

    elif name == "regions":
        from workflows import regions_workflow

        regions_workflow.run()

    elif name == "combine-regions":
        from workflows import combine_regions_workflow

        combine_regions_workflow.run()

    elif name == "create-project":
        from workflows import create_project_workflow

        create_project_workflow.run(MapCode(args.map_code))

    elif name == "multi-event-to-multi-group":
        from workflows import multi_event_to_multi_group_workflow

        multi_event_to_multi_group_workflow.run(args.project_id)

    elif name == "run-impact-analysis":
        from workflows import run_impact_analysis_workflow

        run_impact_analysis_workflow.run(args.project_id)

    elif name == "bulk-from-csv":
        from workflows import bulk_from_csv_workflow

        bulk_from_csv_workflow.run()

    elif name == "regional-exports":
        from workflows import regional_exports_workflow

        regional_exports_workflow.run(
            region_type=RegionType(args.region_type),
            export_name=args.export_name,
            limit=args.limit or None,
        )

    elif name == "import-events":
        from pathlib import Path

        from workflows import import_events_workflow

        workbook = Path(args.workbook) if args.workbook else None
        import_events_workflow.run(workbook)

    elif name == "mrio-project":
        from workflows import mrio_project_workflow

        mrio_project_workflow.run()

    elif name == "advanced-events":
        from workflows import advanced_events_workflow

        advanced_events_workflow.run()

    else:  # pragma: no cover - argparse rejects anything else first
        raise ValueError(f"Unknown workflow {name!r}")


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.list or not args.workflow:
        _print_workflows()
        return 0

    logger = logging_setup.configure()
    logger.info("IMPLAN Impact API sample: %s", args.workflow)
    logger.info("API: %s", config.BASE_URL)

    try:
        _dispatch(args)
    except AuthenticationError as error:
        # Credentials or subscription. The message says which.
        logger.info("")
        logger.info("Authentication failed.")
        logger.info("%s", error)
        return 2
    except ImplanApiError as error:
        # The API refused the request and said why. Quote the traceId to support.
        logger.info("")
        logger.info("The API returned an error.")
        logger.info("%s", error)
        logger.info("")
        logger.info("Full request and response detail: %s", logging_setup.log_path())
        return 3
    except (FileNotFoundError, LookupError, ValueError, RuntimeError, TimeoutError) as error:
        logger.info("")
        logger.info("%s", error)
        return 4
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Stopped. Anything already created is still in your IMPLAN account.")
        return 130

    return 0


if __name__ == "__main__":
    sys.exit(main())
