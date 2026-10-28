"""Events: the economic changes being analyzed.

An Event says what happened, a Group says where and when, and an Impact Run
combines them. Every event carries `impact_event_type`, and that value decides
which other fields the API expects, so the models here are one class per type
rather than one class with every field on it.

Only the types the workflows use are modeled. Adding another is a matter of
copying the nearest class, changing the type and the fields, and registering it in
`EVENT_TYPES` at the bottom so responses deserialize to it.

Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
Support: Explaining Event Types
https://support.implan.com/hc/en-us/articles/360051087394-Quick-Start-Guide-4-Impacts
"""

import dataclasses
import enum
import uuid
from typing import Any

from utilities.json_helper import ApiModel
from models.spending_pattern import SpendingPatternCommodity


class EventType(str, enum.Enum):
    """The event types the API accepts.

    Not every type is valid in every Project: the international types are only
    valid in an international Aggregation Scheme, and `INDUSTRY_IMPACT_ANALYSIS`
    and `INDUSTRY_PROPRIETOR_INCOME` are not valid in one. Ask the Project which
    types it accepts with `endpoints.events.get_event_types` rather than assuming.
    """

    INDUSTRY_OUTPUT = "IndustryOutput"
    INDUSTRY_EMPLOYMENT = "IndustryEmployment"
    INDUSTRY_EMPLOYEE_COMPENSATION = "IndustryEmployeeCompensation"
    INDUSTRY_PROPRIETOR_INCOME = "IndustryProprietorIncome"
    COMMODITY_OUTPUT = "CommodityOutput"
    LABOR_INCOME = "LaborIncome"
    HOUSEHOLD_INCOME = "HouseholdIncome"
    INDUSTRY_CONTRIBUTION_ANALYSIS = "IndustryContributionAnalysis"
    INDUSTRY_IMPACT_ANALYSIS = "IndustryImpactAnalysis"
    CUSTOM_INDUSTRY_IMPACT_ANALYSIS = "CustomIndustryImpactAnalysis"
    INTERNATIONAL_INDUSTRY_IMPACT_ANALYSIS = "InternationalIndustryImpactAnalysis"
    CUSTOM_INTERNATIONAL_INDUSTRY_IMPACT_ANALYSIS = (
        "CustomInternationalIndustryImpactAnalysis"
    )
    INDUSTRY_SPENDING_PATTERN = "IndustrySpendingPattern"
    INSTITUTIONAL_SPENDING_PATTERN = "InstitutionalSpendingPattern"
    HOUSEHOLD_SPENDING_PATTERN = "HouseholdSpendingPattern"
    CUSTOM_SPENDING_PATTERN = "CustomSpendingPattern"


class MarginType(str, enum.Enum):
    """Whether a value is the price the producer received or the buyer paid.

    Only retail and wholesale industries, and commodities sold through them, can be
    margined. Setting `PURCHASER_PRICE` on anything else is reverted to
    `PRODUCER_PRICE` before the impact runs.

    Support: Margins - https://support.implan.com/hc/en-us/articles/115009506007
    """

    PRODUCER_PRICE = "ProducerPrice"
    PURCHASER_PRICE = "PurchaserPrice"


class SpendingPatternValueType(str, enum.Enum):
    """How a spending-pattern event's value should be read.

    `INTERMEDIATE_EXPENDITURE` spends the whole value across the pattern's
    commodities. `OUTPUT` multiplies it by the industry's gross absorption first,
    so only the portion actually spent on intermediate inputs flows through.
    """

    INTERMEDIATE_EXPENDITURE = "IntermediateExpenditure"
    OUTPUT = "Output"


@dataclasses.dataclass(kw_only=True)
class Event(ApiModel):
    """Fields shared by every event type.

    Leave `id` unset when creating: the API generates it and returns it. `title`
    must be unique among the Project's events and must avoid an ampersand and the
    characters `| ; % * ? ! = ' " ^ #`.

    `tags` are free text and are how results get filtered later; see the
    AdvancedEvents workflow. Note that updating an event merges tags rather than
    replacing them, so a tag can be added but not removed through an update.
    """

    impact_event_type: str = ""
    title: str = ""
    id: uuid.UUID | str | None = None
    project_id: uuid.UUID | str | None = None
    tags: list[str] = dataclasses.field(default_factory=list)

    def describe(self) -> str:
        """One line naming the event, for the console."""
        return f"{self.title}  [{self.impact_event_type}]  id={self.id}"


@dataclasses.dataclass(kw_only=True)
class IndustryOutputEvent(Event):
    """A change in what an industry produces, stated in dollars of output.

    The most common event type and the right default when you know a dollar figure
    and the industry that earned it. Supply any one of output, employment,
    employee compensation, or proprietor income; IMPLAN estimates the rest from the
    industry's averages for the region.

    Support: Industry Events
    https://support.implan.com/hc/en-us/articles/360051441834-Industry-Events
    """

    impact_event_type: str = EventType.INDUSTRY_OUTPUT.value
    industry_code: int = 0
    output: float | None = None
    employment: float | None = None
    employee_compensation: float | None = None
    proprietor_income: float | None = None

    # Margins apply to retail and wholesale industries only.
    margin_type: str | None = None
    percentage: float | None = None

    # The data year the margins come from, when margins are applied.
    dataset_id: int | None = None


@dataclasses.dataclass(kw_only=True)
class CommodityOutputEvent(Event):
    """A change in demand for a commodity rather than for an industry's output.

    Use this when you know what was bought rather than who produced it. IMPLAN
    decides which industries supply the commodity locally.
    """

    impact_event_type: str = EventType.COMMODITY_OUTPUT.value
    commodity_code: int = 0
    output: float | None = None
    margin_type: str | None = None


