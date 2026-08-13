from models.enums import EventType, SpendingPatternValueType, MarginType
from uuid import UUID
from models.spending_pattern_commodity import SpendingPatternCommodity
from utilities.prelude import uuid_empty


# This file contains the Models for _some_ of the different Event Types that can be used
# All Events should use `Event` as a baseclass for common fields and to work with the `event_endpoints`


class Event:
    """
    This is the base Event Model used for Impact Events
    All other Event Types share these same base fields
    """

    def __init__(self,
                 impact_event_type: EventType,
                 title: str | None,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 **kwargs): # kwargs lets us use Event as the only type for a response rather than always having to specify the exact type
        self.impact_event_type = impact_event_type
        self.title = title
        self.id = id if id is not None else uuid_empty()
        self.project_id = project_id if project_id is not None else uuid_empty()
        self.tags = tags if tags is not None else []


class HouseholdIncomeEvent(Event):
    """
    A Household Income Event
    """

    def __init__(self,
                 title: str | None,
                 household_income_code: int,
                 value: float | None,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.HOUSEHOLD_INCOME.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to a Household Income Event"

        super().__init__(EventType.HOUSEHOLD_INCOME, title, id, project_id, tags)
        self.household_income_code = household_income_code
        self.value = value


class IndustryEmployeeCompensationEvent(Event):
    """
    An Industry Employee Compensation Event
    """

    def __init__(self,
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.INDUSTRY_EMPLOYEE_COMPENSATION.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to an Industry Employee Compensation Event"

        super().__init__(EventType.INDUSTRY_EMPLOYEE_COMPENSATION, title, id, project_id, tags)
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
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.INDUSTRY_EMPLOYMENT.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to an Industry Employment Event"

        super().__init__(EventType.INDUSTRY_EMPLOYMENT, title, id, project_id, tags)
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
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.INDUSTRY_IMPACT_ANALYSIS.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to an Industry Impact Analysis Event"

        super().__init__(EventType.INDUSTRY_IMPACT_ANALYSIS, title, id, project_id, tags)
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
                 title: str,
                 industry_code: int,
                 output: float | None = None,
                 employment: float | None = None,
                 employee_compensation: float | None = None,
                 proprietor_income: float | None = None,
                 margin_type: MarginType | None = None,
                 percentage: float | None = None,
                 dataset_id: int | None = None,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.INDUSTRY_OUTPUT.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to an Industry Output Event"

        super().__init__(EventType.INDUSTRY_OUTPUT, title, id, project_id, tags)
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
                 title: str | None,
                 output: float | None,
                 employment: float | None,
                 employee_compensation: float | None,
                 proprietor_income: float | None,
                 industry_code: int,
                 id: UUID | None = None,
                 project_id: UUID | None = None,
                 tags: list[str] | None = None,
                 impact_event_type: EventType | None = None):
        # Verify that any passed in impact_event_type is the one we're expecting
        if impact_event_type is not None and impact_event_type != EventType.INDUSTRY_PROPRIETOR_INCOME.value:
            raise f"Attempting to map Impact Event Type {impact_event_type} to an Industry Proprietor Income Event"

        super().__init__(EventType.INDUSTRY_PROPRIETOR_INCOME, title, id, project_id, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
