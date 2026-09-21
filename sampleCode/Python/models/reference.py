"""Reference data: the identifiers everything else is built on.

Nothing in the Impact API stands on its own. An Industry Code only means something
inside an Industry Set, a Dataset only exists for an Aggregation Scheme, and a
Region is unique to a scheme and dataset together. These models carry those
identifiers, and `Identifiers` is the resolved bundle every workflow starts from.

Wiki: Aggregation Schemes - https://github.com/Implan-Group/api/wiki/Aggregation-Schemes
Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets
Wiki: Industries - https://github.com/Implan-Group/api/wiki/Industries
"""

import dataclasses
import enum

from utilities.json_helper import ApiModel


class MapCode(str, enum.Enum):
    """Which country's data an Aggregation Scheme covers."""

    US = "US"
    CANADA = "CAN"
    INTERNATIONAL = "INTL"


@dataclasses.dataclass(kw_only=True)
class IndustrySet(ApiModel):
    """The full list of industries for a country, in one vintage.

    IMPLAN revises its industry list periodically, so several sets coexist: the US
    has had 536, 546, and 528 industries. Exactly one set is flagged `is_default`,
    and that is the current one. The descriptions carry a country in parentheses,
    for example `528 Industries (latest US)`, so match on the id rather than on the
    text wherever you can.
    """

    id: int
    description: str = ""
    default_aggregation_scheme_id: int | None = None
    active_status: bool | None = None
    is_default: bool | None = None
    map_type_id: int | None = None
    is_naics_compatible: bool = False


@dataclasses.dataclass(kw_only=True)
class AggregationScheme(ApiModel):
    """How industries are grouped for a Project.

    An Unaggregated scheme keeps every industry separate; the NAICS schemes roll
    them up. A Project's scheme is fixed at creation and cannot be changed, and
    every region identifier and industry code you use has to come from the same
    scheme.

    `status` is `Complete` when the scheme is ready to run impacts against.
    """

    id: int
    description: str = ""
    industry_set_id: int = 0
    household_set_ids: list[int] = dataclasses.field(default_factory=list)
    map_code: str = ""
    status: str = ""


@dataclasses.dataclass(kw_only=True)
class Dataset(ApiModel):
    """One data year, within one Aggregation Scheme.

    Dataset ids are specific to a scheme and are not ordered by year, so an id
    taken from another scheme is either rejected or, worse, silently resolves to a
    different year. Always read the list for the scheme you are using and take the
    entry flagged `is_default`.
    """

    id: int
    description: str = ""
    is_default: bool = False


@dataclasses.dataclass(kw_only=True)
class IndustryCode(ApiModel):
    """One industry within an Industry Set.

    The same `code` means different industries in different sets: 509 is
    Full-service restaurants in the 546 set and Federal electric utilities in the
    528 set. Workflows here check the description alongside the code for that
    reason.
    """

    id: int = 0
    code: int
    description: str = ""


@dataclasses.dataclass(kw_only=True)
class Specification(ApiModel):
    """A valid code for an event type that needs one.

    Household Income events, for instance, take an income bracket such as
    `10002 - Households 15-30k` rather than an industry.
    """

    code: str
    name: str = ""


@dataclasses.dataclass(kw_only=True)
class Identifiers:
    """Everything a workflow needs to address data, resolved from the API.

    Built by `endpoints.identifiers.resolve`. Holding these together means a
    workflow asks for them once and then passes one object around, instead of
    threading four integers through every call.
    """

    map_code: MapCode
    industry_set: IndustrySet
    aggregation_scheme: AggregationScheme
    dataset: Dataset
    household_set_id: int

    @property
    def aggregation_scheme_id(self) -> int:
        return self.aggregation_scheme.id

    @property
    def dataset_id(self) -> int:
        return self.dataset.id

    def describe(self) -> str:
        """A short block naming everything that was resolved, for the console."""
        return (
            f"  Map code:          {self.map_code.value}\n"
            f"  Industry Set:      {self.industry_set.id} - {self.industry_set.description}\n"
            f"  Aggregation Scheme:{self.aggregation_scheme.id} - {self.aggregation_scheme.description}\n"
            f"  Dataset:           {self.dataset.id} - {self.dataset.description}\n"
            f"  Household Set:     {self.household_set_id}"
        )
