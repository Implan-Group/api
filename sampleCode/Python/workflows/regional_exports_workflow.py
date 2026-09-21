"""Workflow 9: RegionalExports.

Goal: download a regional data export for many regions, without tripping the
rate limit.

Regional data exports describe a region's economy as it already is, so they need no
project and no impact run, only a built region. Wanting one for every MSA, or every
county in a state, is common.

The naive version of this asks each region for its status, then downloads. That is
one extra call per region, which for three thousand counties is hours of waiting
under the published five-region-model-requests-per-minute limit. It is also
unnecessary: the children listing already carries `modelBuildStatus` for every
region it returns, so one call gives both the list and which of them are ready.

So the shape here is:

  1. One children call: every region, with its build status.
  2. One build-and-return call for whichever are not built, then wait.
  3. Download, skipping any file already on disk so a re-run resumes.

The export is a parameter. `RegionOverviewIndustries` and the single-file GAMS
export are named for convenience, but any report from the wiki's Regional Data
Exports section can be passed by name.

Wiki: Regional Data Exports
https://github.com/Implan-Group/api/wiki/Regional-Data-Exports
"""

import re
import time

from endpoints import identifiers, regional_data_exports, regions
from models.reference import MapCode
from models.region import Region, RegionType
from utilities import auth, config, logging_setup
from utilities.rest import ApiClient, ImplanApiError, RateLimiter

REGION_REQUESTS_PER_MINUTE = 5

# How many regions to ask for in one build-and-return call.
BUILD_BATCH_SIZE = 25


def _safe_file_name(text: str) -> str:
    """Turn a region description into a filename that is valid on Windows."""
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", text).strip().rstrip(".")
    return cleaned[:150] or "region"


def _ensure_built(
    client: ApiClient, aggregation_scheme_id: int, unbuilt: list[Region]
) -> None:
    """Build the regions whose models are not ready, in batches."""
    logger = logging_setup.get_logger()

    for start in range(0, len(unbuilt), BUILD_BATCH_SIZE):
        batch = unbuilt[start : start + BUILD_BATCH_SIZE]
        hash_ids = [region.hash_id for region in batch]
        logger.info(
            "  requesting %d models (%d to %d of %d)",
            len(batch),
            start + 1,
            start + len(batch),
            len(unbuilt),
        )

        # POST /api/v1/region/build-and-return/{aggregationSchemeId}
        # (wiki: Build and Return Regions)
        regions.build_and_return_regions(client, aggregation_scheme_id, hash_ids)

        # These are IMPLAN regions rather than user regions, so the user-region
        # endpoint does not see them. Give the queue time to work and let the
        # download step below treat a 400 as "still building".
        time.sleep(30)


def run(
    region_type: RegionType = RegionType.MSA,
    export_name: str = regional_data_exports.REGION_OVERVIEW_INDUSTRIES,
    limit: int | None = 10,
) -> None:
    """Download one export for every region of a type.

    `limit` caps how many regions are processed, which keeps a first run short.
    Pass `None` to process all of them, and expect it to take a while: the rate
    limit, not the API's speed, sets the pace.
    """
    logger = logging_setup.get_logger()
    client = auth.create_client()
    client.rate_limiter = RateLimiter(REGION_REQUESTS_PER_MINUTE)

    # Step 1. Resolve identifiers.
    logging_setup.heading("Step 1: resolve the identifiers")
    ids = identifiers.resolve(client, MapCode.US)

    # Step 2. One call for the list and the build status together. This is the
    # step that keeps the workflow inside the rate limit.
    logging_setup.heading("Step 2: list the regions, with their build status")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=...
    # (wiki: Regional Children)
    found = regions.get_region_children(
        client, ids.aggregation_scheme_id, ids.dataset_id, region_type=region_type
    )
    logger.info("  %d regions of type %s", len(found), region_type.value)

    if limit is not None and len(found) > limit:
        found = found[:limit]
        logger.info("  limited to the first %d for this run", limit)

    built = [region for region in found if region.is_built]
    unbuilt = [region for region in found if not region.is_built]
    logger.info("  %d already built, %d not yet", len(built), len(unbuilt))
    logger.info("  (that status came from the same call as the list, so this cost")
    logger.info("   one request rather than one per region)")

    # Step 3. Build whatever is missing.
    if unbuilt:
        logging_setup.heading("Step 3: build the models that are missing")
        _ensure_built(client, ids.aggregation_scheme_id, unbuilt)
    else:
        logging_setup.heading("Step 3: nothing to build")
        logger.info("  every region already has a model")

    # Step 4. Download. Skipping files already on disk makes a re-run resume
    # rather than start over, which matters when the whole job takes an hour.
    logging_setup.heading("Step 4: download the export for each region")
    extension = regional_data_exports.file_extension_for(export_name)
    destination = (
        config.REPORTS_DIRECTORY
        / f"{export_name}-agg{ids.aggregation_scheme_id}-ds{ids.dataset_id}"
    )
    destination.mkdir(parents=True, exist_ok=True)
    logger.info("  into %s", destination)

    downloaded = skipped = failed = 0

    for region in found:
        path = destination / f"{_safe_file_name(region.description)}{extension}"
        if path.exists():
            skipped += 1
            continue

        try:
            # GET /api/v1/regions/export/{aggregationSchemeId}/{exportName}?hashId=...
            # (wiki: Regional Data Exports)
            content = regional_data_exports.get_export(
                client, ids.aggregation_scheme_id, export_name, region=region
            )
        except ImplanApiError as error:
            if error.status_code == 400:
                # From these endpoints a 400 nearly always means the model is still
                # building rather than that the request was wrong.
                logger.info(
                    "  %s: not ready yet (400); run again later", region.description
                )
            else:
                logger.info("  %s: %s", region.description, error.problem.describe())
            failed += 1
            continue

        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        downloaded += 1
        logger.info("  %s", path.name)

    logging_setup.heading("Done")
    logger.info("Downloaded: %d", downloaded)
    logger.info("Skipped (already on disk): %d", skipped)
    logger.info("Not ready or failed: %d", failed)
    logger.info("Folder: %s", destination)
    if failed:
        logger.info("")
        logger.info("Run this again to pick up the ones that were still building.")
