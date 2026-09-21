"""Workflow 2: Identifiers.

Goal: discover every id the other workflows need, instead of hardcoding it.

This is the workflow to read first if you are new to the API, because the ids it
resolves are the ones that trip people up. They are not stable across time and not
portable across schemes:

  - Industry Set ids change when IMPLAN publishes a new industry vintage.
  - Dataset ids are specific to an Aggregation Scheme and are not ordered by year.
  - Industry codes mean different industries in different Industry Sets. Code 509
    is Full-service restaurants in the 546 set and Federal electric utilities in
    the 528 set, so a code copied from an old example silently analyzes the wrong
    industry.

Nothing here is expensive, and the resolution is four GETs. Do it at the start of a
run and pass the result around.

Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started
"""

from endpoints import datasets, identifiers, industries, regions
from models.reference import MapCode
from utilities import auth, logging_setup


def run() -> None:
    """Resolve the current identifiers for the US, Canada, and International."""
    logger = logging_setup.get_logger()
    client = auth.create_client()

    # Step 1. Resolve the United States identifiers. This is the chain every
    # workflow starts with: default Industry Set, its Aggregation Scheme, that
    # scheme's default Dataset, and the scheme's first Household Set.
    logging_setup.heading("Step 1: resolve the current United States identifiers")
    us = identifiers.resolve(client, MapCode.US)

    # Step 2. Show the pieces the resolution walked through, so the chain is
    # visible rather than implied.
    logging_setup.heading("Step 2: the lists those came from")

    # GET /api/v1/industry-sets  (wiki: Get Industry Sets)
    all_sets = industries.get_industry_sets(client)
    logger.info("  Industry Sets (%d). The one flagged default is the current US list:", len(all_sets))
    for industry_set in all_sets:
        marker = " <- default" if industry_set.is_default else ""
        active = "" if industry_set.active_status else "  (retired)"
        logger.info(
            "    %3d  %-40s%s%s",
            industry_set.id,
            industry_set.description,
            active,
            marker,
        )

    # GET /api/v1/datasets/{aggregationSchemeId}  (wiki: Dataset by Aggregation Scheme)
    scheme_datasets = datasets.get_datasets_for_scheme(client, us.aggregation_scheme_id)
    logger.info("")
    logger.info(
        "  Datasets in Aggregation Scheme %d (%d). Note that the default is last,",
        us.aggregation_scheme_id,
        len(scheme_datasets),
    )
    logger.info("  not first, and that these ids are meaningless in another scheme:")
    for dataset in scheme_datasets:
        marker = " <- default" if dataset.is_default else ""
        logger.info("    %3d  %s%s", dataset.id, dataset.description, marker)

    # Step 3. Look an industry up properly. Checking the description alongside the
    # code is what catches a code that has moved between industry vintages.
    logging_setup.heading("Step 3: look up an industry by code, and verify it")

    # GET /api/v1/IndustryCodes/{aggregationSchemeId}
    # (wiki: Industry Codes by Aggregation Scheme)
    # This route takes no query string: the scheme already implies its Industry Set.
    codes = industries.get_industry_codes_for_scheme(client, us.aggregation_scheme_id)
    logger.info("  %d industries in this Aggregation Scheme", len(codes))

    oilseed = industries.find_industry(codes, 1, "Oilseed farming")
    logger.info("  code %d is '%s', as expected", oilseed.code, oilseed.description)

    # The portable way round: ask for the industry by name and accept whatever code
    # it has in this scheme. This is what the other workflows do for restaurants.
    restaurants = industries.find_industry_by_description(codes, "Full-service restaurants")
    logger.info(
        "  'Full-service restaurants' is code %d in this Industry Set", restaurants.code
    )
    logger.info(
        "  (it is a different code in other sets, which is why the samples look it"
    )
    logger.info("   up by name rather than hardcoding a number)")

    # Step 4. Region types, which are the values the region filters accept.
    logging_setup.heading("Step 4: region types")

    # GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
    region_types = regions.get_region_types(client)
    logger.info("  %s", ", ".join(region_types))
    logger.info("  For Canadian data, State filters to Provinces and County to")
    logger.info("  Economic Regions.")

    # Step 5. The same resolution for Canada and International. Only the US set
    # carries the default flag, so for these two the newest set in use is found
    # through the Aggregation Schemes instead.
    logging_setup.heading("Step 5: the same resolution for Canada and International")
    for map_code in (MapCode.CANADA, MapCode.INTERNATIONAL):
        try:
            # `resolve` prints what it found, so there is nothing to do with the
            # return value here.
            identifiers.resolve(client, map_code)
            logger.info("")
        except LookupError as error:
            # An account whose subscription does not include Canadian or
            # international data is a normal situation, not a failure.
            logger.info(
                "  %s is not available on this subscription: %s", map_code.value, error
            )

    logging_setup.heading("Done")
    logger.info("Use these ids for the rest of this session. Resolve them again next")
    logger.info("run rather than writing them down: IMPLAN publishes new data every")
    logger.info("year, and the defaults move.")
