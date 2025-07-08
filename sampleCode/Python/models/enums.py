from enum import Enum

# All Enums must be defined as subclassing `str` so that the JsonHelper can properly translate them to and from the string representatinos
# used by the Impact API


class EventType(str, Enum):
    """
    All the possible Event Types
    Not all event types are available for all projects
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

    def __str__(self) -> str:
        return str.__str__(self)



class SpendingPatternValueType(str, Enum):
    """
    The different Spending Pattern Value Types
    """
    INTERMEDIATE_EXPENDITURE = 'IntermediateExpenditure'
    OUTPUT = 'Output'


class MarginType(str, Enum):
    PRODUCER_PRICE = 'ProducerPrice'
    PURCHASER_PRICE = 'PurchaserPrice'


class RegionType(str, Enum):
    UNKNOWN = 'Unknown'
    COUNTRY = 'Country'
    STATE = 'State'
    MSA = 'Msa'
    COUNTY = 'County'
    CONGRESSIONAL_DISTRICT = 'CongressionalDistrict'
    ZIPCODE = 'Zipcode'