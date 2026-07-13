from enum import Enum


# This file contains a collection of Enums that are used by the Impact API
# All Python Enum implementations should subclass `str` so that the `JsonHelper` utility can property translate them to and from
# their API string representations.


class EventType(str, Enum):
    """
    All the possible Event Types
    Note: Not all Event Types are available for all Projects, see `event_endpoints` and any of the Project Workflows
    """

    UNKNOWN = 0
    INDUSTRY_OUTPUT = 'IndustryOutput'
    INDUSTRY_EMPLOYMENT = 'IndustryEmployment'
    INDUSTRY_EMPLOYEE_COMPENSATION = 'IndustryEmployeeCompensation'
    INDUSTRY_PROPRIETOR_INCOME = 'IndustryProprietorIncome'
    COMMODITY_OUTPUT = 'CommodityOutput'
    LABOR_INCOME = 'LaborIncome'
    HOUSEHOLD_INCOME = 'HouseholdIncome'
    INDUSTRY_SPENDING_PATTERN_2018 = 'IndustrySpendingPattern2018'
    INDUSTRY_CONTRIBUTION_ANALYSIS = 'IndustryContributionAnalysis'
    INSTITUTIONAL_SPENDING_PATTERN_2018 = 'InstitutionalSpendingPattern2018'
    INDUSTRY_SPENDING_PATTERN_2019 = 'IndustrySpendingPattern2019'
    INDUSTRY_IMPACT_ANALYSIS = 'IndustryImpactAnalysis'
    INSTITUTIONAL_SPENDING_PATTERN_2019 = 'InstitutionalSpendingPattern2019'
    INSTITUTIONAL_SPENDING_PATTERN = 'InstitutionalSpendingPattern'
    INDUSTRY_SPENDING_PATTERN = 'IndustrySpendingPattern'
    CUSTOM_SPENDING_PATTERN = 'CustomSpendingPattern'
    HOUSEHOLD_SPENDING_PATTERN = 'HouseholdSpendingPattern'
    INTERNATIONAL_INDUSTRY_IMPACT_ANALYSIS = 'InternationalIndustryImpactAnalysis'
    CUSTOM_INDUSTRY_IMPACT_ANALYSIS = 'CustomIndustryImpactAnalysis'
    CUSTOM_INTERNATIONAL_INDUSTRY_IMPACT_ANALYSIS = 'CustomInternationalIndustryImpactAnalysis'


class SpendingPatternValueType(str, Enum):
    """
    The options for a Spending Pattern's Value Type
    """
    INTERMEDIATE_EXPENDITURE = 'IntermediateExpenditure'
    OUTPUT = 'Output'


class MarginType(str, Enum):
    """
    The options for a Margin Price
    """
    PRODUCER_PRICE = 'ProducerPrice'
    PURCHASER_PRICE = 'PurchaserPrice'


class RegionType(str, Enum):
    """
    All the different types of Regions that can be used (see `regional_endpoints` and `regional_workflow_examples`)
    """
    UNKNOWN = 'Unknown'
    COUNTRY = 'Country'
    STATE = 'State'
    MSA = 'Msa'
    COUNTY = 'County'
    CONGRESSIONAL_DISTRICT = 'CongressionalDistrict'
    ZIPCODE = 'Zipcode'


class ImpactType(str, Enum):
    """
    The options for an Impact's Type
    """
    DIRECT = 'Direct'
    INDIRECT = 'Indirect'
    INDUCED = 'Induced'
