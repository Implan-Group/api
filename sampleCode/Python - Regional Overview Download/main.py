import logging
import os
import sys
import time
import pathvalidate
from dotenv import load_dotenv

from Models.combine_region_request import CombineRegionRequest
from auth_helper import AuthHelper
from excel_helper import ExcelHelper
from Models.region_types import RegionType
from impact_endpoints import Endpoints
from Models.region import Region

"""
Please look at `readme.md` for instructions on executing this Python Script
"""

##############################################################################################
# !!! YOU MUST FILL OUT THE INFORMATION IN THIS SECTION FOR THIS SCRIPT TO EXECUTE PROPERLY !!!
# These are the variables that are required from the user in order for this script to execute:

# The Aggregation Scheme Id for the output reports:
# Aggregation Scheme  8 (546)
# Aggregation Scheme 14 (528)
aggregation_scheme_id = 14

# The Dataset Id for the MSAs:
# Dataset #98 (2023)
dataset_id = 98

# The Combined Region Builder xlsx file that contains the custom Regions
# If you do not wish to do any custom regions you may leave this blank
combined_regions_builder_file_path = "Combined Region Builder - Example.xlsx"

# Specify the output directory for the CSV Report Downloads
# You can use `os.getcwd()` to use the Current Working Directory, which is the same folder as the `main.py` file
output_dir = os.getcwd()
##############################################################################################

# Load information from the secret `.env` file (see `readme.md` for more information)
load_dotenv()

# Configure logging to show all messages Debug severity or higher with a specific format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# We have a subfolder for the output directory to keep the paths much cleaner
output_dir = os.path.join(output_dir, f"GAMS_Agg{aggregation_scheme_id}")

# This code creates the csv output directory if it does not already exist
if not os.path.exists(output_dir):
    os.mkdir(output_dir)


def main():
    """
    The `main()` method contains all the steps to perform this process
    """


    # We first must perform authentication to get a JWT Bearer Token
    # https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication

    logging.info(f"Authenticating...")
    auth = AuthHelper()
    token = auth.get_bearer_token()
    if token is None:
        logging.error("Could not authenticate to the Implan Impact API, exiting.")
        sys.exit("Could not authenticate")

    logging.info(f"Authenticated to Implan Impact API")

    # Then we initialize the Endpoints with that token, so it will be used for all future requests
    endpoints = Endpoints(token)


    # We need to create a lookup that maps a County's FIPS code to its HashId
    # Hashids are required for combining regions and looking up their information
    logging.info("Creating lookup sets...")
    fips_to_hashid: dict[int, str] = { }
    # Retrieve a list of all the counties in the United States
    counties = endpoints.get_top_level_children(aggregation_scheme_id, dataset_id, RegionType.COUNTY)
    # For each of them
    for county in counties:
        # Map the county's 5-digit FIPS code to its HashId
        fips_to_hashid[int(county.fipsCode)] = county.hashId


    # Now we gather the total list of all Regions that will have reports generated and saved
    regions: list[Region] = []

    # ------ All Implan Counties

    # Retrieve all the Counties for the US
    logging.info(f"Retrieving all the Counties for the United States...")
    us_regions: list[Region] = endpoints.get_top_level_children(aggregation_scheme_id, dataset_id, RegionType.COUNTY)

    ## DEMO ##
    # culling this to a shorter list for demonstration purposes
    us_regions = us_regions[:10]

    # Verify that each region is built
    logging.info(f"Retrieved {len(us_regions)} total Regions, verifying build status...")
    unbuilt_region_hashids: list[str] = []
    for us_region in us_regions:
        # Get the Region's current status
        region_status = endpoints.get_region_by_hashid(aggregation_scheme_id, dataset_id, us_region.hashId)
        # If it exists and the build is completed, continue to verify the next region
        if region_status and region_status.modelBuildStatus == "Complete":
            continue

        # This region is not yet built
        unbuilt_region_hashids.append(us_region.hashId)


    # Are there any Regions that we need to build?
    if len(unbuilt_region_hashids) > 0:
        logging.info(f"Batch Building {len(unbuilt_region_hashids)} Regions...")
        # We can batch build all of them
        response: list[Region] | None
        response = endpoints.build_batch_regions(aggregation_scheme_id, unbuilt_region_hashids)

        # The response must contain the same number of regions
        if response is None or len(response) != len(unbuilt_region_hashids):
            logging.error(f"Could not Build Batch Regions: {response}")
            sys.exit("Could not Build Batch Regions")

        # We need to wait for their models to be built
        while len(unbuilt_region_hashids) > 0:
            # For all remaining unbuilt models
            for unbuilt_region_hashid in unbuilt_region_hashids:
                # Get the Region's current status
                region_status = endpoints.get_region_by_hashid(aggregation_scheme_id, dataset_id, unbuilt_region_hashid)
                # If it exists and the build is completed, we can remove this from unbuilt
                if region_status and region_status.modelBuildStatus == "Complete":
                    logging.info(f"Region '{unbuilt_region_hashid}' has been built.")
                    unbuilt_region_hashids.remove(unbuilt_region_hashid)
                    continue

            # If we're still waiting on any Regions to build, pause a moment and then try again
            if len(unbuilt_region_hashids) > 0:
                logging.info(f"There are still {len(unbuilt_region_hashids)} being built...")
                time.sleep(30)  # 30 seconds

        logging.info(f"Finished building all Regions.")


    # Add those to the regions that need to be processed
    regions.extend(us_regions)


    # ------ Download Single-File GAMS Reports

    # Process each region in turn
    logging.info(f"Downloading {len(regions)} reports...")

    region: Region
    for region in regions:
        # Get the hashid
        hashid = region.hashId
        # Figure out what the output file will be named
        filename = f"{region.description}.gms"
        # Sanitize the name so it is valid for Windows (some Regions' names include characters that are not valid for file paths)
        filename = pathvalidate.sanitize_filename(filename, replacement_text="_", platform="windows")
        # Create the full path the file will be stored at
        filepath = os.path.join(output_dir, filename)

        # If that file already exists, skip downloading this report
        if os.path.exists(filepath):
            continue

        # Load the GAMS data
        gams_data = endpoints.get_single_file_gams(aggregation_scheme_id, hashid)

        # If there was an error, display it and skip this hashid
        if gams_data is None:
            logging.error(f"Could not get Report for Region '{region.description}'")
            continue

        # Save the csv data to the local file
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(gams_data)

        # Done with this Region, onto the next
        logging.info(f"Processed '{region.description}'")


    # Done with all Regions
    logging.info(f"Finished processing {len(regions)} regions")
    sys.exit(0)


# This code allows this file to be run as a script or module
# https://docs.python.org/3/library/__main__.html
if __name__ == '__main__':
    main()
