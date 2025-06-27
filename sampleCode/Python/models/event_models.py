import uuid
from enum import Enum


from models.commodity_models import SpendingPatternCommodity
from models.enums import EventType, SpendingPatternValueType, MarginType
from uuid import UUID


class Event:
    """
    This is the base Event Model used for Impact Events
    All other Event Types share these same base fields
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 impact_event_type: EventType,
                 title: str | None,
                 tags: list[str] | None = None):
        self.id = id
        self.project_id = project_id
        self.impact_event_type = impact_event_type
        self.title = title
        self.tags = tags if tags is not None else []


class HouseholdIncomeEvent(Event):
    """
    A Household Income Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str | None,
                 household_income_code: int,
                 value: float | None,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.HOUSEHOLD_INCOME, title, tags)
        self.household_income_code = household_income_code
        self.value = value


class IndustryEmployeeCompensationEvent(Event):
    """
    An Industry Employee Compensation Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.INDUSTRY_EMPLOYEE_COMPENSATION, title, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code


class IndustryEmploymentEvent(Event):
    """
    An Industry Employment Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.INDUSTRY_EMPLOYMENT, title, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code


class IndustryImpactAnalysisEvent(Event):
    """
    An Industry Impact Analysis Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str,
                 industry_code: int,
                 is_sam: bool,
                 spending_pattern_dataset_id: int | None,
                 spending_pattern_value_type: SpendingPatternValueType,
                 is_fte_employment: bool = False,
                 is_wage_and_salary: bool = False,
                 intermediate_inputs: float | None = None,
                 total_employment: float | None = None,
                 employee_compensation: float | None = None,
                 proprietor_income: float | None = None,
                 wage_and_salary_employment: float | None = None,
                 proprietor_employment: float | None = None,
                 total_labor_income: float | None = None,
                 other_property_income: float | None = None,
                 tax_on_production_and_imports: float | None = None,
                 total_output: float | None = None,
                 spending_pattern_commodities: list[SpendingPatternCommodity] | None = None,
                 is_local_employee_compensation: bool = False,
                 local_purchase_percentage: float | None = 1.0,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.INDUSTRY_IMPACT_ANALYSIS, title, tags)
        self.industry_code = industry_code
        self.intermediate_inputs = intermediate_inputs
        self.total_employment = total_employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.wage_and_salary_employment = wage_and_salary_employment
        self.proprietor_employment = proprietor_employment
        self.total_labor_income = total_labor_income
        self.other_property_income = other_property_income
        self.tax_on_production_and_imports = tax_on_production_and_imports
        self.total_output = total_output
        self.is_sam = is_sam
        self.spending_pattern_dataset_id = spending_pattern_dataset_id
        self.spending_pattern_value_type = spending_pattern_value_type
        self.is_fte_employment = is_fte_employment
        self.is_wage_and_salary = is_wage_and_salary
        self.spending_pattern_commodities = spending_pattern_commodities if spending_pattern_commodities is not None else []
        self.is_local_employee_compensation = is_local_employee_compensation
        self.local_purchase_percentage = local_purchase_percentage


class IndustryOutputEvent(Event):
    """
    An Industry Output Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str,
                 industry_code: int,
                 output: float | None = None,
                 employment: float | None = None,
                 employee_compensation: float | None = None,
                 proprietor_income: float | None = None,
                 margin_type: MarginType | None = None,
                 percentage: float | None = None,
                 dataset_id: int | None = None,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.INDUSTRY_OUTPUT, title, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
        self.margin_type = margin_type
        self.percentage = percentage
        self.dataset_id = dataset_id


class IndustryProprietorIncomeEvent(Event):
    """
    An Industry Proprietor Income Event
    """

    def __init__(self,
                 id: UUID,
                 project_id: UUID,
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 tags: list[str] | None = None):
        super().__init__(id, project_id, EventType.INDUSTRY_PROPRIETOR_INCOME, title, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
