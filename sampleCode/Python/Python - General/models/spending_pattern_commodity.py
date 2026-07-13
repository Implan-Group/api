class SpendingPatternCommodity:
    """
    The Model for a Spending Pattern Commodity
    """

    def __init__(self,
                 coefficient: float | None,
                 commodity_code: int,
                 commodity_description: str,
                 is_sam_value: bool,
                 is_user_coefficient: bool,
                 local_purchase_percentage: float = 1.0):
        self.coefficient = coefficient
        self.commodity_code = commodity_code
        self.commodity_description = commodity_description
        self.is_sam_value = is_sam_value
        self.is_user_coefficient = is_user_coefficient
        self.local_purchase_percentage = local_purchase_percentage
