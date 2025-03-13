import uuid

from endpoints.Events.Event import Event

class HouseholdIncomeEvent(Event):
    def __init__(self, title, household_income_code, value, id_=None, project_id=None, tags=None):
        super().__init__(title, id_, project_id, tags)
        self.household_income_code = household_income_code
        self.value = value
        self.impact_event_type = "HouseholdIncome"

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            household_income_code=data.get('householdIncomeCode', 0),
            value=data.get('value', 0.0),
            id_=data.get('id', str(uuid.uuid4())),
            project_id=data.get('projectId', 'Default Project ID'),
            tags=data.get('tags', [])
        )

    def to_dict(self):
        event_dict = super().to_dict()
        event_dict.update({
            "householdIncomeCode": self.household_income_code,
            "value": self.value
        })
        return event_dict
