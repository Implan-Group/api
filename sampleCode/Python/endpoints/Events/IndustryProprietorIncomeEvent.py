# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid
from endpoints.Events.Event import Event 

class IndustryProprietorIncomeEvent(Event):
    def __init__(self, title, proprietor_income, industry_code, output=None, employment=None, employee_compensation=None, dataset_id=None, margin_type=None, percentage=None, id=None, project_id=None, tags=None):
        super().__init__(title, id, project_id, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
        self.dataset_id = dataset_id
        self.margin_type = margin_type
        self.percentage = percentage
        self.impact_event_type = "IndustryProprietorIncome"

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get('title', 'Default Title'),
            output=data.get('output', 0.0),
            employment=data.get('employment'),
            employee_compensation=data.get('employeeCompensation'),
            proprietor_income=data.get('proprietorIncome'),
            industry_code=data.get('industryCode', 0),
            dataset_id=data.get('datasetId'),
            margin_type=data.get('marginType'),
            percentage=data.get('percentage'),
            id=data.get('id', str(uuid.uuid4())),
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
            "marginType": self.margin_type,
            "percentage": self.percentage
        })
        return event_dict
