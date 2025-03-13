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

# aggregation_schemes.py
import requests
import logging

class AggregationScheme:
    def __init__(self, id_, description, industry_set_id, household_set_ids, map_code, status):
        self.id = id_
        self.description = description
        self.industry_set_id = industry_set_id
        self.household_set_ids = household_set_ids
        self.map_code = map_code
        self.status = status

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

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
