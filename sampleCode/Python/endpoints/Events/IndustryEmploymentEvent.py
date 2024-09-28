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

class IndustryEmploymentEvent(Event):
    def __init__(self, title, employment, industry_code, output=None, employee_compensation=None, proprietor_income=None, dataset_id=None, id=None, project_id=None, tags=None):
        super().__init__(title, id, project_id, tags)
        self.output = output
        self.employment = employment
        self.employee_compensation = employee_compensation
        self.proprietor_income = proprietor_income
        self.industry_code = industry_code
        self.impact_event_type = "IndustryEmployment"

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
        })
        return event_dict
