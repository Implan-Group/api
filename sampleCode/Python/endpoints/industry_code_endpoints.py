import requests
import logging

class IndustryCode:
    def __init__(self, id_, code, description):
        self.id = id_
        self.code = code
        self.description = description

class IndustryCodeEndpoints:
    @staticmethod
    def get_industry_codes(aggregation_scheme_id=None, industry_set_id=None, bearer_token=None):
        if aggregation_scheme_id is None:
            url = "https://api.implan.com/api/v1/IndustryCodes"
        else:
            url = f"https://api.implan.com/api/v1/IndustryCodes/{aggregation_scheme_id}"

        headers = {"Authorization": f"Bearer {bearer_token}"}
        params = {}
        if industry_set_id is not None:
            params['industrySetId'] = industry_set_id

        logging.debug(f"Request URL: {url}")
        logging.debug(f"Request Headers: {headers}")
        logging.debug(f"Request Params: {params}")

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            logging.debug(f"Response Data: {data}")
            return [IndustryCode(**item) for item in data]
        except requests.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            raise
        except Exception as err:
            logging.error(f"Other error occurred: {err}")
            raise