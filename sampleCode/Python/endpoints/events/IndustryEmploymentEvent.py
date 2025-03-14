import uuid

from endpoints.events.Event import Event

class IndustryEmploymentEvent(Event):
    def __init__(self, title, employment, industry_code, output=None, employee_compensation=None, proprietor_income=None, dataset_id=None, id_=None, project_id=None, tags=None):
        super().__init__(title, id_, project_id, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
        self.impact_event_type = "IndustryEmployment"
        self.dataset_id = dataset_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            employment=data.get('employment', 0.0),
            industry_code=data.get('industryCode', 0),
            output=data.get('output'),
            employee_compensation=data.get('employeeCompensation'),
            proprietor_income=data.get('proprietorIncome'),
            dataset_id=data.get('datasetId'),
            id_=data.get('id', str(uuid.uuid4())),
            project_id=data.get('projectId', 'Default Project ID'),
            tags=data.get('tags', [])
        )

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "output": self.output,
            "employment": self.employment,
            "employeeCompensation": self.employee_compensation,
            "proprietorIncome": self.proprietor_income,
            "industryCode": self.industry_code,
            "datasetId": self.dataset_id,
        })
        return event_dict
