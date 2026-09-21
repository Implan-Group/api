"""Region endpoints: finding, combining, and building regions.

Regions form a hierarchy. The top-level region for a United States scheme is the
country; its children are the states; a state's children are its counties, MSAs,
and congressional districts; a county's children are its ZIP codes. International
schemes have no top-level region, so start from the country children instead.

Alongside IMPLAN's regions sit your own: combined regions you built from several
others, and customized regions where you edited the underlying economic data. Those
are the "user" regions.

Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
Wiki: Combine Regions - https://github.com/Implan-Group/api/wiki/Combine-Regions
"""

import time

from models.region import CombineRegionRequest, ModelBuildStatus, Region, RegionType
from utilities import config, logging_setup
from utilities.rest import ApiClient, ImplanApiError


def get_region_types(client: ApiClient) -> list[str]:
    """List the values accepted by the `regionTypeFilter` parameter.

    GET /api/v1/region/RegionTypes  (wiki: Get Region Types)

    This is also the cheapest authenticated call in the API, which is why the auth
    helper uses it to test a cached token.
    """
    return client.get_json("/api/v1/region/RegionTypes")


def get_top_level_region(
    client: ApiClient, aggregation_scheme_id: int, dataset_id: int
) -> Region:
    """Read the region at the top of the hierarchy, usually a country.

    GET /api/v1/region/{aggregationSchemeId}/{datasetId}
    (wiki: Regions - Top Level)

    International schemes have no top-level region and answer 422 here; use
    `get_region_children` with `RegionType.COUNTRY` for those.
    """
    payload = client.get_json(f"/api/v1/region/{aggregation_scheme_id}/{dataset_id}")
    return Region.from_api(payload)


def get_region(
    client: ApiClient,
    aggregation_scheme_id: int,
    dataset_id: int,
    hash_id_or_urid: str | int,
) -> Region:
    """Read one region by HashId or URID.

    GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}
    (wiki: Get Region by Id)
    """
    payload = client.get_json(
        f"/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hash_id_or_urid}"
    )
    return Region.from_api(payload)


def get_region_children(
    client: ApiClient,
    aggregation_scheme_id: int,
    dataset_id: int,
    parent_hash_id_or_urid: str | int | None = None,
    region_type: RegionType | str | None = None,
) -> list[Region]:
    """List the regions inside a region, optionally filtered to one type.

    GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children
    GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashIdOrUrid}/children
    (wiki: Regional Children)

    Omitting the parent starts from the top-level region, so asking for `State`
    with no parent gives every state in the country.

    The filter reaches through the hierarchy: asking a state for `Zipcode` returns
    the ZIP codes of its counties, not nothing.

    Worth knowing for bulk work: every region in this response carries its own
    `model_build_status`, so one call tells you both which regions exist and which
    of them are already built. There is no separate endpoint for that, and asking
    region by region is what makes a bulk script trip the rate limit.
    """
    if parent_hash_id_or_urid is None:
        path = f"/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children"
    else:
        path = (
            f"/api/v1/region/{aggregation_scheme_id}/{dataset_id}"
            f"/{parent_hash_id_or_urid}/children"
        )

    params = {}
    if region_type is not None:
        value = region_type.value if isinstance(region_type, RegionType) else region_type
        params["regionTypeFilter"] = value

    payload = client.get_json(path, params=params)
    return Region.list_from_api(payload)


def get_user_regions_for_scheme(
    client: ApiClient, aggregation_scheme_id: int, dataset_id: int
) -> list[Region]:
    """List your combined and customized regions for one scheme and dataset.

    GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user
    (wiki: Get User Regions by Aggregation Scheme)
    """
    payload = client.get_json(
        f"/api/v1/region/{aggregation_scheme_id}/{dataset_id}/user"
    )
    return Region.list_from_api(payload)


def get_user_regions(
    client: ApiClient,
    aggregation_scheme_id: int | None = None,
    dataset_id: int | None = None,
) -> list[Region]:
    """List all of your combined and customized regions.

    GET /api/v1/region/user  (wiki: Get User Regions)

    On an account with many custom schemes this call can answer 503 while IMPLAN
    rebuilds its region cache, and the first request can exceed the gateway's
    30-second limit. Narrowing it with a scheme and dataset, or using the
    scheme-scoped call above, is more reliable.
    """
    params = {}
    if aggregation_scheme_id is not None:
        params["aggregationSchemeId"] = aggregation_scheme_id
    if dataset_id is not None:
        params["datasetId"] = dataset_id

    payload = client.get_json("/api/v1/region/user", params=params)
    return Region.list_from_api(payload)


