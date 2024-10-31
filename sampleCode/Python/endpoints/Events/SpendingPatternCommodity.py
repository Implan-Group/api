# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
