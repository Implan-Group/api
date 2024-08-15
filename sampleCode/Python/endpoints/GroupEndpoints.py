import requests
import logging
import uuid

class GroupEvent:
    def __init__(self, eventId=None, scalingFactor=1.0):
        self.event_id = eventId
        self.scaling_factor = scalingFactor

    def to_dict(self):
        return {
            "eventId": self.event_id,
            "scalingFactor": self.scaling_factor
        }
    

class Group:
    def __init__(self, title, projectId, hashId, datasetId, groupEvents=None, id=None, urid=None, userModelId=None, modelId=None, dollarYear=2024, scalingFactor=1.0):
        self.title = title
        self.id = id if id is not None else str(uuid.uuid4())  # Generate a new UUID if not provided
        self.project_id = projectId
        self.hash_id = hashId
        self.urid = urid
        self.user_model_id = userModelId
        self.model_id = modelId
        self.dollar_year = dollarYear
        self.scaling_factor = scalingFactor
        self.dataset_id = datasetId
        self.group_events = groupEvents or []

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
        url = f"https://api.implan.com/beta/api/v1/impact/project/{project_guid}/group"
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

