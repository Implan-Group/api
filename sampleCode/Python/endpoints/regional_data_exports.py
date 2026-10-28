"""Regional data exports: the data behind a region, rather than an impact result.

These endpoints describe a region's economy as it already is: what its industries
produce, what they buy, who they employ. They need no Project and no impact run,
only a built region.

They all take the region the same way, through one of `hashId`, `urid`, or
`userModelId` on the query string, and they all answer with CSV. That regularity is
why `get_export` below takes the report name as a parameter instead of there being
one function per report; the wiki's Regional Data Exports section lists the rest.

Wiki: Regional Data Exports
https://github.com/Implan-Group/api/wiki/Regional-Data-Exports
"""

from models.region import Region
from utilities.rest import ApiClient

# The two exports the samples name. Any other report from the wiki's Regional Data
# Exports section can be passed to `get_export` as a string. The GAMS file (wiki:
# Region Data - GAMS) takes an IMPLAN region into the General Algebraic Modeling
# System, which is why it saves as `.gms`. Support: Exporting Data from IMPLAN to
# GAMS, https://support.implan.com/hc/en-us/articles/360033706954
REGION_OVERVIEW_INDUSTRIES = "RegionOverviewIndustries"
GAMS_SINGLE_FILE = "region-general-algebraic-modeling-single-file"

# Reports whose natural file extension is not `.csv`.
_FILE_EXTENSIONS = {GAMS_SINGLE_FILE: ".gms"}


def file_extension_for(export_name: str) -> str:
    """The extension a given export should be saved with."""
    return _FILE_EXTENSIONS.get(export_name, ".csv")


def get_export(
    client: ApiClient,
    aggregation_scheme_id: int,
    export_name: str,
    region: Region | None = None,
    hash_id: str | None = None,
) -> str:
    """Download one regional data export for one region, as text.

    GET /api/v1/regions/export/{aggregationSchemeId}/{exportName}?hashId=...
    (wiki: Regional Data Exports)

    Pass either a `Region` or a `hash_id`. A 409 titled "Model not built" means
    the region's model has not finished building, or was never requested, rather
    than that the request was malformed. Build the region and ask again.

    `export_name` is the segment from the wiki page for the report you want, for
    example `RegionOverviewIndustries` or `StudyAreaDataIndustrySummary`.
    """
    if hash_id is None:
        if region is None:
            raise ValueError("Pass either a region or a hash_id.")
        hash_id = region.hash_id

    return client.get_text(
        f"/api/v1/regions/export/{aggregation_scheme_id}/{export_name}",
        params={"hashId": hash_id},
    )
