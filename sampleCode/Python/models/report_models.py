from models.enums import ImpactType

class ImpactResultsExportRequest:
    """

    """

    def __init__(self,
                dollar_year: int,
                regions: list[str] | None = None,
                 impacts: list[ImpactType] | None = None,
                 group_names: list[str] | None = None,
                 event_names: list[str] | None = None,
                 event_tags: list[str] | None = None,
                 ):
        self.dollar_year = dollar_year
        self.regions = regions if regions is not None else []
        self.impacts = impacts if impacts is not None else []
        self.group_names = group_names if group_names is not None else []
        self.event_names = event_names if event_names is not None else []
        self.event_tags = event_tags if event_tags is not None else []