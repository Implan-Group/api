class IndustrySet:
    def __init__(self,
                 id: int,
                 description: str,
                 default_aggregation_scheme_id: int | None = None,
                 active_status: bool | None = None,
                 is_default: bool | None = None,
                 map_type_id: int | None = None,
                 is_naics_compatible: bool = False):
        self.id = id
        self.description = description
        self.default_aggregation_scheme_id = default_aggregation_scheme_id
        self.active_status = active_status
        self.is_default = is_default
        self.map_type_id = map_type_id
        self.is_naics_compatible = is_naics_compatible