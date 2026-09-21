"""Impact runs and their results.

An Impact Run is one execution of a Project. It is started with a POST, it takes a
few minutes, and its status is polled until it reaches a terminal state. The
results are then read as CSV reports, filtered however you like.

Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results
"""

import dataclasses
import enum

from utilities.json_helper import ApiModel


class ImpactStatus(str, enum.Enum):
    """The states an impact run moves through.

    `COMPLETE` is the only one that means results can be read. `ERROR` and
    `USER_CANCELLED` are terminal failures: polling past them waits forever. A 404
    from the status endpoint is also terminal, and means the run never attached to
    a project, most often because a group was saved without a dollar year.
    """

    UNKNOWN = "Unknown"
    NEW = "New"
    IN_PROGRESS = "InProgress"
    READY_FOR_WAREHOUSE = "ReadyForWarehouse"
    COMPLETE = "Complete"
    ERROR = "Error"
    USER_CANCELLED = "UserCancelled"

    @property
    def is_terminal_failure(self) -> bool:
        """True when the run has stopped and will not produce results."""
        return self in (ImpactStatus.ERROR, ImpactStatus.USER_CANCELLED)


class ImpactType(str, enum.Enum):
    """The three effects an impact analysis separates.

    Direct is the activity itself, Indirect is its supply chain, and Induced is the
    household spending of everyone paid along the way.

    Support: Examining Results and Interpreting Direct, Indirect, and Induced Effects
    https://support.implan.com/hc/en-us/articles/360038799153
    """

    DIRECT = "Direct"
    INDIRECT = "Indirect"
    INDUCED = "Induced"


@dataclasses.dataclass(kw_only=True)
class ImpactResultsExportRequest(ApiModel):
    """Filters for the Estimated Growth Percentage report.

    Every list has to be present in the request, even when empty, so all five
    default to empty lists here rather than to `None`. `dollar_year` is required.

    This is the body of a GET request, which is unusual but is what the endpoint
    requires; see `endpoints.impact_results.get_estimated_growth_percentage`.
    """

    dollar_year: int
    regions: list[str] = dataclasses.field(default_factory=list)
    impacts: list[str] = dataclasses.field(default_factory=list)
    group_names: list[str] = dataclasses.field(default_factory=list)
    event_names: list[str] = dataclasses.field(default_factory=list)
    event_tags: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(kw_only=True)
class ResultFilters:
    """Optional filters shared by the CSV report endpoints.

    These go on the query string rather than in a body. Leaving one empty means no
    filter on that dimension.

    `year` overrides the dollar year the results are expressed in. Left unset, the
    API uses your account's dollar-year preference, falling back to the current
    calendar year, so the samples set it explicitly to keep runs reproducible.
    """

    year: int | None = None
    regions: list[str] = dataclasses.field(default_factory=list)
    impacts: list[str] = dataclasses.field(default_factory=list)
    groups: list[str] = dataclasses.field(default_factory=list)
    events: list[str] = dataclasses.field(default_factory=list)
    event_tags: list[str] = dataclasses.field(default_factory=list)

    def to_query(self) -> dict[str, object]:
        """Render the filters as query parameters, omitting the empty ones.

        `requests` turns a list value into a repeated parameter, which is the shape
        the API expects for these.
        """
        query: dict[str, object] = {}
        if self.year is not None:
            query["year"] = self.year
        if self.regions:
            query["regions"] = self.regions
        if self.impacts:
            query["impacts"] = self.impacts
        if self.groups:
            query["groups"] = self.groups
        if self.events:
            query["events"] = self.events
        if self.event_tags:
            query["eventTags"] = self.event_tags
        return query
