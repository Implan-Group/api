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

class IndustryCode:
    def __init__(self, id, code, description):
        self.id = id
        self.code = code
        self.description = description

class IndustryCodeEndpoints:
    @staticmethod
    def get_industry_codes(aggregation_scheme_id=None, industry_set_id=None, bearer_token=None):
        if aggregation_scheme_id is None:
            url = "https://api.implan.com/beta/api/v1/IndustryCodes"
        else:
            url = f"https://api.implan.com/beta/api/v1/IndustryCodes/{aggregation_scheme_id}"

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

# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
