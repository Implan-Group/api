class AggregationScheme:
    """
    The Model for an Aggregation Scheme
    """

    def __init__(self,
                 id: int,
                 description: str,
                 industry_set_id: int,
                 household_set_ids: list[int],
                 map_code: str,
                 status: str):
        self.id = id
        self.description = description
        self.industry_set_id = industry_set_id
        self.household_set_ids = household_set_ids
        self.map_code = map_code
        self.status = status
