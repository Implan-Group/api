import requests
import logging



def get_response_data(url, headers, params=None):
    response = None
    try:
        logging.info(f"Request URL: {url}")
        logging.info(f"Request Headers: {headers}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Response: {response.text}")
        raise
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        raise

class AggregationSchemeEndpoints:
    @staticmethod
    def get_aggregation_schemes(bearer_token, industry_set_id=None):
        url = "https://api.implan.com/api/v1/aggregationSchemes"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}"
        }
        params = {}
        if industry_set_id is not None:
            params['industrySetId'] = industry_set_id
        
        response_data = get_response_data(url, headers, params=params)
        
        return [AggregationScheme(
            id_=item['id'],
            description=item['description'],
            industry_set_id=item['industrySetId'],
            household_set_ids=item['householdSetIds'],
            map_code=item['mapCode'],
            status=item['status']
        ) for item in response_data]