"""Regions: the geographies an impact is measured in.

A Region in IMPLAN is not just a place, it is a place within one Aggregation
Scheme and one Dataset. The same county has a different `hash_id` in the 528 and
546 schemes, and in the 2023 and 2024 datasets, because the underlying economic
model differs.

Prefer `hash_id` when you have a choice. `urid` still works and appears in older
examples, but HashId is the identifier IMPLAN is standardizing on.

Wiki: Regions - https://github.com/Implan-Group/api/wiki/Regions
"""

import dataclasses
import enum

from utilities.json_helper import ApiModel


class RegionType(str, enum.Enum):
    """The values accepted by the `regionTypeFilter` parameter.

    Read them from `GET /api/v1/region/RegionTypes` rather than hardcoding, which
    is what the Regions workflow demonstrates. They are listed here so editors can
    complete them and so a typo fails in Python rather than as an empty result.

    For Canadian data, `STATE` filters to Provinces and `COUNTY` to Economic
    Regions.
    """

    COUNTRY = "Country"
    STATE = "State"
    MSA = "Msa"
    COUNTY = "County"
    CONGRESSIONAL_DISTRICT = "CongressionalDistrict"
    ZIPCODE = "Zipcode"


class ModelBuildStatus(str, enum.Enum):
    """Where a region's economic model is in the build process.

    A newly combined region starts at `NEW` and is only usable at `COMPLETE`.
    Anything else means waiting, and `ERROR` means it will never finish.
    """

    NEW = "New"
    IN_PROGRESS = "InProgress"
    COMPLETE = "Complete"
    ERROR = "Error"


@dataclasses.dataclass(kw_only=True)
class Region(ApiModel):
    """One region, as the API returns it.

    The identifier fields are populated selectively: an IMPLAN-defined region has a
    `urid`, a region you combined yourself has a `user_model_id` and no `fips_code`,
    and both have a `hash_id`.
    """

    hash_id: str = ""
    urid: int | None = None
    user_model_id: int | None = None
    description: str = ""
    model_id: int | None = None
    model_build_status: str = ""

    # Totals for the region, useful as a sanity check that you picked the right one.
    employment: float | None = None
    output: float | None = None
    value_added: float | None = None

    aggregation_scheme_id: int | None = None
    dataset_id: int | None = None
    dataset_description: str = ""

    # Geographic codes, whichever applies: FIPS in the US, province in Canada, M49
    # internationally.
    fips_code: str | None = None
    province_code: str | None = None
    m49_code: str | None = None
    geo_id: str | None = None
    sgc_fuller_code: str | None = None

    region_type: str = ""
    region_type_description: str = ""
    has_accessible_children: bool = False

    # Whether this region can take part in a multi-regional (MRIO) analysis. The
    # MrioProject workflow checks this before building a project.
    is_mrio_allowed: bool = False

    @property
    def is_built(self) -> bool:
        """True when the economic model is ready to run impacts against."""
        return self.model_build_status == ModelBuildStatus.COMPLETE.value

    @property
    def is_user_defined(self) -> bool:
        """True for a region you combined or customized, rather than an IMPLAN one."""
        return self.user_model_id is not None

    def describe(self) -> str:
        """One line naming the region and its identifiers, for the console."""
        parts = [f"{self.description or '(unnamed)'}"]
        parts.append(f"hashId={self.hash_id}")
        if self.urid is not None:
            parts.append(f"urid={self.urid}")
        if self.model_build_status:
            parts.append(self.model_build_status)
        return "  ".join(parts)


@dataclasses.dataclass(kw_only=True)
class CombineRegionRequest(ApiModel):
    """The body for combining two or more regions into one.

    Supply the regions through `hash_ids`, `urids`, or both; two or more regions
    are required between them. HashId is the identifier IMPLAN is standardizing
    on, so these samples use it. The description becomes the new region's name
    and has to be unique for your account, which is why the samples put a
    timestamp in it.

    Regions being combined must come from the same dataset, must not overlap, and
    must not nest inside one another: a state and a county within it cannot be
    combined.
    """

    description: str
    hash_ids: list[str] = dataclasses.field(default_factory=list)
    urids: list[int] = dataclasses.field(default_factory=list)
