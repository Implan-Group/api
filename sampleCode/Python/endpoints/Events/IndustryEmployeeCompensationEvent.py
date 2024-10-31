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
