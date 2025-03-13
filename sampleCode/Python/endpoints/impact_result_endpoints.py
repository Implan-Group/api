import requests
import logging

class ImpactType:
    Direct = 1
    Indirect = 2
    Induced = 3

class ImpactResultEndpoints:
    class CsvReports:
        @staticmethod
        def get_detailed_economic_indicators(impact_run_id, bearer_token):
            url = f"https://api.implan.com/api/v1/impact/results/ExportDetailEconomicIndicators/{impact_run_id}"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.HTTPError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
                raise
            except Exception as err:
                logging.error(f"Other error occurred: {err}")
                raise

        @staticmethod
        def get_summary_economic_indicators(impact_run_id, bearer_token):
            url = f"https://api.implan.com/api/v1/impact/results/SummaryEconomicIndicators/{impact_run_id}"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.HTTPError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
                raise
            except Exception as err:
                logging.error(f"Other error occurred: {err}")
                raise

        @staticmethod
        def get_detailed_taxes(impact_run_id, bearer_token):
            url = f"https://api.implan.com/api/v1/impact/results/DetailedTaxes/{impact_run_id}"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.HTTPError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
                raise
            except Exception as err:
                logging.error(f"Other error occurred: {err}")
                raise

        @staticmethod
        def get_summary_taxes(impact_run_id, bearer_token):
            url = f"https://api.implan.com/api/v1/impact/results/SummaryTaxes/{impact_run_id}"
            headers = {"Authorization": f"Bearer {bearer_token}"}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.HTTPError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
                raise
            except Exception as err:
                logging.error(f"Other error occurred: {err}")
                raise

    class EstimatedGrowthPercentageFilter:
        def __init__(self, dollar_year, regions=None, impacts=None, group_names=None, event_names=None, event_tags=None):
            self.dollar_year = dollar_year
            self.regions = regions or []
            self.impacts = impacts or []
            self.group_names = group_names or []
            self.event_names = event_names or []
            self.event_tags = event_tags or []

        def to_dict(self):
            return {
                "DollarYear": self.dollar_year,
                "Regions": self.regions,
                "Impacts": [impact for impact in self.impacts],
                "GroupNames": self.group_names,
                "EventNames": self.event_names,
                "EventTags": self.event_tags,
            }

    @staticmethod
    def get_estimated_growth_percentage(impact_run_id, filter_, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/results/EstimatedGrowthPercentage/{impact_run_id}"
        headers = {"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"}
        payload = filter_.to_dict()
        logging.debug(f"Request URL: {url}")
        logging.debug(f"Request Headers: {headers}")
        logging.debug(f"Request Payload: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logging.debug(f"Response Status Code: {response.status_code}")
            logging.debug(f"Response Headers: {response.headers}")
            logging.debug(f"Response Text: {response.text}")
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None