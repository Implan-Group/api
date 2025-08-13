import logging
import time
import requests

from requests import RequestException
from Models.combine_region_request import CombineRegionRequest
from Models.region_types import RegionType
from Models.region import Region


class Endpoints:
    """
    This class contains the information needed to make requests to various Implan API endpoints
    """

    def __init__(self, bearer_token: str):
        """
        Construct `Endpoints` by specifying a Bearer Token
        :param bearer_token: The JWT from the Implan API Auth endpoint
        """

        self.bearer_token = bearer_token
        self.base_url = "https://api.implan.com"

    def get_region_overview_industries(self, aggregation_scheme_id: int, hashid: str) -> str | None:
        """
        Gets the Region Overview Industries CSV report for a region
        :param aggregation_scheme_id: The Aggregation Scheme
        :param hashid: The Region's Hash Identifier
        :return: A string containing the CSV report

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#region-overview-industries
        """
        # The Implan API endpoint to get a region's industry overview csv
        url = f"{self.base_url}/api/v1/regions/export/{aggregation_scheme_id}/RegionOverviewIndustries?hashid={hashid}"

        # Specify the Bearer Token
        headers = {"Authorization": self.bearer_token}

        response = None
        try:
            # Get the response
            response = requests.get(url, headers=headers)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            # Return our response text (which is the CSV data as UTF8)
            text = response.text
            return text
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            if response is not None and response.status_code == 400:
                # This usually indicates that the region isn't built
                logging.info("Status Code indicates that the Region may be unbuilt")
            return None

    def get_top_level_children(self, aggregation_scheme_id: int, dataset_id: int, region_type: RegionType) -> list[Region] | None:
        """
        Gets all the child Regions of a particular Type for the United States
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param dataset_id: The Dataset Id
        :param region_type: The Type of Child Regions to return
        :return: A list of all child Regions

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#top-level-region-children
        """

        # The Implan API endpoint to get the top-level region's (United States) child regions
        url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/children?regionTypeFilter={region_type.name}"

        # Specify the Bearer Token
        headers = {"Authorization": self.bearer_token}

        try:
            # Get the response
            response = requests.get(url, headers=headers)
            # If it isn't a 200 OK, throw
            response.raise_for_status()

            json_body = response.json()
            # Map the response JSON to a List of Region classes
            regions = [Region(**item) for item in json_body]
            return regions
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def get_region_children(self, aggregation_scheme_id: int, dataset_id: int, parent_hashid: str,
                            region_type: RegionType) -> list[Region] | None:
        """
        Gets all the child Regions of a particular Type from a Parent Region
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param dataset_id: The Dataset Id
        :param parent_hashid: The HashId for the Parent Region
        :param region_type: The Type of Child Regions to return
        :return: A list of all child Regions

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#top-level-region-children
        """

        # The Implan API endpoint to get a Region's Children
        url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{parent_hashid}/children?regionTypeFilter={region_type.name}"

        # Specify the Bearer Token
        headers = {"Authorization": self.bearer_token}

        try:
            # Get the response
            response = requests.get(url, headers=headers)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            body_json = response.json()
            # Map the response JSON to a List of Region classes
            regions = [Region(**item) for item in body_json]
            return regions
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def build_combined_regions(self, aggregation_scheme_id: int, request: CombineRegionRequest) -> list[Region] | None:
        """
        Combines several Regions together into a single Region
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param request: A model that contains information about the Regions to be combined
        :return: A list of Regions that will contain a single Region definition for the newly combined Region

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#build-combined-region-post
        """

        # The Implan Impact API Endpoint to build combined regions
        url = f"{self.base_url}/api/v1/region/build/combined/{aggregation_scheme_id}"
        # Pass in the bearer token
        headers = {"Authorization": self.bearer_token}
        # Convert the CombineRegionRequest into a dictionary/json
        payload = vars(request)

        try:
            # POST the request
            response = requests.post(url, headers=headers, json=payload)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            json_body = response.json()
            # Map the response JSON to a List of Region classes
            regions = [Region(**item) for item in json_body]
            return regions
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def build_batch_regions(self, aggregation_scheme_id: int, region_ids: list[str]) -> list[Region] | None:
        """
        Build several Implan-defined Regions simultaniously (but does not combine them)
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param region_ids: A list of HashIds and/or Urids for the Implan Regions to be built
        :return: A list of all the specified Regions

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#regions---build-and-return
        """
        # The Implan Impact API Endpoint to build batch regions (_not_ combined)
        url = f"{self.base_url}/api/v1/region/build-and-return/{aggregation_scheme_id}"
        # Pass in the bearer token
        headers = {"Authorization": self.bearer_token}

        try:
            # POST the request
            response = requests.post(url, headers=headers, json=region_ids)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            json_body = response.json()
            # Map the response JSON to a List of Region classes
            regions = [Region(**item) for item in json_body]
            return regions
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def get_region_by_hashid(self, aggregation_scheme_id: int, dataset_id: int, hashid: str) -> Region | None:
        """
        Gets an Implan-defined Region
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param dataset_id: The Dataset Id
        :param hashid: The HashId for the Implan Region to retrieve
        :return: The Implan Region with the given HashId or None if the Region does not exist

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#get-regions-by-urid-get
        """

        # The Implan Impact API Endpoint to get a single region's details
        url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/{hashid}"

        # Bearer Token
        headers = {"Authorization": self.bearer_token}

        # Send the request
        try:
            # POST the request
            response = requests.get(url, headers=headers)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            # The response json is a single Region
            json_body = response.json()
            region = Region(**json_body)
            return region
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def get_user_regions(self, aggregation_scheme_id: int, dataset_id: int) -> list[Region] | None:
        """
        Gets all user-defined (customized and/or combined) Regions
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param dataset_id: The Dataset Id
        :return: A list of all user-defined Regions

        https://github.com/Implan-Group/api/blob/main/impact/readme.md#user-custom-and-combined-regions-get
        """

        # The Implan Impact API Endpoint to get a list of all a user's customized regions
        url = f"{self.base_url}/api/v1/region/{aggregation_scheme_id}/{dataset_id}/user"
        # Bearer Token
        headers = {"Authorization": self.bearer_token}
        try:
            # Send the request
            response = requests.get(url, headers=headers)
            # If it isn't a 200 OK, throw
            response.raise_for_status()
            json_body = response.json()
            # Map the response JSON to a List of Region classes
            regions = [Region(**item) for item in json_body]
            return regions
        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None

    def wait_for_region_build(self,
                              aggregation_scheme_id: int,
                              dataset_id: int,
                              hashid: str,
                              is_custom: bool,
                              delay_time_seconds: int = 30) -> Region | None:
        """
        Wait for the build process of a Region to complete
        :param aggregation_scheme_id: The Aggregation Scheme Id
        :param dataset_id: The Dataset Id
        :hashid: The HashId for the Region
        :is_custom: Whether this is a customized/combined region or a default Implan Region
        :delay_time_seconds: How long, in seconds, we will wait between checking a Region's status
        :return: The Region's information once it has been built

        """

        # We need to wait for the combined model to be built before processing the next region
        region: Region | None

        # We'll have to loop in case the region is not yet built
        while True:

            if is_custom:
                # Get a list of all known User Regions (combined + customized)
                user_regions = self.get_user_regions(aggregation_scheme_id, dataset_id)
                # Find one that matches our hashid
                region = next((r for r in user_regions if r.hashId == hashid), None)
            else:
                # Get the Region's current status
                region = self.get_region_by_hashid(aggregation_scheme_id, dataset_id, hashid)

            # If it exists and the build is completed, we can stop polling
            if region and region.modelBuildStatus == "Complete":
                return region

            # Otherwise, wait a bit and check again
            time.sleep(delay_time_seconds)

    def get_single_file_gams(self,
                             aggregation_scheme_id: int,
                             hashid: str):

        url:str  = f"{self.base_url}/api/v1/regions/export/{aggregation_scheme_id}/region-general-algebraic-modeling-single-file"

        headers = {"Authorization": self.bearer_token}

        query_params:dict = {
            "hashId": hashid
        }

        try:
            # Send the request
            response = requests.get(url, headers=headers, params=query_params)

            # If it isn't a 200 OK, throw
            response.raise_for_status()

            # The Response is a GAMS single file
            content: bytes = response.content

            gams: str = content.decode("utf-8")

            return gams

        except RequestException as ex:
            logging.error(f"Request Failed: {ex}")
            return None
