import uuid

from utilities.python_helper import uuid_empty


class Project:
    """
    The model definition for adding and updating Projects
    """

    def __init__(self,
                 title: str,
                 aggregation_scheme_id: int,
                 household_set_id: int,
                 is_mrio: bool = False,
                 id: uuid.UUID | None = None,
                 folder_id: int | None = None,
                 last_impact_run_id: int | None = None
                 ):
        # If the Id is unspecified, default to empty
        self.id = id if id is not None else uuid_empty()
        self.title = title
        self.aggregation_scheme_id = aggregation_scheme_id
        self.household_set_id = household_set_id
        self.is_mrio = is_mrio
        self.folder_id = folder_id
        self.last_impact_run_id = last_impact_run_id
