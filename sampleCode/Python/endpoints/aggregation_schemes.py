"""Aggregation Scheme endpoints.

An Aggregation Scheme decides how industries are grouped for a Project. It is the
first identifier you resolve and the one everything else hangs off: datasets,
regions, industry codes, and events are all scoped to it.

Wiki: Aggregation Schemes
https://github.com/Implan-Group/api/wiki/Aggregation-Schemes
"""

from models.reference import AggregationScheme
from utilities.rest import ApiClient


def get_aggregation_schemes(
    client: ApiClient, industry_set_id: int | None = None
) -> list[AggregationScheme]:
    """List the Aggregation Schemes the signed-in user can use.

    GET /api/v1/aggregationSchemes  (wiki: Aggregation Schemes)

    Returns both IMPLAN's standard schemes and any custom ones on the account.
    Supplying `industry_set_id` narrows the list to the schemes built on that set,
    which is how you get from "the current industry set" to "the scheme to use".

    Only schemes that have finished building are returned, so an entry here is
    ready to use.
    """
    params = {}
    if industry_set_id is not None:
        # The API spells this parameter with a lowercase `s`: `industrysetId`.
        params["industrysetId"] = industry_set_id

    payload = client.get_json("/api/v1/aggregationSchemes", params=params)
    return AggregationScheme.list_from_api(payload)


def get_aggregation_scheme(
    client: ApiClient, aggregation_scheme_id: int
) -> AggregationScheme:
    """Read one Aggregation Scheme by its id.

    GET /api/v1/aggregationSchemes/{aggregationSchemeId}
    (wiki: Aggregation Scheme by Id)

    Useful for checking `status` after creating a custom scheme: it is only usable
    once that reads `Complete`.
    """
    payload = client.get_json(f"/api/v1/aggregationSchemes/{aggregation_scheme_id}")
    return AggregationScheme.from_api(payload)
