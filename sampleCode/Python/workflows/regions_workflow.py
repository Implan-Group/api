"""Workflow 3: Regions.

Goal: navigate the region hierarchy and find the regions an analysis will use.

Regions nest. For a United States scheme the top-level region is the country, its
children are the states, and a state's children are its counties, MSAs, and
congressional districts. The filter reaches down through that hierarchy, so asking
a state for ZIP codes works even though ZIP codes are children of counties.

A region is identified by `hashId`, and that identifier is specific to one
Aggregation Scheme and one Dataset. The same county has a different HashId in a
different scheme or data year, so never carry one between them.

Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
"""

from endpoints import identifiers, regions
from models.reference import MapCode
from models.region import RegionType
from utilities import auth, logging_setup

# The states the later workflows use. Looked up by description so the sample does
# not depend on a HashId that changes with the data year.
TARGET_STATES = ["Oregon", "Wisconsin", "North Carolina"]


def run() -> None:
    """Walk the region hierarchy and find the regions the samples use."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve the scheme and dataset. Region identifiers only mean
    # something inside these two, so they come first.
    logging_setup.heading("Step 1: resolve the Aggregation Scheme and Dataset")
    ids = identifiers.resolve(client, MapCode.US)

    # Step 2. The top of the hierarchy. For a US scheme this is the country.
    logging_setup.heading("Step 2: the top-level region")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}
    # (wiki: Regions - Top Level)
    country = regions.get_top_level_region(
        client, ids.aggregation_scheme_id, ids.dataset_id
    )
    logger.info("  %s", country.describe())
    logger.info(
        "  employment %s    output %s",
        f"{country.employment or 0:,.0f}",
        f"{country.output or 0:,.0f}",
    )
    logger.info(
        "  International schemes have no top-level region and answer 422 here;"
    )
    logger.info("  start from the country children instead.")

    # Step 3. The states. No parent region means "children of the top-level
    # region", so this is every state in the country.
    logging_setup.heading("Step 3: the states")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=State
    # (wiki: Regional Children)
    states = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        region_type=RegionType.STATE,
    )
    logger.info("  %d states and equivalents", len(states))

    # Find the three the other workflows use. Matching on description rather than
    # on a HashId is what keeps these samples working across data years.
    for name in TARGET_STATES:
        state = regions.find_region_by_description(states, name)
        logger.info("    %s", state.describe())

    # Step 4. One level further down. Counties are children of a state.
    logging_setup.heading("Step 4: the counties inside one state")
    oregon = regions.find_region_by_description(states, "Oregon")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}/children?regionTypeFilter=County
    # (wiki: Regional Children)
    counties = regions.get_region_children(
        client,
        ids.aggregation_scheme_id,
        ids.dataset_id,
        parent_hash_id_or_urid=oregon.hash_id,
        region_type=RegionType.COUNTY,
    )
    logger.info("  %d counties in %s", len(counties), oregon.description)
    for county in counties[:5]:
        logger.info("    %s", county.describe())
    if len(counties) > 5:
        logger.info("    ... and %d more", len(counties) - 5)

    logger.info("")
    logger.info("  Every region above carries its own model build status, so this one")
    logger.info("  call tells you both which regions exist and which are ready to use.")
    built = sum(1 for county in counties if county.is_built)
    logger.info("  %d of %d counties are built", built, len(counties))

    # Step 5. Read one region on its own, by HashId.
    logging_setup.heading("Step 5: read one region by HashId")
    lane = regions.find_region_by_description(counties, "Lane County, OR")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}
    # (wiki: Get Region by Id)
    lane_again = regions.get_region(
        client, ids.aggregation_scheme_id, ids.dataset_id, lane.hash_id
    )
    logger.info("  %s", lane_again.describe())
    logger.info("  MRIO allowed: %s", lane_again.is_mrio_allowed)

    # Step 6. Your own regions: the ones you combined or customized. A fresh
    # account has none, and that is a normal result rather than an error.
    logging_setup.heading("Step 6: your combined and customized regions")

    # GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
    # (wiki: Get User Regions by Aggregation Scheme)
    user_regions = regions.get_user_regions_for_scheme(
        client, ids.aggregation_scheme_id, ids.dataset_id
    )
    if user_regions:
        logger.info("  %d of your own regions in this scheme and dataset:", len(user_regions))
        for region in user_regions[:10]:
            logger.info("    %s", region.describe())
        if len(user_regions) > 10:
            logger.info("    ... and %d more", len(user_regions) - 10)

        # GET /api/v1/region/user/{hashId}  (wiki: Get User Region)
        # Reading one is faster than the list and is what to poll while a region
        # builds.
        one = regions.get_user_region(client, user_regions[0].hash_id)
        if one is not None:
            logger.info("  read back one by HashId: %s", one.describe())
    else:
        logger.info("  none yet. The CombineRegions workflow creates one.")

    logging_setup.heading("Done")
    logger.info("HashIds from this run are good for Aggregation Scheme %d and", ids.aggregation_scheme_id)
    logger.info("Dataset %d only. Look them up again for any other combination.", ids.dataset_id)
