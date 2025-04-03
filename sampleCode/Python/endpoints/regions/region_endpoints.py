import requests

from endpoints.regions.Region import Region

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
    def get_region_children(bearer_token, aggregation_scheme_id, dataset_id, hashid_or_urid=None, region_type=None):
        if hashid_or_urid:
            url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hashid_or_urid}/children"
        else:
            url = f"https://api.implan.com/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children"
       
        headers = {"Authorization": f"Bearer {bearer_token}"}
        params = {}
        if region_type:
            params["regionTypeFilter"] = region_type
 
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

    @staticmethod
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