import requests
import logging

class DataSet:
    def __init__(self, id_, description, is_default):
        self.id = id_
        self.description = description
        self.is_default = is_default

class DataSetEndpoints:
    @staticmethod
    def get_datasets(aggregation_scheme_id, bearer_token):
        url = f"https://api.implan.com/api/v1/datasets/{aggregation_scheme_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Data Sets: {data}")  # Log the data to see the exact keys
            return [DataSet(**item) for item in data]
        else:
            logging.error(f"Failed to get data sets: {response.status_code} - {response.text}")
            response.raise_for_status()