"""Spending patterns: how a dollar moves through a supply chain.

A spending pattern is a list of commodities with the share of a dollar that goes to
each. IMPLAN supplies a default pattern for every industry and institution, and you
can read it, change individual coefficients, and send it back as part of an event.

Wiki: Spending Patterns
https://github.com/Implan-Group/api/wiki/Spending-Patterns
"""

import dataclasses
import enum

from utilities.json_helper import ApiModel


class SpendingPatternType(str, enum.Enum):
    """Which family of spending pattern to read.

    `INSTITUTION` patterns additionally require a region, because government and
    household spending varies by where it happens.
    """

    INDUSTRY = "Industry"
    INSTITUTION = "Institution"
    CUSTOM = "Custom"
    HOUSEHOLD = "Household"


@dataclasses.dataclass(kw_only=True)
class SpendingPatternCommodity(ApiModel):
    """One commodity within a spending pattern, and the share spent on it.

    `coefficient` is that share, from 0 to 1, and the coefficients across a pattern
    sum to 1. Change one and set `is_user_coefficient` so IMPLAN knows the value is
    yours rather than its own.

    `local_purchase_percentage` is how much of this commodity is bought inside the
    region. Leave it at 1.0 to assume everything is local, or set `is_sam_value` to
    have IMPLAN substitute the region's own trade data, which is usually the more
    defensible choice.
    """

    commodity_code: int
    commodity_description: str = ""
    coefficient: float | None = None
    is_sam_value: bool = False
    is_user_coefficient: bool = False
    local_purchase_percentage: float = 1.0

    def describe(self) -> str:
        """One line naming the commodity and its share, for the console."""
        share = "" if self.coefficient is None else f"{self.coefficient:.6f}"
        return f"{self.commodity_code:>5}  {share:>10}  {self.commodity_description}"


@dataclasses.dataclass(kw_only=True)
class SpendingPattern(ApiModel):
    """A spending pattern as the API returns it.

    The shape varies a little by pattern type, so the commodity list is read
    explicitly and anything else the endpoint returned stays in `extra`.
    """

    commodities: list[SpendingPatternCommodity] = dataclasses.field(
        default_factory=list
    )

    @classmethod
    def from_api(cls, payload) -> "SpendingPattern":
        """Read a pattern, accepting either a bare array or an object holding one."""
        if isinstance(payload, list):
            # Some pattern endpoints answer with the commodity array directly.
            return cls(
                commodities=SpendingPatternCommodity.list_from_api(payload),
                extra={},
            )

        rest = dict(payload)
        raw_commodities = (
            rest.pop("commodities", None)
            or rest.pop("spendingPatternCommodities", None)
            or []
        )
        instance = super().from_api(rest)
        instance.commodities = SpendingPatternCommodity.list_from_api(raw_commodities)
        return instance
