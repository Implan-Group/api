# Impact API - Combined Region Workflow
- This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Further detail on additional workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us)

### Notes:
- All API Endpoints require a valid JWT Bearer Token ([JWT.IO](https://jwt.io/))
  -	Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section of the primary Readme to review authentication steps
- Variables for endpoints will appear inside of double-brackets, those must be replaced with valid values before execution
  - _e.g. `{{api_domain}}`_
  - See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information

## Overview
- Not all economic models are built for Regions by default, or sometimes you may want to combine regions. Combining regions is used to create a custom group of counties, ZIP codes, MSAs, and/or states and treat them as one economic region that can be studied. The endpoints defined in this section may be used to build single or combined regions.
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#building-regions)


## Workflow
- To find Regions to combine, first you must have an Aggregation Scheme and a Dataset

#### Aggregation Schemes
- See [Aggregation Schemes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#aggregation-schemes) in the main Impact Readme for details on finding the correct `AggregationSchemeId`

#### Data Sets
- See [Datasets](https://github.com/Implan-Group/api/blob/main/impact/readme.md#dataset-endpoint-get) in the main Impact Readme for details on finding the correct `DatasetId`


### Find Regions to Combine
- All region data in IMPLAN are unique based upon the Aggregation Scheme, Dataset (data year), and geographic demarcation (zip, county, state, etc...).
- The unique regional identifiers used with the IMPLAN API are:
  - [HashID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#hashid)
  - [URID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#urid)
    - URIDs are slowly being depreciated, prefer HashIds whenever possible
- One or the other of the above identifiers are used for calls to build combined Regions, pull Region data, and assign to Groups for Impacts.

#### Region Types
- `GET {{api_domain}}api/v1/region/RegionTypes`
  - Returns a `json` array of Regions

#### Top-Level Region
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}`
  - Returns the `json` representation of the Top-Level Region for a given Aggregation Scheme and Dataset
  - This is usually the Country that matches the Dataset (e.g. US, Canada)

#### Region Children
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children`
  - Returns a `json` array of all of the Children Regions in a Dataset
    - This will include _all_ children (zip, county, state, msa)
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children?regionTypeFilter={{regionType}}`
  - On optional `regionTypeFilter` can be specified to limit the returned Regions

#### User Regions
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/user`
  - Returns a `json` array of all of the User-defined Regions in a Dataset
  - This includes all customized and combined Regions


### Combine Regions
- Once you have found the HashIds of all of the regions you wish to combine (using the endpoints above), you can combine them together into a single Region
- `POST {{api_domain}}api/v1/region/build/combined/{{aggregationSchemeId}}`
  - A `json` body must be included that defines the Combined Region:
  ```json
  {
    "description": "Testing Combined Region",
    "hashids": [
      { 
        "W1aQl9wzxj", 
        "Rgxp4eA3xK"
      }
    ]
  }
  ```
    - `description` (text): A unique-per-Project description for this Combined Region
    - `hashids` (array of text): An array of the HashIds for all the Regions to be combined
  - Returns a `json` array containing a single Region entry for the newly-combined Region



## Region Json
- The `json` response from regional endpoints is either a single Region or an Array of Regions, shaped like this:
  - _Note: Some information may be `null` as it is not relevant for the Region_
  - _e.g. Combined Regions will have a `null` `fipsCode`_
```json
{
    "hashId": "xAnXEl1YDa",
    "urid": null,
    "userModelId": 9601,
    "description": "Workflow - Combine Regions",
    "modelId": 15041,
    "modelBuildStatus": "Complete",
    "employment": 264756.6275649546,
    "output": 48940767302.00896,
    "valueAdded": 26236124822.124428,
    "aggregationSchemeId": 8,
    "datasetId": 96,
    "datasetDescription": "2022",
    "fipsCode": null,
    "provinceCode": null,
    "m49Code": null,
    "regionType": "",
    "hasAccessibleChildren": false,
    "regionTypeDescription": "",
    "geoId": null,
    "isMrioAllowed": true
}
```
- `hashId` (text): The HashId for this Region (used to reference this exact Region)
- `urid` (number, optional): The URID for this Region (depreciated way to reference this exact Region)
- `userModelId` (number, optional): The User's Model Id for this Region, filled in for Combined and Customized Regions
- `description` (text): The description of this Region
- `modelId` (number): Unique identifier for a particular model, used internally
- `modelBuildStatus` (text): The current status of the Model's Build progress. Certain complex Models may take time to process until they are `Complete`
    - You can query the User's Regions and search for a matching HashId in order to determine when the status has changed
- `employment` (number): Total employment value for this Region
- `output` (number): Total industry output value for this Region
- `valueAdded` (number): Total value-added for this Region
- `aggregationSchemeId` (number): The Aggregation Scheme that includes this Region
- `datasetId` (number): The Dataset that includes this Region
- `datasetDescription` (text): A description of the Dataset that usually includes the Data Year
- `fipsCode` (text, optional): The Federal Information Processing Standards (FIPS) Code for this Region
- `provinceCode` (text, optional): If a Canadian Region, the Code for the Province
- `m49Code` (text, optional): The M49 standard Code for this Region
- `regionType` (text, optional): The Region's Type, one of:
    - `country`, `state`, `msa`, `county`, `Congressional District`, `zipcode`
- `hasAccessibleChildren` (boolean): Whether or not this Region has other children Regions associated with it
    - _e.g. A `state` has many `county` and `zipcode` children
- `regionTypeDescription` (text): A further description of the `regionType`
- `geoId` (text, optional): The first non-`null` value among `provinceCode`, `fipsCode`, or `m49Code` (in that order) (used internally)
- `isMrioAllowed` (boolean): Whether or not the Region supports Multi-Region Input/Ouput  (MRIO) Analysis