@dataclasses.dataclass(kw_only=True)
class HouseholdIncomeEvent(Event):
    """A change in income for one household income bracket.

    `household_income_code` is a specification code, not an industry code. Read the
    valid ones from `endpoints.events.get_event_specifications`; they look like
    `10002 - Households 15-30k`.

    Support: Household Income Events
    https://support.implan.com/hc/en-us/articles/360052212413
    """

    impact_event_type: str = EventType.HOUSEHOLD_INCOME.value
    household_income_code: int = 0
    value: float | None = None


@dataclasses.dataclass(kw_only=True)
class IndustryContributionAnalysisEvent(Event):
    """The contribution an existing industry already makes to a region.

    This is a different question from an impact. An impact asks what would change
    if new activity arrived; a contribution asks how much of the current economy
    rests on an industry that is already there. The analysis constrains the
    industry from buying from itself so its own output is not counted twice.

    Set `output` to a dollar figure, or set `is_output_percentage` and give
    `output` as a share of the industry's regional output from 0 to 1.

    Support: ICA: Introduction to Industry Contribution Analysis
    https://support.implan.com/hc/en-us/articles/360025854654
    """

    impact_event_type: str = EventType.INDUSTRY_CONTRIBUTION_ANALYSIS.value
    industry_code: int = 0
    output: float | None = None
    is_output_percentage: bool = False


@dataclasses.dataclass(kw_only=True)
class IndustryImpactAnalysisEvent(Event):
    """An industry event where you know the production function, not just a total.

    Where an Industry Output event gives IMPLAN one number and lets it estimate the
    rest, this type lets you state employment, compensation, proprietor income,
    taxes, and intermediate inputs yourself. Use it when you have the operating
    statement for the thing being modeled, such as a hospital or a university.

    Support: Industry Impact Analysis (Detailed) Events
    https://support.implan.com/hc/en-us/articles/4414451454491
    """

    impact_event_type: str = EventType.INDUSTRY_IMPACT_ANALYSIS.value
    industry_code: int = 0

    intermediate_inputs: float | None = None
    total_output: float | None = None
    employee_compensation: float | None = None
    proprietor_income: float | None = None
    total_labor_income: float | None = None
    other_property_income: float | None = None
    tax_on_production_and_imports: float | None = None

    wage_and_salary_employment: float | None = None
    proprietor_employment: float | None = None
    total_employment: float | None = None

    # Share of intermediate inputs bought inside the region, 0 to 1. Leave at 1.0
    # when everything is local, or set `is_sam` to let IMPLAN use the region's own
    # trade data instead.
    local_purchase_percentage: float | None = 1.0
    is_sam: bool = False

    # Which data year's spending pattern to spend the intermediate inputs through.
    spending_pattern_dataset_id: int | None = None
    spending_pattern_value_type: str = SpendingPatternValueType.INTERMEDIATE_EXPENDITURE.value
    spending_pattern_commodities: list[SpendingPatternCommodity] = dataclasses.field(
        default_factory=list
    )

    # Returned by the API on read. Setting either employment flag requires
    # conversion data to exist for the Industry Set, so leave them alone unless you
    # know the region has it.
    is_local_employee_compensation: bool = False
    is_fte_employment: bool = False
    is_wage_and_salary: bool = False
    is_contribution_analysis: bool = False


@dataclasses.dataclass(kw_only=True)
class IndustrySpendingPatternEvent(Event):
    """An industry's purchases of goods and services, excluding labor.

    Use this to model a buyer rather than a producer: the event spends money
    through an industry's supply chain without adding any direct output of its own.
    The commodity list can be left empty to use IMPLAN's default pattern, or
    supplied with edited coefficients, which is what the AdvancedEvents workflow
    demonstrates.

    Support: Industry Spending Pattern Events
    https://support.implan.com/hc/en-us/articles/360052212933
    """

    impact_event_type: str = EventType.INDUSTRY_SPENDING_PATTERN.value
    industry_code: int = 0
    output: float | None = None

    local_purchase_percentage: float | None = 1.0
    is_sam: bool = False

    spending_pattern_dataset_id: int | None = None
    spending_pattern_region_urid: int | None = None
    spending_pattern_value_type: str = SpendingPatternValueType.OUTPUT.value
    spending_pattern_commodities: list[SpendingPatternCommodity] = dataclasses.field(
        default_factory=list
    )


# Maps the API's `impactEventType` to the class that models it. Types not listed
# deserialize to the base `Event`, which carries the shared fields and keeps
# everything else in `extra`.
EVENT_TYPES: dict[str, type[Event]] = {
    EventType.INDUSTRY_OUTPUT.value: IndustryOutputEvent,
    EventType.COMMODITY_OUTPUT.value: CommodityOutputEvent,
    EventType.HOUSEHOLD_INCOME.value: HouseholdIncomeEvent,
    EventType.INDUSTRY_CONTRIBUTION_ANALYSIS.value: IndustryContributionAnalysisEvent,
    EventType.INDUSTRY_IMPACT_ANALYSIS.value: IndustryImpactAnalysisEvent,
    EventType.INDUSTRY_SPENDING_PATTERN.value: IndustrySpendingPatternEvent,
}


def event_from_api(payload: dict[str, Any]) -> Event:
    """Build the right event class from a response, whatever type it turns out to be.

    `GET /api/v1/impact/project/{projectId}/event` returns a mixed list, so the
    type has to be read from each item before it can be deserialized.
    """
    event_type = payload.get("impactEventType", "")
    model = EVENT_TYPES.get(event_type, Event)
    return model.from_api(payload)


def events_from_api(payload: Any) -> list[Event]:
    """Build a list of events from a response array."""
    if not payload:
        return []
    return [event_from_api(item) for item in payload]
