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

import json
import uuid
import requests
from endpoints.Events.IndustryOutputEvent import IndustryOutputEvent
from endpoints.Events.IndustryImpactAnalysisEvent import IndustryImpactAnalysisEvent

class EventEndpoints:
    @staticmethod
    def add_industry_output_event(project_id, event_data, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_id}/event"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        try:
            payload = event_data.to_dict()
            print("Request Payload for IndustryOutputEvent:", json.dumps(payload, indent=4))
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return IndustryOutputEvent.from_dict(response.json())
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    @staticmethod
    def add_industry_impact_analysis_event(project_id, event_data, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_id}/event"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        try:
            payload = event_data.to_dict()
            print("Request Payload for IndustryImpactAnalysisEvent:", json.dumps(payload, indent=4))
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return IndustryImpactAnalysisEvent.from_dict(response.json())
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.content}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    def get_events_types(project_guid, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_guid}/eventtype"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            event_types = response.json()
            return event_types
        else:
            print(f"Failed to get event types: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def get_event(project_guid, event_guid, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_guid}/event/{event_guid}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            event_data = response.json()
            return event_data
        else:
            print(f"Failed to get event: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def get_events(project_guid, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_guid}/event"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            events_data = response.json()
            print(f"Events Data: {events_data}")  # Debugging line
            return events_data
        else:
            print(f"Failed to get events: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def add_household_income_event(project_guid, household_income_event, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_guid}/event"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.post(url, json=household_income_event.to_dict(), headers=headers)
        response.raise_for_status()
        return response.json()
