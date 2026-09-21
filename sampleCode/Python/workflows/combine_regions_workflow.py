"""Workflow 4: CombineRegions.

Goal: combine two counties into one region and wait for its model to build.

IMPLAN builds a model for every region it publishes, but a study area is often not
one of them: two counties either side of a state line, the six counties a transit
authority serves, a metro area plus its exurbs. Combining regions makes one
economic region out of several, and the result behaves like any other region
afterwards.

The important part of this workflow is the waiting. The build is asynchronous: the
POST returns immediately with the new region at status `New`, and the model is not
usable until that reads `Complete`. Poll the single-region endpoint for that, and
never poll a heavy data export to find out, because those answer with an error
until the model is ready and the error looks like a different problem.

Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
Support: Combining Regions
https://support.implan.com/hc/en-us/articles/1260805784110
"""

from endpoints import identifiers, regions
from models.reference import MapCode
from models.region import CombineRegionRequest, RegionType
from utilities import auth, config, logging_setup

# Two adjacent Oregon counties. They must come from the same dataset, must not
# overlap, and must not nest inside one another, so a state and a county within it
# would be rejected.
COUNTIES_TO_COMBINE = ["Lane County, OR", "Douglas County, OR"]


def run() -> str:
    """Combine two counties, wait for the build, and return the new HashId."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve the scheme and dataset the combined region will belong to.
    logging_setup.heading("Step 1: resolve the Aggregation Scheme and Dataset")
    ids = identifiers.resolve(client, MapCode.US)

    # Step 2. Find the counties by name and collect their HashIds.
    logging_setup.heading("Step 2: find the regions to combine")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=County
    # (wiki: Regional Children)
    all_counties = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        region_type=RegionType.COUNTY,
    )
    logger.info("  %d counties in this scheme and dataset", len(all_counties))

    chosen = [
        regions.find_region_by_description(all_counties, name)
        for name in COUNTIES_TO_COMBINE
    ]
    for county in chosen:
        logger.info("    %s", county.describe())

    # Step 3. Ask for the combination. The description has to be unique for your
    # account, so it carries a timestamp.
    logging_setup.heading("Step 3: request the combined region")
    description = config.unique_title("Combined Region")

    # Re-running this workflow should not fail on a name that already exists, and
    # should not build the same region twice.
    existing = regions.find_existing_user_region(
        client, ids.aggregation_scheme_id, ids.dataset_id, description
    )
    if existing is not None:
        logger.info("  a region named '%s' already exists; reusing it", description)
        combined = existing
    else:
        request = CombineRegionRequest(
            description=description,
            hash_ids=[county.hash_id for county in chosen],
        )
        logger.info("  combining %d regions as '%s'", len(chosen), description)

        # POST /api/v1/region/build/combined/{aggregationSchemeId}
        # (wiki: Combine Regions)
        combined = regions.build_combined_region(
            client, ids.aggregation_scheme_id, request
        )
        logger.info("  accepted: %s", combined.describe())
        logger.info("  status is '%s'; the model builds in the background", combined.model_build_status)

    # Step 4. Wait for the model. A combined region usually finishes inside a
    # minute; the helper gives up after ten and says so rather than looping.
    logging_setup.heading("Step 4: wait for the model to build")

    # GET /api/v1/region/user/{hashId}, polled  (wiki: Get User Region)
    built = regions.wait_for_region_build(client, combined.hash_id)
    logger.info("  built")
    logger.info("    %s", built.describe())
    logger.info(
        "    employment %s    output %s",
        f"{built.employment or 0:,.0f}",
        f"{built.output or 0:,.0f}",
    )

    logging_setup.heading("Done")
    logger.info("Created region: %s", built.description)
    logger.info("  HashId:      %s", built.hash_id)
    logger.info("  userModelId: %s", built.user_model_id)
    logger.info("")
    logger.info("Use that HashId in a Group exactly as you would an IMPLAN region.")
    logger.info("Delete the region from Regions in IMPLAN Cloud when you are done.")
    return built.hash_id
