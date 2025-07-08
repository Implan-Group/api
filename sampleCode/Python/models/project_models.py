import uuid


class Project:
    def __init__(self,
                 id: uuid.UUID,
                 title: str,
                 aggregation_scheme_id: int,
                 household_set_id: int,
                 is_mrio: bool = False,
                 folder_id: int | None = None,
                 last_impact_run_id: int | None = None
                 ):
        self.id = id if id is not None else uuid.UUID(int=0)
        self.title = title
        self.aggregation_scheme_id = aggregation_scheme_id
        self.household_set_id = household_set_id
        self.is_mrio = is_mrio
        self.folder_id = folder_id
        self.last_impact_run_id = last_impact_run_id
