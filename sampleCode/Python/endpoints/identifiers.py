"""Resolving the identifiers every other call needs.

This module composes the lookup endpoints into the one answer a workflow actually
wants: which Aggregation Scheme, Dataset, and Household Set should I use right now?

Resolving instead of hardcoding is the single most important habit when writing
against this API. IMPLAN publishes new data every year and new industry vintages
every few years, and a sample with `aggregation_scheme_id = 8` frozen into it
quietly analyzes 2022 data in 2030. Nothing here is expensive: three GETs, cached
for the life of the run.

Wiki: Getting Started
https://github.com/Implan-Group/api/wiki/Getting-Started
"""

from endpoints import aggregation_schemes, datasets, industries
from models.reference import Identifiers, IndustrySet, MapCode
from utilities import logging_setup
from utilities.rest import ApiClient


def _default_us_industry_set(sets: list[IndustrySet]) -> IndustrySet:
    """Pick the current United States Industry Set.

    Exactly one set carries `is_default`. That flag moves when IMPLAN publishes a
    new vintage, which is precisely why the samples read it instead of naming a
    set.
    """
    for industry_set in sets:
        if industry_set.is_default:
            return industry_set
    raise LookupError(
        "No Industry Set is flagged as the default. Pick one by description from "
        "GET /api/v1/industry-sets."
    )


def _latest_set_for_map_code(
    client: ApiClient, sets: list[IndustrySet], map_code: MapCode
) -> IndustrySet:
    """Pick the newest Industry Set for Canada or International.

    Only the United States set carries `is_default`, so for the other two the
    newest active set is found by looking at which sets the Aggregation Schemes for
    that map code are built on, and taking the highest.
    """
    schemes = [
        scheme
        for scheme in aggregation_schemes.get_aggregation_schemes(client)
        if scheme.map_code == map_code.value and "Unaggregated" in scheme.description
    ]
    if not schemes:
        raise LookupError(f"No Unaggregated Aggregation Scheme for map code {map_code.value}.")

    # Industry Set ids increase with each vintage, so the highest is the newest.
    newest = max(schemes, key=lambda scheme: scheme.industry_set_id)
    for industry_set in sets:
        if industry_set.id == newest.industry_set_id:
            return industry_set

    raise LookupError(
        f"Aggregation Scheme {newest.id} refers to Industry Set "
        f"{newest.industry_set_id}, which is not in the Industry Set list."
    )


def resolve(client: ApiClient, map_code: MapCode = MapCode.US) -> Identifiers:
    """Work out the current Aggregation Scheme, Dataset, and Household Set.

    The chain is always the same:

    1. Find the Industry Set. For the United States that is the one flagged
       `isDefault`; for Canada and International it is the newest one in use.
    2. Take its `defaultAggregationSchemeId`, which is the Unaggregated scheme for
       that set. Falling back to a description search covers a set that does not
       name one.
    3. Read that scheme's Datasets and take the one flagged `isDefault`.
    4. Take the first of the scheme's `householdSetIds`.

    Every workflow starts here, so the console prints what was chosen.
    """
    logger = logging_setup.get_logger()

    # GET /api/v1/industry-sets  (wiki: Get Industry Sets)
    all_sets = industries.get_industry_sets(client)

    if map_code is MapCode.US:
        industry_set = _default_us_industry_set(all_sets)
    else:
        industry_set = _latest_set_for_map_code(client, all_sets, map_code)

    # GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)
    # Narrowing by Industry Set keeps custom schemes on the account out of the way.
    schemes = aggregation_schemes.get_aggregation_schemes(
        client, industry_set_id=industry_set.id
    )
    if not schemes:
        raise LookupError(
            f"Industry Set {industry_set.id} has no Aggregation Schemes available "
            f"to this account."
        )

    scheme = None
    if industry_set.default_aggregation_scheme_id is not None:
        scheme = next(
            (s for s in schemes if s.id == industry_set.default_aggregation_scheme_id),
            None,
        )
    if scheme is None:
        # No default named, so take the Unaggregated scheme, which keeps every
        # industry separate and is the right starting point for a sample.
        scheme = next(
            (s for s in schemes if "Unaggregated" in s.description), schemes[0]
        )

    # GET /api/v1/datasets/{aggregationSchemeId}  (wiki: Dataset by Aggregation Scheme)
    scheme_datasets = datasets.get_datasets_for_scheme(client, scheme.id)
    dataset = datasets.default_dataset(scheme_datasets)

    if not scheme.household_set_ids:
        raise LookupError(
            f"Aggregation Scheme {scheme.id} lists no Household Sets, so a Project "
            f"cannot be created against it."
        )

    identifiers = Identifiers(
        map_code=map_code,
        industry_set=industry_set,
        aggregation_scheme=scheme,
        dataset=dataset,
        household_set_id=scheme.household_set_ids[0],
    )

    logger.info("Resolved identifiers from the API:")
    logger.info(identifiers.describe())
    return identifiers
