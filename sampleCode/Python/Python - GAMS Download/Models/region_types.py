from enum import Enum

class RegionType(Enum):
    """
    All valid Region Types that can be specified for Implan Impact API Endpoints
    """
    COUNTRY = 1
    STATE = 2
    MSA = 3
    COUNTY = 4
    CONGRESSIONAL_DISTRICT = 5
    ZIPCODE = 6