def get_user_region(client: ApiClient, hash_id: str) -> Region | None:
    """Read one of your regions by HashId.

    GET /api/v1/region/user/{hashId}  (wiki: Get User Region)

    This is the endpoint to poll while a combined region builds. It reads one
    region rather than the whole list, so it stays fast and avoids the 503 the list
    can return.

    An unknown HashId comes back as an empty body rather than a 404, so `None` here
    means "no such region of yours".
    """
    payload = client.get_json(f"/api/v1/region/user/{hash_id}")
    if not payload:
        return None
    return Region.from_api(payload)


def build_combined_region(
    client: ApiClient, aggregation_scheme_id: int, request: CombineRegionRequest
) -> Region:
    """Combine two or more regions into one and start building its model.

    POST /api/v1/region/build/combined/{aggregationSchemeId}
    (wiki: Combine Regions)

    Returns immediately with the new region at `modelBuildStatus` of `New`. The
    model is not usable until that reads `Complete`, which is what
    `wait_for_region_build` waits for.

    The regions being combined must come from the same dataset, must not overlap,
    and must not nest: a state and a county inside it cannot be combined. The
    description has to be unique for your account.

    The endpoint answers with an array holding the single new region.
    """
    payload = client.post_json(
        f"/api/v1/region/build/combined/{aggregation_scheme_id}",
        json_body=request.to_api(),
    )
    regions = Region.list_from_api(payload)
    if len(regions) != 1:
        raise RuntimeError(
            f"Expected one combined region back, got {len(regions)}."
        )
    return regions[0]


def build_and_return_regions(
    client: ApiClient, aggregation_scheme_id: int, hash_ids: list[str]
) -> list[Region]:
    """Build several IMPLAN regions at once, without combining them.

    POST /api/v1/region/build-and-return/{aggregationSchemeId}
    (wiki: Build and Return Regions)

    The body is a plain array of HashIds. Use this when a bulk job needs regions
    whose models have not been built yet: one call queues all of them instead of
    one call each.

    Like the combined build, this returns before the models are ready.
    """
    payload = client.post_json(
        f"/api/v1/region/build-and-return/{aggregation_scheme_id}",
        json_body=hash_ids,
    )
    return Region.list_from_api(payload)


def wait_for_region_build(
    client: ApiClient,
    hash_id: str,
    timeout_seconds: int = config.REGION_BUILD_TIMEOUT_SECONDS,
    poll_seconds: int = config.REGION_BUILD_POLL_SECONDS,
) -> Region:
    """Poll until a combined or customized region has finished building.

    Polls `GET /api/v1/region/user/{hashId}` rather than the user-regions list: it
    is one region instead of all of them, and it does not hit the 503 the list can
    return on a busy account.

    Raises on a build that reports `Error`, and on a build that has not finished
    inside `timeout_seconds`. Never poll a heavy data endpoint to find out whether
    a model is ready; those answer with an error until it is, which is slow and
    reads like a different problem.
    """
    logger = logging_setup.get_logger()
    deadline = time.monotonic() + timeout_seconds
    last_status = ""

    while True:
        region = get_user_region(client, hash_id)

        if region is not None:
            if region.model_build_status != last_status:
                last_status = region.model_build_status
                logger.info("  region %s: %s", hash_id, last_status or "(no status)")

            if region.is_built:
                return region

            if region.model_build_status == ModelBuildStatus.ERROR.value:
                raise RuntimeError(
                    f"The model for region {hash_id} failed to build. Try the "
                    f"request again, or contact support@implan.com if it repeats."
                )

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Region {hash_id} was still building after {timeout_seconds} "
                f"seconds, last status '{last_status or 'unknown'}'. It may still "
                f"finish; check your regions in IMPLAN Cloud."
            )

        time.sleep(poll_seconds)


def find_region_by_description(regions: list[Region], description: str) -> Region:
    """Find one region by its exact description, matched case-insensitively.

    Region descriptions carry their state, as in `Lane County, OR`, so they are
    unique within a region type.
    """
    wanted = description.casefold()
    for region in regions:
        if region.description.casefold() == wanted:
            return region
    raise LookupError(
        f"No region named '{description}' in this list of {len(regions)} regions. "
        f"Check the spelling, including the state abbreviation."
    )


def find_existing_user_region(
    client: ApiClient, aggregation_scheme_id: int, dataset_id: int, description: str
) -> Region | None:
    """Return one of your regions by name, or `None` if you have not built it.

    Bulk workflows call this first so that re-running them reuses the regions they
    built last time instead of failing on a duplicate name.
    """
    try:
        existing = get_user_regions_for_scheme(
            client, aggregation_scheme_id, dataset_id
        )
    except ImplanApiError as error:
        if error.status_code == 503:
            # The region cache is rebuilding. Treat it as "cannot tell", and let
            # the caller try the build, which reports a duplicate name clearly.
            logging_setup.get_logger().info(
                "  the user-regions list is temporarily unavailable (503); "
                "continuing without checking for an existing region"
            )
            return None
        raise

    wanted = description.casefold()
    for region in existing:
        if region.description.casefold() == wanted:
            return region
    return None
