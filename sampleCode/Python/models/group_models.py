from uuid import UUID


class GroupEvent:
    def __init__(self,
                 event_id: UUID,
                 scaling_factor: float = 1.0):
        self.event_id = event_id
        self.scaling_factor = scaling_factor


class Group:
    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str,
                 dollar_year: int | None,
                 dataset_id: int | None,
                 group_events: list[GroupEvent],
                 hash_id: str | None = None,
                 urid: int | None = None,
                 user_model_id: int | None = None,
                 model_id: int | None = None,
                 scaling_factor: float = 1.0):
        self.id = id
        self.project_id = project_id
        self.hash_id = hash_id
        self.urid = urid
        self.user_model_id = user_model_id
        self.model_id = model_id
        self.title = title
        self.dollar_year = dollar_year
        self.dataset_id = dataset_id
        self.group_events = group_events
        self.scaling_factor = scaling_factor
