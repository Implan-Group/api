import uuid
from endpoints.Events.Event import Event 
class IndustryEmployeeCompensationEvent(Event):
    def __init__(self, title, employee_compensation, industry_code, output=None, employment=None, proprietor_income=None, dataset_id=None, margin_type=None, percentage=None, id=None, project_id=None, tags=None):
        super().__init__(title, id, project_id, tags)
        self.employee_compensation = employee_compensation
        self.industry_code = industry_code
        self.output = output
        self.employment = employment
        self.proprietor_income = proprietor_income
      
        self.impact_event_type = "IndustryEmployeeCompensation"

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            employee_compensation=data.get('employeeCompensation', 0.0),
            industry_code=data.get('industryCode', 0),
            output=data.get('output'),
            employment=data.get('employment'),
            proprietor_income=data.get('proprietorIncome'),
            id=data.get('id', str(uuid.uuid4())),
            project_id=data.get('projectId', 'Default Project ID'),
            tags=data.get('tags', [])
        )

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "employeeCompensation": self.employee_compensation,
            "industryCode": self.industry_code,
            "output": self.output,
            "employment": self.employment,
            "proprietorIncome": self.proprietor_income
        })
        return event_dict
