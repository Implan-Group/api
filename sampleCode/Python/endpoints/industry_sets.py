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


