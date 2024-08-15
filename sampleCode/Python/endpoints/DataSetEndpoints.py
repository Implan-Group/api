import requests
import json
import logging

class DataSet:
    def __init__(self, id, description, isDefault):
        self.id = id
        self.description = description
        self.is_default = isDefault

class DataSetEndpoints:
    @staticmethod
    def get_datasets(aggregation_scheme_id, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/datasets/{aggregation_scheme_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Data Sets: {data}")  # Log the data to see the exact keys
            return [DataSet(**item) for item in data]
        else:
            logging.error(f"Failed to get data sets: {response.status_code} - {response.text}")
            response.raise_for_status()

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


