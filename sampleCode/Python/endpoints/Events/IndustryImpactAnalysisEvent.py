import uuid
from endpoints.Events.Event import Event

class IndustryImpactAnalysisEvent(Event):
    def __init__(self, title, industry_code, intermediate_inputs=None, total_employment=None, employee_compensation=None, proprietor_income=None, wage_and_salary_employment=None, proprietor_employment=None, total_labor_income=None, other_property_income=None, tax_on_production_and_imports=None, local_purchase_percentage=1.0, total_output=None, is_sam=None, spending_pattern_dataset_id=None, spending_pattern_value_type=None, spending_pattern_commodities=None, id=None, project_id=None, tags=None):
        super().__init__(title, id, project_id, tags)
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
        self.local_purchase_percentage = local_purchase_percentage
        self.total_output = total_output
        self.is_sam = is_sam
        self.spending_pattern_dataset_id = spending_pattern_dataset_id
        self.spending_pattern_value_type = spending_pattern_value_type
        self.spending_pattern_commodities = spending_pattern_commodities
        self.impact_event_type = "IndustryImpactAnalysis"

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            industry_code=data.get('industryCode', 0),
            intermediate_inputs=data.get('intermediateInputs'),
            total_employment=data.get('totalEmployment'),
            employee_compensation=data.get('employeeCompensation'),
            proprietor_income=data.get('proprietorIncome'),
            wage_and_salary_employment=data.get('wageAndSalaryEmployment'),
            proprietor_employment=data.get('proprietorEmployment'),
            total_labor_income=data.get('totalLaborIncome'),
            other_property_income=data.get('otherPropertyIncome'),
            tax_on_production_and_imports=data.get('taxOnProductionAndImports'),
            local_purchase_percentage=data.get('localPurchasePercentage', 1.0),
            total_output=data.get('totalOutput'),
            is_sam=data.get('isSam', False),
            spending_pattern_dataset_id=data.get('spendingPatternDatasetId'),
            spending_pattern_value_type=data.get('spendingPatternValueType'),
            spending_pattern_commodities=data.get('spendingPatternCommodities', []),
            id=data.get('id', str(uuid.uuid4())),
            project_id=data.get('projectId', None),  # Avoid using 'Default Project ID'
            tags=data.get('tags', [])
        )

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "industryCode": self.industry_code,
            "intermediateInputs": self.intermediate_inputs,
            "totalEmployment": self.total_employment,
            "employeeCompensation": self.employee_compensation,
            "proprietorIncome": self.proprietor_income,
            "wageAndSalaryEmployment": self.wage_and_salary_employment,
            "proprietorEmployment": self.proprietor_employment,
            "totalLaborIncome": self.total_labor_income,
            "otherPropertyIncome": self.other_property_income,
            "taxOnProductionAndImports": self.tax_on_production_and_imports,
            "localPurchasePercentage": self.local_purchase_percentage,
            "totalOutput": self.total_output,
            "isSam": self.is_sam,
            "spendingPatternDatasetId": self.spending_pattern_dataset_id,
            "spendingPatternValueType": self.spending_pattern_value_type,
            "spendingPatternCommodities": self.spending_pattern_commodities
        })
        return event_dict
