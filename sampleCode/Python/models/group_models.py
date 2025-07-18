from uuid import UUID
from utilities.prelude import uuid_empty


class GroupEvent:
    def __init__(self,
                 event_id: UUID,
                 scaling_factor: float = 1.0):
        self.event_id = event_id
        self.scaling_factor = scaling_factor


class Group:
    def __init__(self,
                 title: str,
                 dollar_year: int | None,
                 dataset_id: int | None,
                 group_events: list[GroupEvent],
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 hash_id: str | None = None,
                 urid: int | None = None,
                 user_model_id: int | None = None,
                 model_id: int | None = None,
                 scaling_factor: float = 1.0):
        self.id = id if id is not None else uuid_empty()
        self.project_id = project_id if project_id is not None else uuid_empty()
        self.hash_id = hash_id
        self.urid = urid
        self.user_model_id = user_model_id
        self.model_id = model_id
        self.title = title
        self.dollar_year = dollar_year
        self.dataset_id = dataset_id
        self.group_events = group_events
        self.scaling_factor = scaling_factor
