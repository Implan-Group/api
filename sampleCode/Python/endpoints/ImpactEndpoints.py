import requests
import json
import logging
class ImpactEndpoints:
    @staticmethod
    def run_impact(project_guid, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/{project_guid}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            impact_run_id = response.json()  # Assuming the API returns the impact_run_id as JSON
            logging.info(f"Impact run started successfully: {impact_run_id}")
            return impact_run_id
        except requests.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Other error occurred: {err}")
            raise
        
    @staticmethod        
    def get_impact_status(impact_run_id, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/status/{impact_run_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Request Headers: {headers}")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            logging.debug(f"Response Status Code: {response.status_code}")
            logging.debug(f"Response Headers: {response.headers}")
            logging.debug(f"Response Text: {response.text}")
            
            # Handle plain text response
            return response.text.strip()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None


    @staticmethod
    def cancel_impact(impact_run_id, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/impact/cancel/{impact_run_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        try:
            response = requests.put(url, headers=headers)
            response.raise_for_status()
            result = response.text.strip().lower()
            logging.info(f"Cancel impact result: {result}")
            return result == "analysis run cancelled."
        except requests.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Other error occurred: {err}")
            raise