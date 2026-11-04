"""Industry Set and Industry Code endpoints.

An Industry Set is a vintage of IMPLAN's industry list; an Industry Code names one
industry inside a set. Codes are only meaningful with their set: 509 is
Full-service restaurants in the 546 set and Federal electric utilities in the 528
set, so a code copied from an older example lands on the wrong industry rather than
failing.

Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries
"""

from models.reference import IndustryCode, IndustrySet
from utilities.rest import ApiClient


def get_industry_sets(client: ApiClient) -> list[IndustrySet]:
    """List every Industry Set, including retired ones.

    GET /api/v1/industry-sets  (wiki: Get Industry Sets)

    `active_status` marks a set as still supported and exactly one set carries
    `is_default`, which is the current United States list. There is no public
    endpoint for reading a single set, so filter this list when you want one.
    """
    payload = client.get_json("/api/v1/industry-sets")
    return IndustrySet.list_from_api(payload)


def get_industry_codes_for_scheme(
    client: ApiClient, aggregation_scheme_id: int
) -> list[IndustryCode]:
    """List the industries in an Aggregation Scheme, ordered by code.

    GET /api/v1/IndustryCodes/{aggregationSchemeId}
    (wiki: Industry Codes by Aggregation Scheme)

    This route takes no query string. An `industrySetId` parameter added here is
    ignored, because a scheme already implies its Industry Set; the route below is
    the one that accepts it. For a custom scheme these are the scheme's own
    aggregated sectors.
    """
    payload = client.get_json(f"/api/v1/IndustryCodes/{aggregation_scheme_id}")
    return IndustryCode.list_from_api(payload)


def get_industry_codes_for_set(
    client: ApiClient, industry_set_id: int | None = None
) -> list[IndustryCode]:
    """List the industries in an Industry Set, ordered by code.

    GET /api/v1/IndustryCodes  (wiki: Industry Codes by Industry Set)

    Omitting `industry_set_id` uses the current default United States set.
    """
    params = {}
    if industry_set_id is not None:
        params["industrySetId"] = industry_set_id

    payload = client.get_json("/api/v1/IndustryCodes", params=params)
    return IndustryCode.list_from_api(payload)


def find_industry(
    industries: list[IndustryCode], code: int, expected_description: str
) -> IndustryCode:
    """Find one industry by code, and confirm it is the industry you meant.

    Checking the description as well as the code is the guard against the trap this
    module's docstring describes. The comparison is loose on purpose: IMPLAN
    rewords descriptions between vintages, so a substring match either way is
    enough to catch a code that has moved to a different industry entirely.
    """
    for industry in industries:
        if industry.code != code:
            continue

        actual = industry.description.casefold()
        expected = expected_description.casefold()
        if expected in actual or actual in expected:
            return industry

        raise LookupError(
            f"Industry code {code} is '{industry.description}' in this Aggregation "
            f"Scheme, not '{expected_description}'. Industry codes differ between "
            f"Industry Sets; look the industry up by description instead."
        )

    raise LookupError(f"No industry with code {code} in this Aggregation Scheme.")


def find_industry_by_description(
    industries: list[IndustryCode], description: str
) -> IndustryCode:
    """Find one industry by description, matched case-insensitively.

    Use this when you know the industry by name and want whatever code it carries
    in the scheme you resolved, which is the portable way to write a sample.
    """
    wanted = description.casefold()
    matches = [i for i in industries if i.description.casefold() == wanted]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise LookupError(
            f"No industry named '{description}' in this Aggregation Scheme. "
            f"Print the industry list to see the available descriptions."
        )
    raise LookupError(
        f"'{description}' matches {len(matches)} industries in this Aggregation "
        f"Scheme; use the code instead."
    )
