class SpendingPatternCommodity:
    def __init__(self, coefficient=None, commodity_code=0, commodity_description="", is_sam_value=False, is_user_coefficient=False, local_purchase_percentage=1.0):
        self.coefficient = coefficient
        self.commodity_code = commodity_code
        self.commodity_description = commodity_description
        self.is_sam_value = is_sam_value
        self.is_user_coefficient = is_user_coefficient
        self.local_purchase_percentage = local_purchase_percentage

    def to_dict(self):
        return {
            "coefficient": self.coefficient,
            "commodityCode": self.commodity_code,
            "commodityDescription": self.commodity_description,
            "isSamValue": self.is_sam_value,
            "isUserCoefficient": self.is_user_coefficient,
            "localPurchasePercentage": self.local_purchase_percentage
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            coefficient=data.get("coefficient"),
            commodity_code=data.get("commodityCode", 0),
            commodity_description=data.get("commodityDescription", ""),
            is_sam_value=data.get("isSamValue", False),
            is_user_coefficient=data.get("isUserCoefficient", False),
            local_purchase_percentage=data.get("localPurchasePercentage", 1.0)
        )
