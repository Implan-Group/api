# ImpactApi - Regional Workflow
- [Impact Readme - Regions](https://github.com/Implan-Group/api/blob/main/impact/readme.md#regions)
- Regions are one of the core parts of an Impact and there are many ways to search for them


### 🗈 Notes
- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
	- Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
- Variables required for Endpoint calls will appear inside of double-braces (`{{}}`) and they must be replaced with valid values before the Request is sent
	- _e.g._ `{{api_domain}}` should be replaced with `https://api.implan.com/` for Public Production requests
	- See the [Production Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#production-variables) section of the Readme for more information


---
## 🔽 Regional Attributes
- All region data in IMPLAN are unique based upon the Aggregation Scheme, Dataset (data year), and geographic demarcation (zip, county, state, etc...).
- The unique regional identifiers used with the IMPLAN API are:
  - [HashID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#hashid)
  - [URID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#urid)
    - URIDs are slowly being depreciated, prefer HashIds whenever possible
- One or the other of the above identifiers are used for calls to build combined Regions, pull Region data, and assign to Groups for Impacts.

### Get / Filter Aggregation Schemes
- [Impact Readme - Aggregation Schemes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#aggregation-schemes)

##### Request
- `GET {{api_domain}}api/v1/aggregationSchemes`
- `GET {{api_domain}}api/v1/aggregationSchemes?industrySetId={{industry_set_id}}`
  - The `industrySetId` is an optional filter that can be applied to limit the returned Aggregation Schemes further
  - [Impact Readme - Industry Sets](https://github.com/Implan-Group/api/blob/main/impact/readme.md#industry-sets)

##### Response
- Returns a `json` array of valid Aggregation Schemes
```json
[
    {
        "id": 1,
        "description": "536 Unaggregated",
        "industrySetId": 2,
        "householdSetIds": [1,2],
        "mapCode": "US",
        "status": "Complete"
    },
    ...
     {
        "id": 1099,
        "description": "Custom Scheme",
        "industrySetId": 8,
        "householdSetIds": [1],
        "mapCode": "US",
        "status": "Complete"
    }
]
```
- `id` (number): Aggregation Scheme Identifier
- `description` (text): Description of the aggregation scheme
- `industrySetId` (number): Industry Set Identifier
- `householdSetIds` (array of numbers): Valid Household Set Identifiers that can be used with this aggregation scheme
- `mapCode` (text): A code to describe
- `status` (text): Whether or not this aggregation scheme has been built yet

---
### Datasets
- To explore Regions further, a Dataset Id is required -- this specifies the Data Year
- See [Datasets](https://github.com/Implan-Group/api/blob/main/impact/readme.md#dataset-endpoint-get) in the main Impact Readme for details on finding the correct `DatasetId`

##### Request
- `GET {{api_domain}}api/v1/datasets`
- `GET {{api_domain}}api/v1/datasets/{{aggregationSchemeId}}`
  - Use this endpoint to further filter the Datasets by Aggregation Scheme Id

##### Response
- Returns a `json` array of valid Datasets
```json
[
	{
		"id": 60,
        "description": "2001",
        "isDefault": false
    },
    ...
    {
	    "id": 96,
        "description": "2022",
        "isDefault": true
    }
]
```
  - `id` (number): Dataset Identifier
  - `description` (text): Description of the Dataset
  - `isDefault` (boolean): Whether or not this Dataset is the default

---
### Region Json
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
- `employment` (number, optional): Total employment value for this Region
- `output` (number, optional): Total industry output value for this Region
- `valueAdded` (number, optional): Total value-added for this Region
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


---
## 🔽 Find Regions

---
### Region Types
- Gets a list of the Types of Regions that can be queried

##### Request
- `GET {{api_domain}}api/v1/region/RegionTypes`

##### Response
- Returns a `json`-array of Region Types
```json
[
    "Country",
    "State",
    "Msa",
    "County",
    "CongressionalDistrict",
    "Zipcode"
]
```

---
### Top-Level Region
- Gets the top-level Region for an Aggregation Scheme and Dataset -- this is usually the Country that matches the Dataset
	- _e.g. "US", "Canada"_

##### Request
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}`

##### Response
- Returns a single `json` Region (see Region Json above)

---
### Region Children
- Gets all the children Regions for an Aggregation Scheme and Dataset

##### Request
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children`
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children?regionTypeFilter={{regionType}}`
	- A `RegionType` Filter can be optionally applied to further limit the response

##### Response
- Returns a `json`-array of child Regions (see Region Json above)

---
### User Regions
- Gets all the user-defined Regions for an Aggregation Scheme and Dataset
	- This includes all customized and combined Regions

##### Request
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/user`

##### Response
- Returns a `json`-array of child Regions (see Region Json above)