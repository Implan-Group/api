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
from endpoints.Regions.Region import Region
class RegionEndpoints:
    @staticmethod
    def get_region_types(bearer_token):
        url = "https://api.implan.com/api/v1/region/RegionTypes"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
       
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {response_data}")  # Debugging line
            return response_data
        else:
            print(f"Failed to get region types: {response.status_code} - {response.text}")
            response.raise_for_status()
 
    @staticmethod
    def get_top_level_region(bearer_token, aggregation_scheme_id, dataset_id):
        url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
       
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {response_data}")  # Debugging line
            return Region(**response_data)
        else:
            print(f"Failed to get top level region: {response.status_code} - {response.text}")
            response.raise_for_status()
 
    @staticmethod
    def get_region_children(bearer_token, aggregation_scheme_id, dataset_id, hashIdOrUrid=None, regionType=None):
        if hashIdOrUrid:
            url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hashIdOrUrid}/children"
        else:
            url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children"
       
        headers = {"Authorization": f"Bearer {bearer_token}"}
        params = {}
        if regionType:
            params["regionTypeFilter"] = regionType
 
        response = requests.get(url, headers=headers, params=params)
       
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {response_data}")  # Debugging line
            return [Region(**item) for item in response_data]
        else:
            print(f"Failed to get region children: {response.status_code} - {response.text}")
            response.raise_for_status()
 
    @staticmethod
    def get_user_regions(bearer_token, aggregation_scheme_id, dataset_id):
        url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}/user"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
       
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {response_data}")  # Debugging line
            return [Region(**item) for item in response_data]
        else:
            print(f"Failed to get user regions: {response.status_code} - {response.text}")
            response.raise_for_status()
 
    def combine_regions(aggregation_scheme_id, payload, bearer_token):
        url = f"https://api.implan.com/api/v1/region/build/combined/{aggregation_scheme_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.post(url, headers=headers, json=payload.to_dict())  # Ensure to_dict() is called
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response Data: {response_data}")  # Debugging line
            if len(response_data) != 1:
                raise Exception("Unexpected number of regions returned")
            return Region(**response_data[0])
        else:
            print(f"Failed to combine regions: {response.status_code} - {response.text}")
            response.raise_for_status()


# Setup basic logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
