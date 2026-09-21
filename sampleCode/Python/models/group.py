"""Groups: where and when an event happens.

An Event says what changed. A Group pairs one region and one dollar year with the
events that apply there. Running the same events in three states means three
groups, which is the MultiEventToMultiGroup workflow.

Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups
"""

import dataclasses
import uuid

from utilities.json_helper import ApiModel


@dataclasses.dataclass(kw_only=True)
class GroupEvent(ApiModel):
    """The link between a Group and one of the Project's Events.

    `scaling_factor` multiplies the event's values inside this group. It is a
    multiplier and not a percentage: 1 leaves the event alone, 0.55 more than halves
    it, and 5000 analyzes it five thousand times over. Two decimal places are kept.

    Group and event scaling compound, so an event scaled 3000 inside a group scaled
    5 is analyzed at 15000. Scale at one level or the other, not both. To leave an
    event out of a group, remove it rather than scaling it to zero.
    """

    event_id: uuid.UUID | str
    scaling_factor: float = 1.0


@dataclasses.dataclass(kw_only=True)
class Group(ApiModel):
    """One region and dollar year, with the events that apply to it.

    Supply exactly one region identifier: `hash_id`, `urid`, `user_model_id`, or
    `model_id`. HashId is the one to use.

    `dollar_year` has no server-side default, and a group saved without one
    produces an impact run that never attaches, so always set it. The samples use
    the current calendar year.
    """

    title: str = ""
    id: uuid.UUID | str | None = None
    project_id: uuid.UUID | str | None = None

    # Exactly one of these four identifies the region. HashId is preferred.
    hash_id: str | None = None
    urid: int | None = None
    user_model_id: int | None = None
    model_id: int | None = None

    dollar_year: int | None = None
    dataset_id: int | None = None
    scaling_factor: float = 1.0

    group_events: list[GroupEvent] = dataclasses.field(default_factory=list)

    @classmethod
    def from_api(cls, payload) -> "Group":
        """Read a group, deserializing its nested event links properly."""
        rest = dict(payload)
        raw_events = rest.pop("groupEvents", None) or []
        instance = super().from_api(rest)
        instance.group_events = GroupEvent.list_from_api(raw_events)
        return instance

    def describe(self) -> str:
        """One line naming the group, for the console."""
        return (
            f"{self.title}  id={self.id}  "
            f"hashId={self.hash_id}  events={len(self.group_events)}"
        )
