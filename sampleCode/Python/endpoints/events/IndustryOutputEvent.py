import uuid

from endpoints.events.Event import Event

class IndustryOutputEvent(Event):
    def __init__(self, title, industry_code, output, employment=None, employee_compensation=None, proprietor_income=None, dataset_id=None, margin_type=None, percentage=None, id_=None, project_id=None, tags=None):
        super().__init__(title, id_, project_id, tags)
        self.industry_code = industry_code
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.dataset_id = dataset_id
        self.margin_type = margin_type
        self.percentage = percentage
        self.impact_event_type = "IndustryOutput"
 
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            industry_code=data.get('industryCode', 0),
            output=data.get('output', 0.0),
            employment=data.get('employment'),
            employee_compensation=data.get('employeeCompensation'),
            proprietor_income=data.get('proprietorIncome'),
            dataset_id=data.get('datasetId'),
            margin_type=data.get('marginType', 'Default Margin'),
            percentage=data.get('percentage'),
            id_=data.get('id', str(uuid.uuid4())),
            project_id=data.get('projectId', 'Default Project ID'),
            tags=data.get('tags', [])
        )
 
    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "industryCode": self.industry_code,
            "output": self.output,
            "employment": self.employment,
            "employeeCompensation": self.employee_compensation,
            "proprietorIncome": self.proprietor_income,
            "datasetId": self.dataset_id,
            "marginType": self.margin_type,
            "percentage": self.percentage
        })
        return event_dict