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

class IndustrySet:
    def __init__(self, id, description, defaultAggregationSchemeId=None, activeStatus=None, isDefault=None, mapTypeId=None, isNaicsCompatible=False):
        self.id = id
        self.description = description
        self.default_aggregation_scheme_id = defaultAggregationSchemeId
        self.active_status = activeStatus
        self.is_default = isDefault
        self.map_type_id = mapTypeId
        self.is_naics_compatible = isNaicsCompatible

class IndustrySets:
    @staticmethod
    def get_industry_set(industry_set_id, bearer_token):
        url = f"https://api.implan.com/beta/api/v1/industry-sets/{industry_set_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(data)  # Print the data to see the exact keys
            return IndustrySet(**data) if data else None
        else:
            response.raise_for_status()

    @staticmethod
    def get_industry_sets(bearer_token):
        url = "https://api.implan.com/beta/api/v1/industry-sets"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(data)  # Print the data to see the exact keys
            return [IndustrySet(
                id=item.get('id'),
                description=item.get('description'),
                defaultAggregationSchemeId=item.get('defaultAggregationSchemeId'),
                activeStatus=item.get('activeStatus'),
                isDefault=item.get('isDefault'),
                mapTypeId=item.get('mapTypeId'),
                isNaicsCompatible=item.get('isNaicsCompatible', False)
            ) for item in data]
        else:
            response.raise_for_status()

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


