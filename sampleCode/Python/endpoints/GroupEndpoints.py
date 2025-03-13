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

import requests
import logging
import uuid

class GroupEvent:
    def __init__(self, event_id=None, scaling_factor=1.0):
        self.event_id = event_id
        self.scaling_factor = scaling_factor

    def to_dict(self):
        return {
            "eventId": self.event_id,
            "scalingFactor": self.scaling_factor
        }
    

class Group:
    def __init__(self, title, project_id, hash_id, dataset_id, group_events=None, id_=None, urid=None, user_model_id=None, model_id=None, dollar_year=2024, scaling_factor=1.0):
        self.title = title
        self.id = id_ if id_ is not None else str(uuid.uuid4())  # Generate a new UUID if not provided
        self.project_id = project_id
        self.hash_id = hash_id
        self.urid = urid
        self.user_model_id = user_model_id
        self.model_id = model_id
        self.dollar_year = dollar_year
        self.scaling_factor = scaling_factor
        self.dataset_id = dataset_id
        self.group_events = group_events or []

    def to_dict(self):
        return {
            "title": self.title,
            "id": self.id,
            "projectId": self.project_id,
            "hashId": self.hash_id,
            "urid": self.urid,
            "userModelId": self.user_model_id,
            "modelId": self.model_id,
            "dollarYear": self.dollar_year,
            "scalingFactor": self.scaling_factor,
            "datasetId": self.dataset_id,
            "groupEvents": [event.to_dict() for event in self.group_events]
        }


class GroupEndpoints:
    @staticmethod
    def add_group_to_project(project_guid, group, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_guid}/group"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        payload = group.to_dict()
        
        logging.debug(f"Sending POST request to URL: {url}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {payload}")

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logging.info("Group added successfully")
            return Group(**response.json())
        else:
            error_msg = f"Failed to add group: {response.status_code} - {response.text}"
            logging.error(error_msg)
            response.raise_for_status()

        # Optional: You may handle different status codes differently here, before raising an error

