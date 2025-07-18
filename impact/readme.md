# Overview
This document is intended to provide a developer guide for the API that IMPLAN has developed for creating economic models and  generating impacts via API.  This API is intended to eventually replicate the functionality of IMPLAN Cloud, allowing you to embed IMPLAN into your applications and workflows.  

This document assumes a working knowledge of the IMPLAN Cloud and its workflow, which can be found on [support.implan.com](https://support.implan.com/hc/en-us).  

## Getting Started
To help you get started running economic impact analysis, this section will provide a quick overview of the implan workflow after you’ve completed the [Authentication](#authentication).

### Find a region and industry to study
In order to run an economic impact analysis, you will first need to identify the [Data Year (Dataset)](#dataset-endpoint-get) on when the impact will take place, the [Industry](#industry-codes-endpoint-get) that will change, and the [Region](#region-model-endpoint-get) where the impact will take place.

### Create a project, define groups and events
After determining your Region(s), Datasets, and Industries, you can create a [Project](#create-project-post), add [Events](#create-event-post) to the project, and add [Groups](create-group-post) to the project with associated Events.

### Run an Impact on your project
Once your project has been defined, you can [Run an Impact](#run-impact-post) on your project.  Depending on the size of your project based on the number of events and groups, your project may take a few seconds or a few minutes to complete.  While waiting, you can poll for the [status](#run-status-get) of your project’s impact run. We recommend a polling frequency of 30 seconds.

### Export Results of the Impact
Once your project’s impact run has completed, you may export the [Results](#results) based on the impact run id.

## Glossary
You can find a detailed [Glossary](https://support.implan.com/hc/en-us/sections/16901820111003-Glossary) of economic terms on [support.implan.com](https://support.implan.com/hc/en-us/sections/16901820111003-Glossary), including [Events](https://support.implan.com/hc/en-us/articles/115009668408-Event) and [Groups](https://support.implan.com/hc/en-us/articles/360042981553-Groups), but in this section you will find terms unique to the API.

### URID
URID stands for Universal Region Identifier, and refers to a unique identifying number specific to a single implan region, such as a country, state, metropolitan statistical area (MSA), county, congressional district, or zip code.  A URID is a way to identify a geography before economic modeling data (such as multipliers) has been created. You may use a URID to combine single regions into a combined region, or to generate economic modeling data as a single region.

### HashID
A HashID is associated with a single region (like a URID), or can be associated with combined or customized regions that have built economic modeling data, and are ready to be used in impact analysis.  There are many underlying identifiers in the IMPLAN system associated with regions, and this field is a Hash of all of them so that you can provide a single identifier for the region you wish to study, and we can parse in our system to return the correct data.  

### AggregationSchemeId
### HouseholdSetId
## Postman Collection

We have created a Postman collection with reference calls per section in this document to help with implementation.  IMPLAN will provide credentials in a separate correspondence.  The latest Postman Collection is available for download below at:

[https://github.com/Implan-Group/api/blob/main/IMPLAN-API.postman_collection.json](https://github.com/Implan-Group/api/blob/main/IMPLAN-API.postman_collection.json) 


## Production Variables

<table>
  <tr>
   <td>Item
   </td>
   <td>Reference Value
   </td>
   <td>Production Value
   </td>
  </tr>
  <tr>
   <td>API Domain 
   </td>
   <td>{{api_domain}}
   </td>
   <td>https://api.implan.com/
   </td>
  </tr>
  <tr>
   <td>User Email
   </td>
   <td>{{email}}
   </td>
   <td>Same as app.implan.com
   </td>
  </tr>
  <tr>
   <td>User Password
   </td>
   <td>{{password}}
   </td>
   <td>Same as app.implan.com
   </td>
  </tr>
</table>

---
# Throttling Rates

The IMPLAN API will currently support the following requests per timeframe, to ensure a smooth operation for all customers. When exceeding these rates, you will receiving a throttling error response.
- Industry Codes
  - Requests per minute = 10
- Data Sets
  - Requests per minute = 10
- Region Models
  - Requests per minute = 5
- Instant
  - Requests per second = 5
- Batch
  - Requests per minute = 6
  - 2500 events per request supported.

---
# Authentication

## Bearer Access Token
- The ImpactAPI uses a [jwt](jwt.io) to store authentication information about your current user.
- You are required to send a valid Bearer Token with all Api requests.

### Retrieving the Token (non-SSO, non-M2M)
`POST {{api_domain}}api/auth`
You must include a `json` body that includes your username and password:

```json
{  
	"username": "{ImplanUsername}",
    "password": "{ImplanPassword}" 
}
```
- There are code examples in the [Appendix](#Appendix) for several languages on how to accomplish this.

### Single Sign On (SSO) & Machine to Machine (M2M)
- SSO and M2M customers _must_ use the following endpoint to retrieve their Bearer Token, substituting your `CLIENT_ID` and `CLIENT_SECRET` into the below:
```curl
curl --request POST \
  --url https://login.implan.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{"client_id":"CLIENT_ID","client_secret":"CLIENT_SECRET","audience":"https://services.implan.com","grant_type":"client_credentials"}'
```

### Response
```txt
Bearer {ENCODED_TEXT_HERE}
```

### Caching
- A retrieved Bearer Token is valid for 24 hours. It is required that you cache this token for all requests during this period. 
- Requesting excessive tokens (e.g. retrieving a new token for every single request) is not necessary, not supported, and may result in additional costs or temporary disabling of your account. Requesting additional tokens is supported for use cases such as system reboots. 

---
# Preliminary Requests to Running an Impact
Responses from the following endpoints are needed to provide information to get regional data, or run an impact analysis and receive results.  Once these are collected, you may proceed to get regional data or run an impact and get results.  

## Dataset Endpoint (Get)
IMPLAN models vary based on annual data sets.  In order to provide the correct list of models and industries, this API endpoint will provide a list of available data sets.  This response may be cached.  As data is released, IMPLAN will update the Default Data Set returned so that your application can update without maintenance.
#### Parameters
* Bearer Token
#### Response (List)
* Data Set ID (Number)
* Data Set Description (Text)
* Default Data Set (Boolean - only 1 record in the list should be true)
Will Return datasets
```
[   

	{

        "id": 59,

        "description": "2018",

        "isDefault": false

    },

    {

        "id": 77,

        "description": "2019",

        "isDefault": true

    }

]
```
#### Endpoint
**GET {{api_domain}}api/v1/datasets**


## Region Model Endpoint (Get)
Since region model id’s and underlying data can change each year, you will need to provide a Data Set ID as an input.  The Endpoint response will include a list of Region Names, Types, and Model ID’s.   The response may be cached.

The Regions that will be accessible by this API endpoint will include the regions purchased in their data subscription.

Take a dataset id from the dataset API request and use it for the model’s API request
#### Parameters
* Bearer Token
* Data Set Id 
#### Response (List)
* Model Id
* Region Type 
    * State
    * MSA
    * County
* Region Name
**  **
Will return Models
```
    [


        {


            "id": 8367,


            "description": "Mecklenburg County, North Carolina",


            "regionType": "County"


        },


        {


            "id": 8368,


            "description": "South Carolina",


            "regionType": "State"


        },


        {


            "id": 8467,


            "description": "Wyoming",


            "regionType": "State",


        }


    ]
```
#### Endpoint
**GET {{api_domain}}api/v1/models?datasetId=77**


## Industry Codes Endpoint (Get)
**Use with project analysis endpoints.  **The Industries supported by this API will be the current standard IMPLAN 546 Industry scheme. This response may be cached.  A list of those industries can be found here: [https://support.implan.com/hc/en-us/articles/360034896614-546-Industries-Conversions-Bridges-Construction-2018-Data](https://support.implan.com/hc/en-us/articles/15398463942683-U-S-546-Industries-Conversions-Bridges)

In 2022, the BEA will redefine the North American Industry Classifications System (NAICS) codes. This change will result in a change to the IMPLAN industry scheme for the 2023 IMPLAN data release. The API will then be updated to include these new industry designations when that data is added to the system.
#### Parameters
* Bearer Token
* `IndustrySetId` _(optional)_
  * If no `IndustrySetId` is specifed, the current default Industry Set will be used
#### Response
- A `json` response will include _all_ Industry Codes unless an optional `IndustrySetId` is specific, in which case the response will be filtered to only the Industry Codes from that Industry Set
```json
[
    {
        "id": 4638,
        "code": 1,
        "description": "Oilseed farming"
    },
    ...
    {
        "id": 5183,
        "code": 546,
        "description": "* Employment and payroll of federal govt, non-military"
    }
]
```
#### Endpoint
`GET {{api_domain}}api/v1/IndustryCodes`
`GET {{api_domain}}api/v1/IndustryCodes?industrySetId={{industrySetId}}`

## Industry Sets
- This endpoint provides a list of all the details about all existing Industry Sets
#### Parameters
- Bearer Token
#### Response
- `json` list of Industry Set details:
```json
[
    {
        "id": 1,
        "description": "440 Industries",
        "defaultAggregationSchemeId": null,
        "activeStatus": null,
        "isDefault": null,
        "mapTypeId": 1,
        "isNaicsCompatible": false,
        "sort": null
    },
    ...
    {
        "id": 11,
        "description": "46 Industries (2018 International)",
        "defaultAggregationSchemeId": 13,
        "activeStatus": true,
        "isDefault": null,
        "mapTypeId": 3,
        "isNaicsCompatible": false,
        "sort": 4
    }
]
```
#### Endpoint
`GET {{api_domain}}api/v1/industry-sets`

---

# Aggregation Schemes


## Aggregation Schemes Endpoint (Get)
This endpoint will return a list of aggregation schemes available for use.
#### Parameters
* Bearer Token
* `IndustrySetId` _(optional)_
#### Response (List)
* Id (Aggregation Scheme Id)
* Description
* Industry Set Id 
* Household Set Ids []
* Map Code
* Status
```json
[
    {
        "id": 1,
        "description": "536 Unaggregated",
        "industrySetId": 2,
        "householdSetIds": [
            1,
            2
        ],
        "mapCode": "US",
        "status": "Complete"
    },
    ...
    {
        "id": 1090,
        "description": "PHX-10001 Test",
        "industrySetId": 8,
        "householdSetIds": [
            1
        ],
        "mapCode": "US",
        "status": "Complete"
    }
]
```
#### Endpoints
`GET {{api_domain}}api/v1/aggregationschemes`
`GET {{api_domain}}api/v1/aggregationschemes?industrySetId={{industrySetId}}`


## Industry Margins Endpoint (Get)
This endpoint will return industry margins data in CSV format.
#### Parameters
* Bearer Token
* AggregationSchemeId (in url)
* DatasetId (in url)
#### Response (CSV)
* Paying Code
* Display Description
* Margin
#### Endpoint
**GET {{api_domain}}api/v1/margins/{{aggregationSchemeId}}/{{datasetId}}/industry-margins**


## Commodity Margins Endpoint (Get)
This endpoint will return commodity margins data in CSV format.
#### Parameters
* Bearer Token
* AggregationSchemeId (in url)
* DatasetId (in url)
#### Response (CSV)
* Paying Code
* Paying Description
* Receiving Code
* Receiving Description
* Margin
#### Endpoint
**GET {{api_domain}}api/v1/margins/{{aggregationSchemeId}}/{{datasetId}}/commodity-margins**

## Aggregation Scheme Details

- This endpoint returns the details for a single Aggregation Scheme

### Parameters

- Bearer Token
- `AggregationSchemeId` - Number - URL

### Response

```json
{
    "id": 10,
    "description": "IMPLAN 3 Digit NAICS 546",
    "industrySetId": 8,
    "householdSetIds": [
        1
    ],
    "mapCode": "US",
    "status": "Complete"
}
```

### Endpoint

- `GET {{api_domain}}api/v1/aggregationSchemes/{{AggregationSchemeId}}`



## Aggregation Scheme Industries

- This endpoint returns a list of my industries and the IMPLAN codes mapped to them for a single Aggregation Scheme

### Parameters

- Bearer Token
- `AggregationSchemeId` - Number - URL

### Response

```json
[
    {
        "displayCode": "492",
        "displayDescription": "Residential intellectual disability, mental health, substance abuse and other facilities",
        "codeFrom": 492,
        "codeTo": 492,
        "industryIdFrom": 5129,
        "industryIdTo": 5129
    },
    ...
    {
        "displayCode": "546",
        "displayDescription": "* Employment and payroll of federal govt, non-military",
        "codeFrom": 546,
        "codeTo": 546,
        "industryIdFrom": 5183,
        "industryIdTo": 5183
    }
]
```

### Endpoint

- `GET {{api_domain}}api/v1/aggregationSchemes/{{AggregationSchemeId}}/industry-mapping`



## Aggregation Scheme Commodities

- This endpoint returns a list of my commodities and the IMPLAN codes mapped to them for a single Aggregation Scheme

### Parameters

- Bearer Token
- `AggregationSchemeId` - Number - URL

### Response

```json
[
    {
        "displayCode": "3001",
        "displayDescription": "Oilseeds",
        "codeFrom": 3001,
        "codeTo": 3001,
        "commodityIdFrom": 1692,
        "commodityIdTo": 1692
    },
    ...
    {
        "displayCode": "3533",
        "displayDescription": "* Not a unique commodity (electricity from local govt utilities)",
        "codeFrom": 3533,
        "codeTo": 3533,
        "commodityIdFrom": 2237,
        "commodityIdTo": 2237
    }
]
```

### Endpoint
- `GET {{api_domain}}api/v1/aggregationSchemes/{{AggregationSchemeId}}/commodity-mapping`

  

## Create Custom Aggregation Scheme

- This endpoints lets an ImpactAPI consumer define a Custom Aggregation Scheme
- Just like in the IMPLAN Cloud platform, not all Industry Codes must be defined as part of a Sector. Any unmapped industries will automatically be added as-is to the Custom Aggregation Scheme.

### Parameters
- Bearer Token

### Request
```json
{  
    "description": "{{Custom Aggregation Scheme Name}}",  
    "industrysetid": {{IndustrySetId}},
    "groups": [  
        {  
            "description": "{{Group Description}}",  
            "sectors": [  
                {  
                    "description": "{{Sector Description}}",  
                    "code": {{Industry Code grouped in this Sector}}
                },  
            ...
                {  
                    "description": "{{Sector Description}}",  
                    "code": {{Industry Code grouped in this Sector}}
                }
            ]  
        },  
    ...
     {  
            "description": "{{Group Description}}",  
            "sectors": [  
                {  
                    "description": "{{Sector Description}}",  
                    "code": {{Industry Code grouped in this Sector}}
                },  
            ...
                {  
                    "description": "{{Sector Description}}",  
                    "code": {{Industry Code grouped in this Sector}}
                }
            ]  
        }  
    ]  
}
```

### Response
- A successful Custom Aggregation Scheme Creation request will respond with a single Number, the newly created `AggregationSchemeId`
- Other endpoints, such as `Aggregation Scheme Details`, can be used to determine when the Custom Aggregation Scheme finishes building

### Endpoint
- `GET {{api_domain}}api/v1/aggregationSchemes/create-custom-industry-aggregation-scheme`



---

# Regions

## Getting Regional Data
If you need to download study area data or obtain regional information to build regions, these endpoints will be helpful.
### Get Region Types (Get)
This endpoint returns region types that can be used for region type filtering in the designated endpoints that follow.
#### Parameters
* Bearer Token
#### Endpoint
**GET {{api_domain}}api/v1/region/RegionTypes**



---
## Top Level Region
- This endpoint will return the top most Region for an Aggregation Scheme and Dataset.
- You may use optional parameter [URID](#urid) to get Region Children
- For now, only United States and Canadian Industry Sets are supported, International Industry Sets will return an error message. Please use the Top Level Region Children endpoint with no filter to retrieve a list of all supported Countries

#### Request
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}`
	- `aggregationSchemeId` (number, required): Aggregation Scheme
	- `datasetId` (number, required): Dataset Id

#### Response
- Returns the Regional information for the Top-Level region for a given Aggregation Scheme and Dataset
- Example:
```json
{
    "hashId": "BEbD05WXb2",
    "urid": 1775072,
    "userModelId": null,
    "description": "United States (US Totals)",
    "modelId": 13188,
    "modelBuildStatus": "Complete",
    "employment": 207667600.00000018,
    "output": 45886905211009.836,
    "valueAdded": 25744109000000.02,
    "aggregationSchemeId": 8,
    "datasetId": 92,
    "datasetDescription": "2022 Archive",
    "fipsCode": "00000",
    "provinceCode": null,
    "m49Code": "840",
    "regionType": "Country",
    "hasAccessibleChildren": false,
    "regionTypeDescription": "Country",
    "geoId": "840",
    "isMrioAllowed": false
}
```

---
## Top Level Region Children
- This endpoint returns all Children Regions (children of the Top Level Region) for a given Aggregation Scheme and Dataset
- An optional filter can limit the response region types
- Use this endpoint for International Industry Sets (with no Region Type Filter) to get a list of all supported Country Regions

#### Request
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/children`
	- `aggregationSchemeId` (number, required): Aggregation Scheme
	- `datasetId` (number, required): Dataset Id
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/children?regionTypeFilter={{regionType}}`
	- `aggregationSchemeId` (number, required): Aggregation Scheme
	- `datasetId` (number, required): Dataset Id
	- `regionType`: An optional filter to limit the Region Types returned
	  - Valid options are `Country`, `State`, `MSA`, `County`, `CongressionalDistrict`, and `ZipCode`

- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/{{urid|hashid}}/children`
	- `aggregationSchemeId` (number, required): Aggregation Scheme
	- `datasetId` (number, required): Dataset Id
	- `urid`: The URID for the top level region to get the Child Regions for

#### Response
- A list of all Children Regions matching the criteria will be returned
```json
[
    {
        "hashId": "LAVBMvDNb1",
        "urid": 1819295,
        "userModelId": null,
        "description": "Kentucky",
        "modelId": 15059,
        "modelBuildStatus": "Complete",
        "employment": 2608978.2972790226,
        "output": 561195509364.5885,
        "valueAdded": 264866590387.3677,
        "aggregationSchemeId": 8,
        "datasetId": 96,
        "datasetDescription": "2022",
        "fipsCode": "21",
        "provinceCode": null,
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": true,
        "regionTypeDescription": "State",
        "geoId": "21",
        "isMrioAllowed": true
    },
    ...
    {
        "hashId": "W9b1AO5Nb5",
        "urid": 1819287,
        "userModelId": null,
        "description": "Delaware",
        "modelId": 15051,
        "modelBuildStatus": "Complete",
        "employment": 625328.0472749957,
        "output": 148446407436.51935,
        "valueAdded": 90372082246.67789,
        "aggregationSchemeId": 8,
        "datasetId": 96,
        "datasetDescription": "2022",
        "fipsCode": "10",
        "provinceCode": null,
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": true,
        "regionTypeDescription": "State",
        "geoId": "10",
        "isMrioAllowed": true
    }
]
```

---
### User Custom and Combined Regions (Get)
This endpoint will return all combined and custom regions that a user created by aggregation scheme and data set.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)
#### Endpoint
**GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/user**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### User Custom and Combined Regions (Get)
This endpoint will return all combined and custom regions that a user created. Parameters can be provided for filtering.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (Optional Parameter)
* Data Set ID (Optional Parameter)
#### Endpoint
**GET {{api_domain}}api/v1/region/user**\
**GET {{api_domain}}api/v1/region/user?aggregationSchemeId={{aggregationSchemeId}}**\
**GET {{api_domain}}api/v1/region/user?datasetId={{datasetId}}**\
**GET {{api_domain}}api/v1/region/user?aggregationSchemeId={{aggregationSchemeId}}&datsetId={{datasetId}}**


#### Get User Custom and/or Combined Region (Get)
This endpoint returns a region card for a specific user created combined and/or custom region.
#### Parameters
* Bearer Token
* HashId ID (in URL)
#### Endpoint
**GET {{api_domain}}api/v1/region/user/{{hashId}}**


### Get Regions by Urid (Get)
This endpoint allows a user to pull high level region information by a specific urid, within an aggregation scheme and data set.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)
* URID (in URL)
#### Endpoint
**GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/{{urid}}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Get Regions Children by Urid (Get)
This endpoint allows a user to pull high level region information for all children regions directly under a specific urid, within an aggregation scheme and data set.  It will only pull direct children descendants, so if a country urid is provided, this will return states. If a state is provided, it will return Counties, MSA’s, and Congressional Districts.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)
* URID (in URL)*
* Optional Region Type Filter
#### Endpoint
**GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/{{urid}}/children?regionTypeFilter={{regionType}}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Regional Data Response
The preceding Region endpoints all have the same response.
#### Response (List)
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId



## Building Regions
Not all economic models are built for regions by default, or sometimes you may want to combine regions.  Combining regions is used to create a custom group of counties, ZIP codes, MSAs, and/or states and treat them as one economic region that can be studied. The endpoints defined in this section may be used to build single or combined regions.  

We have endpoints that will start the economic model build process right away, but if you need to build more than 5 regions at a time, we recommend you leverage our batch region endpoints.

### Built Models (GET)
This endpoint returns a list of currently built models accessible to the user.
#### Parameters
* Aggregation Scheme Id (In URL)
* Dataset Id (InURL)
#### Response (list)
* HashId
* Urid
* UserModelId
* Description
* ModelId
* ModelBuildStatus
* Employment
* Output
* ValueAdded
* AggregationSchemeId
* DatasetId
* DatasetDescription
* FipsCode
* ProvinceCode
* M49Code
* RegionType
* HasAccessibleChildren
* GeoId
* IsMrioAllowed
#### Endpoint
**GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/built**


### Build Region - Batch (POST)
This endpoint will allow a user to batch build single regions by urid and aggregation scheme.  Specify the aggregation scheme id in the url, and the urid or list of urids separated by a comma in the body.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* URID (in body)
#### Response (List)
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId
#### Endpoint
**POST {{api_domain}}api/v1/region/build/batch/{{aggregationSchemeId}}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Build Combined Region - Batch (POST)
This endpoint will allow a user to build multiple combined regions  by providing the urids to combine and an aggregation scheme.  Specify the aggregation scheme id in the url, and the list of urids separated by a comma in the body.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* Description (in body)
* URID (in body)
* Optional - Type of Request Body (CSV/JSON)
    1. If you would prefer to upload your URID’s in a CSV format, you may do so by specifying CSV for the {{type}} parameter
#### Response (List)
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId
#### Endpoint
**POST {{api_domain}}api/v1/region/build/batch/combined/{{aggregationSchemeId}}/{{type}}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Build Combined Region (POST)
This endpoint will allow a user to build a single combined region by providing the urids to combine and an aggregation scheme.  Specify the aggregation scheme id in the url, and the  list of urids separated by a comma in the body.
#### Parameters
* Bearer Token
* Aggregation Scheme ID (in URL)
* Description (in body)
* URID (in body)
#### Response (List)
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId
#### Endpoint
**POST {{api_domain}}api/v1/region/build/combined/{{aggregationSchemeId}}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries

---

# Regions - Build and Return
<p>
This endpoint allows a user to submit a list of Regional Identifiers.
Any regions in the list that have not yet been built will be, and then the full list of hydrated [[Region Cards|RegionCards]] will be returned.
</p>
<p>
Instead of using this endpoint, it is possible to pull down a full list of Regions and then submit only the ones that need to be built to the [[Build Regions|BuildRegions]] endpoint.
</p>


## ⬆️ Request(s)
### `POST {api_domain}api/v1/region/build-and-return/{AggregationSchemeId}`
- [[AggregationSchemeId|AggregationSchemes]] - Aggregation Scheme Id

#### Request Body
- Must include a list of the Regional Identifiers ([[HashIds|HashIds]] or [[Urids|Urids]]) for the Regions that need to be built and returned. 
```json
[
    "p0aRdZl0VJ",
    1905981
]
```


## ⬇️ Response
- The expected response is `json`

### Example Response:
```json
[
  {
    "hashId": "wlx6e9WwVk",
    "urid": 1905008,
    "userModelId": null,
    "modelId": 17026,
    "description": "Marion County, OR",
    "modelBuildStatus": "Complete",
    "employment": 0.0,
    "output": 0.0,
    "valueAdded": 0.0,
    "isCustomized": false,
    "isCombined": false,
    "regionType": "County",
    "datasetId": 98,
    "datasetDescription": "2023",
    "parentRegionIds": [
      {
        "regionType": "Msa",
        "hashId": "W1aQlLzoxj",
        "urid": 1862706
      },
      {
        "regionType": "State",
        "hashId": "9pbP1nM0VN",
        "urid": 1863644
      }
    ],
    "isMrioAllowed": true,
    "isCustomizable": true,
    "isCombinable": true,
    "hasAccess": true,
    "hasAccessibleChildren": false,
    "regionTypeDescription": "County",
    "regionTypeSort": 3,
    "geoId": "41047",
    "congressionalSession": null
  },
  ...
]
```



---

## Customizing Regions

Regions can be customized using the endpoints provided below. For each type of customization, one endpoint will provide regional data that can be used for creating modifications and the other endpoint accepts the modification request.

Note: a region must be built prior to making modifications.

### Economic Industry Data (GET)
This endpoint returns region specific industry data to use as a starting place for making industry customizations.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId, URID, or UserModelId (URL Parameter)
#### Response
* Is Customized (Bool indicating if the model's industry data has been previously modified)
* Industry Economic Data (array)
  * Industry Id
  * Industry Description
  * Output
  * Employment
  * Employee Compensation
  * Proprietor Income
  * Other Property Type Income
  * Tax on Production and Imports
#### Endpoint
**POST {{api_domain}}api/v1/region/EconomicIndustryData/{{aggregationSchemeId}}?hashId={{hashId}}**


### Customize Industry (POST)
This endpoint initiates a new model build that incorporates user provided industry customizations. Only the industries being customized need to be provided in the request body customization array. All fields must be provided for each customization.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId, URID, or UserModelId (in body)
* Model Name (User provided model name)
* Customized Industry Data (array of industry customizations) 
  * Industry Id
  * Output
  * Employment
  * Employee Compensation
  * Proprietor Income
  * Other Property Type Income
  * Tax on Production and Imports
#### Response
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId
#### Endpoint
**POST {{api_domain}}api/v1/region/build/CustomizeIndustry/{{aggregationSchemeId}}**


### Economic Commodity RPC Data (GET)
This endpoint returns region specific average commodity RPC data to use as a starting place for making RPC customizations.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId, URID, or UserModelId (URL Parameter)
#### Response
* Is Customized (Bool indicating if the model's average commodity RPC data has been previously modified)
* Commodity RPC Data (array)
  * Commodity Id
  * Commodity Description
  * Total Commodity Supply
  * Total Gross Commodity Demand
  * Local Use of Local Supply
  * Local Use Ratio
  * Average RPC
  * Foreign Export
  * Foreign Import
  * Is Modifiable
#### Endpoint
**POST {{api_domain}}api/v1/region/EconomicCommodityRPCData/{{aggregationSchemeId}}?hashId={{hashId}}**


### Customize Average Commodity RPC (POST)
This endpoint initiates a new model build that incorporates user provided average commodity RPC customizations. Only the commodity RPCs being customized need to be provided in the request body customization array. All fields must be provided for each customization.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId, URID, or UserModelId (in body)
* Model Name (User provided model name)
* Customized Average Commodity RPC Data (array of commodity RPC customizations)
  * Commodity Id
  * Total Commodity Supply
  * Total Gross Commodity Demand
  * Local Use Of Local Supply 
  * Local Use Ratio
  * Average Rpc
  * Foreign Export
  * Foreign Import
#### Response
* Id
* Urid
* userModelId
* Description
* modelId
* modelBuildStatus
* Employment
* Output
* valueAdded
* aggregationSchemeId
* datasetId
* datasetDescription
* fipsCode
* provinceCode
* m49Code
* regionType
* hasAccessibleChildren
* regionTypeDescription
* geoId
#### Endpoint
**POST {{api_domain}}api/v1/region/build/CustomizeAverageRPC/{{aggregationSchemeId}}**

---
# Regional Data Exports
These endpoints export region specific data for a built model. Data is exported in either CSV or Zip format depending on the endpoint.

---
## Region Overview Industries
- This endpoint provides regional industry overview data equivalent to the Industries table found in `Regions > Regions Overview` in the IMPLAN application
- This endpoint is used for US and Canadian regions. While International regions will work, the returned data will include only Zeros under `Average Proprietor Income per Proprietor`
    - Please use an alternate endpoint for International regions by including `intl` in the path between `export` and the `{aggregationSchemeId}:
    - `{{api_domain}}api/v1/regions/export/intl/{{AggregationSchemeId}}/RegionOverviewIndustries`

#### Request
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionOverviewIndustries?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionOverviewIndustries?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionOverviewIndustries?userModelId={{userModelId}}`
- `AggregationSchemeId` - The Aggregation scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- The API response will provide a CSV response with following fields for all industries:
* Display Code
* Display Description
* Employment
* Labor Income
* Output
* Average Employee Compensation per Wage and Salary Employee
* Average Proprietor Income per Proprietor


---
### Study Area Data General Information (Get)
This endpoint provides regional General Information such as population, land area, and industry count. This data is equivalent to that found on tables in Regions > Regions Overview and Study Area Data > Area Demographics. 
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Region Name
* Fips
* Population
* Land Area
* Dataset year
* Industry Aggregation Description
* Commodity Aggregation Description
* Industry Count
* Total Personal Income
* Total Household Count by Household Group
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataGeneralInformation?hashId={{hashId}}**

---
## Study Area - Industry Detail
- This endpoint provides regional industry detail data equivalent to the Region Industries Detail table found in `Regions > Study Area Data > Industry Detail` in the IMPLAN application.
- This endpoint is used for US and Canadian regions _only_
- Please use an alternate endpoint for International regions by including `intl` in the path between `export` and the `{aggregationSchemeId}:
    - `{{api_domain}}api/v1/regions/export/intl/{{AggregationSchemeId}}/StudyAreaDataIndustryDetail`

#### Request
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataIndustryDetail?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataIndustryDetail?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataIndustryDetail?userModelId={{userModelId}}`
- `AggregationSchemeId` - The Aggregation scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- The API response will provide a CSV response with following fields for all industries:
* Industry Code
* Description
* Total Output
* Wage and Salary Employment
* Employee Compensation
* Proprietor Employment
* Proprietor Income
* Other Property Income
* Taxes on Production and Imports Net of Subsidies
- The final two columns will be named `Gross Operating Surplus` and `Other Taxes on Production Net of Subsidies` in the case of International, to more accurately reflect the data.

---

## Study Area - Industry Averages

- These endpoint provide regional Industry Averages data equivalent to the Region Industry Averages table found in `Regions > Study Area Data > Industry Averages` in the IMPLAN application.

#### Request

- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/industry-averages?hashId={{hashId}}`
  - This endpoint is used for US regions

- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/industry-averages/can?hashId={{hashId}}`
  - This endpoint is used for Canadian regions

- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/industry-averages/intl?hashId={{hashId}}`
  - This endpoint is used for International regions    

- `aggregationSchemeId` - The Aggregation Scheme for the Region
- `hashId` - The Region's HashId

#### Response

- The API response will provide a CSV response with following fields for all industries:
  - `Sort Field`
  - `Display Code`
  - `Description`
  - `Industry Code`
  - `Output per Worker`
  - `Labor Income per Worker`
  - `Employee Compensation per Employee`
  - `Proprietor Income per Proprietor`
    - This field does not exist for International Models
  - `Taxes on Production and Imports per Worker`
  - `Other Property Income per Worker`

---
## Study Area Industry Summary (Get)
- This endpoint provides regional industry summary data equivalent to the Region Industries Summary table found in Regions > Study Area Data > Industry Summary in the IMPLAN application.

#### Request
- `GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataIndustrySummary?hashId={{hashId}}`
- `GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/StudyAreaDataIndustrySummary?urid={{urid}}`
- `AggregationSchemeId` - The Aggregation scheme for the Region
- One of `hashId` or `urid` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- The API response will provide a CSV response with following fields for all industries:
* Industry Code
* Description
* Total Employment
* Total Output
* Total Intermediate Inputs
* Total Value Added
* Labor Income

---
## Institution Commodity Demand (Get)
This endpoint provides regional institution commodity demand data equivalent to the `Regions Institution Commodity Demand` dashboard in `Regions > Study Area Data > Institution Commodity Demand` in the IMPLAN application.
#### Request
- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-institution-commodity-demand?hashId={{hashId}}`
    - This endpoint is used for US regions
- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-institution-commodity-demand/can?hashId={{hashId}}`
    - This endpoint is used for Canadian regions
- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-institution-commodity-demand/intl?hashId={{hashId}}`
    - This endpoint is used for International regions
- `AggregationSchemeId` - The Aggregation scheme for the Region
- `hashId` _must_ be specified alongside this request
    - This is the ID for the Region
#### Response
- The API response will provide a csv response containing the following data:
  - `Display Code`
  - `Display Description`
  - `Sum of Households`
  - `Sum of Federal Government` (US Data Only)
  - `Sum of State and Local Government` (US Data Only)
  - `Government` (Canada and International Only)
  - `Capital`
  - `Inventory`
  - `Domestic Exports`
  - `Foreign Exports`

---
## Area Demographics (Get)
This endpoint provides regional demographic data equivalent to the `Area Demographics` dashboard in `Regions > Study Area Data > Area Demographics `in the IMPLAN application.
#### Request
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/study-area-data-area-demographics?hashId={{hashId}}`
- `AggregationSchemeId` - The Aggregation scheme for the Region
- `hashId` _must_ be specified alongside this request
    - This is the ID for the Region
#### Response
- The API response will provide a zip file containing a csv file per demographic category. CSV files returned are dictated by the level of demographic data available for the dataset. Examples include:
* Land Area and Population
* Households
* Age and Sex
* Language Spoken at Home
* Race and Ethnicity
* Regional Employee Wage & Salary Income by Place of Residence
* Resident Wage & Salary Income by Place of Work
* Housing: Occupancy and Vacancy
* Labor Force Participation Rate: By Race
* Labor Force Participation Rate: By Age
* Unemployment Rate: By Race
* Unemployment Rate: By Age
* Educational Attainment Ages 18-24
* Educational Attainment Ages 25+

---
### Region Multipliers Detailed (Get)
This endpoint provides detailed multipliers by a given type and industry as found in the Regions > Multipliers > Detailed Multipliers tables in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* EffectType 
  * Options include
    * Employment
    * EmployeeCompensation
    * ProprietorIncome
    * OtherPropertyIncome
    * TaxesOnProductionAndImports
    * LaborIncome
    * Output
    * TotalValueAdded
  * International industry set options include
    * Employment
    * EmployeeCompensation
    * GrossOperatingSurplus
    * OtherTaxesOnProductionNetOfSubsidies
    * LaborIncome
    * Output
    * TotalValueAdded
* IndustryCode
#### Response
The API response will provide a CSV response with following fields:
* Display Code
* Display Description
* Industry Code
* Indirect Multiplier Sum
* Type I Multiplier
* Induced Multiplier
* Type SAM Multiplier
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionMultipliersDetailed?hashId={{hashId}}&effectType={{effectType}}&industryCode={{industryCode}}**


### Region Multipliers Summary (Get)
This endpoint provides summary multipliers by a given type as found in the Regions > Multipliers > Summary Multipliers tables in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* EffectType
    * Options include
        * Employment
        * EmployeeCompensation
        * ProprietorIncome
        * OtherPropertyIncome
        * TaxesOnProductionAndImports
        * LaborIncome
        * Output
        * TotalValueAdded
    * International industry set options include
        * Employment
        * EmployeeCompensation
        * GrossOperatingSurplus
        * OtherTaxesOnProductionNetOfSubsidies
        * LaborIncome
        * Output
        * TotalValueAdded
#### Response
The API response will provide a CSV response with following fields:
* Display Code
* Display Description
* Indirect Multiplier Sum
* Type I Multiplier
* Induced Multiplier
* Type SAM Multiplier
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-multipliers-summary?hashId={{hashId}}&effectType={{effectType}}**


### Region Multipliers Per Million Effects (Get)
This endpoint provides per million of output effects by a given type and industry as found in the Regions > Multipliers > Per Million Effects tables in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* EffectType
    * Options include
        * Employment
        * EmployeeCompensation
        * ProprietorIncome
        * OtherPropertyIncome
        * TaxesOnProductionAndImports
        * LaborIncome
        * Output
        * TotalValueAdded
    * International industry set options include
        * Employment
        * EmployeeCompensation
        * GrossOperatingSurplus
        * OtherTaxesOnProductionNetOfSubsidies
        * LaborIncome
        * Output
        * TotalValueAdded
#### Response
The API response will provide a CSV response with following fields:
* Display Code
* Display Description
* Industry Code
* Direct Effects
* Indirect Effects
* Induced Effects
* Type I Effects
* Type SAM Effects
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionMultipliersPerMillionEffects?hashId={{hashId}}&effectType={{effectType}}**


### Region Commodity Summary (Get)
This endpoint provides commodity summary data as found in the Regions > Social Accounts > Reports > Commodity Summary > Commodity Summary table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Commodity Code
* Description
* Industry Commodity Production
* Institutional Commodity Production
* Total Commodity Supply
* Local Use of Local Supply
* Intermediate Commodity Demand
* Institutional Commodity Demand
* Total Gross Commodity demand
* Domestic S/D Ratio
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-summary?hashId={{hashId}}**


### Region Commodity Summary Averages (Get)
This endpoint provides commodity summary averages data as found in the Regions > Social Accounts > Reports > Commodity Summary > Commodity Summary Averages table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Commodity Code
* Description
* Average RPC
* Average RSC
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-summary-averages?hashId={{hashId}}**

### Region Commodity Exports (Get)
This endpoint provides commodity exports data as found in the Regions > Social Accounts > Reports > Commodity Trade > Commodity Exports table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Commodity Code
* Description
* Industry Exports
* Institutional Exports
* Domestic Exports
* Foreign Exports
* Total Exports
* Foreign Export Proportion
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-exports?hashId={{hashId}}**

### Region Commodity Imports (Get)
This endpoint provides commodity imports data as found in the Regions > Social Accounts > Reports > Commodity Trade > Commodity Imports table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Commodity Code
* Description
* Intermediate Imports
* Institutional Imports
* Domestic Imports
* Foreign Imports
* Total Imports
* Foreign Import Proportion
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-imports?hashId={{hashId}}**


### Region Household Local Commodity Demand (Get)
This endpoint provides per household local commodity demand as found in the Regions > Study Area Data > Household Commodity Demand table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields (per commodity):
* Commodity Code
* Description
* Household cateogry (one column per household category)
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionHouseholdLocalCommodityDemand?hashId={{hashId}}**


### Region Household Commodity Demand (Get)
This endpoint provides per household total commodity demand as found in the Regions > Study Area Data > Household Commodity Demand table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields (per commodity):
* Commodity Code
* Description
* Household Cateogry (one column per household category)
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionHouseholdCommodityDemand?hashId={{hashId}}**


---
## Region Industry Commodity Production (Get)
This endpoint provides commodity production data for a given industry as found in the `Regions > Social Accounts > Balance Sheets > Industry Balance Sheets > Commodity Production` table in the IMPLAN application.
#### Request
- `GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/region-industry-commodity-production/{{industryCode}}?hashId={{hashId}}`
- `AggregationSchemeId` - The Aggregation scheme for the Region
- `IndustryCode` - The industry specification code
- `hashId` _must_ be specified alongside this request
    - This is the ID for the Region
#### Response
- The API response will provide a csv response containing the following data:
    - `Code`
    - `Description`
    - `Commodity Production`
    - `Byproduct Coefficient`
    - `Regional Market Share`

---


### Region Industry Commodity Demand (Get)
This endpoint provides commodity demand data for a given industry as found in the Regions > Social Accounts > Balance Sheets > Industry Balance Sheets > Commodity Demand table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* IndustryCode (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Code
* Description
* RPC
* Gross Absorption
* Gross Inputs
* Regional Absorption
* Regional Inputs
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-industry-commodity-demand/{{IndustryCode}}?hashId={{hashId}}**


### Region Industry Value Added (Get)
This endpoint provides industry value added data for a given industry as found in the Regions > Social Accounts > Balance Sheets > Industry Balance Sheets > Value Added table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* IndustryCode (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Description
* Value Added Coefficient
* Value Added
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-industry-value-added/{{IndustryCode}}?hashId={{hashId}}**


### Region Industry Institutional Production (Get)
This endpoint provides commodity production data for a given commodity by industries and institutions as found in the Regions > Social Accounts > Balance Sheets > Commodity Balance Sheet > Industry-Institutional Production table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* CommodityCode (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Code
* Description
* Industry/Institutional Production
* Regional Market Share
* Coefficient
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-industry-institutional-production/{{CommodityCode}}?hashId={{hashId}}**


### Region Commodity Industry Demand (Get)
This endpoint provides industry demand data for a given commodity as found in the Regions > Social Accounts > Balance Sheets > Commodity Balance Sheets > Industry Demand table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* CommodityCode (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Industry Code
* Description
* RPC
* Gross Absorption
* Gross Inputs
* Regional Absorption
* Regional Inputs
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-industry-demand/{{CommodityCode}}?hashId={{hashId}}**


### Region Commodity Institutional Demand (Get)
This endpoint provides institutional demand data for a given commodity as found in the Regions > Social Accounts > Balance Sheets > Commodity Balance Sheets > Institutional Demand table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* CommodityCode (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Code
* Description
* RPC
* Gross Demand
* Regional Demand
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-commodity-institutional-demand/{{CommodityCode}}?hashId={{hashId}}**

---
## Region Institution Industry Demand
- This endpoint provides institution industry demand data as found in the `Regions > Industry Accounts > Reports > Institution Industry Demand` table in the IMPLAN application
- This endpoint works for United States, Canadian, and International Industry Sets so long as an appropriate Aggregation Scheme is used alongside the region's HashId

#### Request
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-institution-industry-demand?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-institution-industry-demand?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-institution-industry-demand?userModelId={{userModelId}}`
- `aggregationSchemeId` - The Aggregation Scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- The API response will provide a CSV response with following fields:
* Code
* Description
* Household Demand
* Federal Government Demand
* State and Local Government Demand
* Capital
* Inventory
* Domestic Exports
* Foreign Exports


---
### Region Industry Output/Outlay Summary (Get)
This endpoint provides industry output/outlay data as found in the Regions > Industry Accounts > Reports > Industry Output/Outlay Summary table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a CSV response with following fields:
* Display Code
* Display Description
* Total Outlay
* Intermediate Outlay
* Institutional Outlay
* Intermediate Imports
* Value Added
* Total Output
* Intermediate Output
* Final Demand
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-industry-output-outlay-summary?urid={{urid}}**


### Region General Algebraic Modeling System Files (Get)
This endpoint provides a zip file containing .dat files for use in GAMS systems.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a zip file containing multiple .dat files.
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionGeneralAlgebraicModeling?hashId={{hashId}}**


### Region General Algebraic Modeling System Single File (Get)
This endpoint provides a single .gms file for use in GAMS systems.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
#### Response
The API response will provide a .gms file.
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/region-general-algebraic-modeling-single-file?hashId={{hashId}}**


### Region Industry Occupation Detail (Get)
This endpoint provides industry occupation detail as found in the Regions > Occupation Data > Industry Occupation Detail table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Occupation Data Year (in body)
* Occupation Aggregation Level (in body)
* Industry Code (in body)
* Occupation Code Filter (in body; array)
#### Response
The API response will provide a CSV response with following fields (per occupation):
* OCC Code
* Occupation
* Wage and Salary Employment
* Wage and Salary Income
* Supplements to Wages and Salaries
* Employee Compensation
* Hours Worked
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionIndustryOccupationDetail?hashId={{hashId}}**


### Region Industry Occupation Averages (Get)
This endpoint provides industry occupation averages as found in the Regions > Occupation Data > Industry Occupation Averages table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Occupation Data Year (in body)
* Occupation Aggregation Level (in body)
* Industry Code (in body)
* Occupation Code Filter (in body; array)
#### Response
The API response will provide a CSV response with following fields (per occupation):
* OCC Code
* Occupation
* Average Wage and Salary Income
* Average Supplements to Wages and Salaries
* Average Employee Compensation
* Average Hours per Year
* Average Wage and Salary Income per Hour
* Average Supplements to Wages and Salaries per Hour
* Average Employee Compensation per Hour
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionIndustryOccupationAverages?hashId={{hashId}}**


### Region Core Competencies Region Summary (Get)
This endpoint provides a zip file containing CSV files for each table as found in Regions > Occupation Data > Core Competencies > Region Summary in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Occupation Data Year (in body)
* Occupation Aggregation Level (in body)
#### Response
The API response will provide a zip file with a collection of CSV files representing the region core competencies summary tables.
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionCoreCompetenciesRegionSummary?hashId={{hashId}}**


### Region Core Competencies Industry Summary (Get)
This endpoint provides a zip file containing CSV files for each table as found in Regions > Occupation Data > Core Competencies > Industry Summary in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Occupation Data Year (in body)
* Occupation Aggregation Level (in body)
* Industry Code (in body)
#### Response
The API response will provide a zip file with a collection of CSV files representing the region core competencies industry summary tables.
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionCoreCompetenciesIndustrySummary?hashId={{hashId}}**


### Region Core Competencies Occupation Summary (Get)
This endpoint provides a zip file containing CSV files for each table as found in Regions > Occupation Data > Core Competencies > Occupation Summary in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Occupation Data Year (in body)
* Occupation Aggregation Level (in body)
* Occupation Code (in body)
#### Response
The API response will provide a zip file with a collection of CSV files representing the region core competencies occupation summary tables.
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/RegionCoreCompetenciesOccupationSummary?hashId={{hashId}}**


### Environmental Region Summary (Get)
This endpoint provides a CSV file containing environmental summary data as found in Regions > Environmental > Region Environmental Summary table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Environment Release String (in body; required)
* Industry Codes (in body; array)
#### Response
The API response will provide a CSV response with the following fields (per industry).
* Industry
* Environmental Output
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/EnvironmentSummary?hashId={{hashId}}**


### Environmental Region Details (Get)
This endpoint provides a CSV file containing environmental detail data as found in Regions > Environmental > Region Environmental Details table in the IMPLAN application.
#### Parameters
* Bearer Token
* AggregationSchemeId (In URL)
* HashId or URID (required)
* Environment Release String (in body; required)
* Industry Codes (in body; optional*)
* Environment Category (in body; required)
*NOTE: HashId or URID must be supplied, but both are not required.
#### Response
The API response will provide a CSV response with the following fields (per environment name). There is a 5000 row limit to the amount of data returned.
* Environment Name
* Environment Context
* Environment Unit
* Units per $ of Output
* Environmental Output
#### Endpoint
**GET {{api_domain}}api/v1/regions/export/{{AggregationSchemeId}}/EnvironmentDetail?hashId={{hashId}}**

---
## Region Detail IxI SAM
- This endpoint provides a zipped CSV file containing a region's IxI SAM output, the same as `Region Details > Industry Accounts > IxI Social Accounting Matrix > Export Detail IxI SAM`
- This endpoint works for United States, Canadian, and International Industry Sets so long as an appropriate Aggregation Scheme is used alongside the region's HashId

#### Request
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxISam??hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxISam?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxISam??userModelId={{userModelId}}`
- `aggregationSchemeId` - The Aggregation Scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- A zipped CSV file


---
## Region Detail IxC SAM
- This endpoint provides a zipped CSV file containing a Region's IxC SAM output, the same as `Region Details > Social Accounts > IxC Social Accounting Matrix > Export Detail IxC SAM`
- This endpoint works for United States, Canadian, and International Industry Sets so long as an appropriate Aggregation Scheme is used alongside the region's HashId

#### Request
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxCSam?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxCSam?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/StudyAreaDataDetailIxCSam?userModelId={{userModelId}}`
- `aggregationSchemeId` - The Aggregation Scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- A zipped CSV file

---
## Region Aggregate IxI SAM
- This endpoint provides a CSV file containing a Region's Aggregate IxI SAM output, the same as `Region Details > Industry Accounts > IxI Social Accounting Matrix > Aggregate IxI SAM`

#### Request
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixi-sam?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixi-sam?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixi-sam?userModelId={{userModelId}}`
- `aggregationSchemeId` - The Aggregation Scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- A CSV file with the following columns:
	- PayingCode, PayingDescription, ReceivingCode, ReceivingDescription, Value

---
## Region Aggregate IxC SAM
- This endpoint provides a CSV file containing a Region's Aggregate IxC SAM output, the same as `Region Details > Social Accounts > IxC Social Accounting Matrix > Aggregate IxC SAM`

#### Request
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixc-sam?hashId={{hashId}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixc-sam?urid={{urid}}`
`GET {{api_domain}}api/v1/regions/export/{{aggregationSchemeId}}/study-area-data-aggregate-ixc-sam?userModelId={{userModelId}}`
- `aggregationSchemeId` - The Aggregation Scheme for the Region
- One of `hashId`, `urid`, or `userModelId` _must_ be specified alongside this request
    - This is the ID for the Region

#### Response
- A CSV file with the following columns:
	- PayingCode, PayingDescription, ReceivingCode, ReceivingDescription, Value

---
# Impacts
After the authentication token, and responses have been collected from the API endpoints above, you may then proceed with running an impact analysis. The starting point for this is to create a project.  

Inside the project, you will define the Events, which are the changes to an economy that you want to analyze, and the groups, which are the regions and time frame the changes take place.  After defining your Project, Events, and Groups, you may Run the Impact, and poll for a status on the Impact Run. 

### Create Project (Post)
#### Parameters
* Title
* AggregationSchemeId - Default to 8
* HouseholdSetId - Default to 1
* IsMrio (Optional)
* folderId (Optional)
#### Response
* Id - This will be used on all subsequent Project, Event, and Group API Requests
* Title
* aggregationSchemeId
* householdSetId
* isMrio
* folderId
#### Endpoint
**POST {{api_domain}}api/v1/impact/project**


### Get Project (Get)
#### Parameters
* Project id (In URL)
#### Response
* Id - This will be used on all subsequent Project, Event, and Group API Requests
* Title
* aggregationSchemeId
* householdSetId
* isMrio
* folderId
#### Endpoint
**GET {{api_domain}}api/v1/impact/project/{{project id}}**


### Get Projects (Get)
Returns a list of all non-deleted projects owned by the user. If the deleted parameter is passed as true, then returns a list of all deleted projects owned by the user. 
#### Parameters
* deleted
#### Response
Array of the following:
* Id - This will be used on all subsequent Project, Event, and Group API Requests
* Title
* aggregationSchemeId
* householdSetId
* isMrio
* folderId
* LastImpactRunId
#### Endpoint
**GET {{api_domain}}api/v1/impact/project**

**GET {{api_domain}}api/v1/impact/project?deleted=true**


### Get Projects Shared With User (Get)
Returns a list of all projects shared with the user
#### Parameters
none
#### Response
Array of the following:
* Id - This will be used on all subsequent Project, Event, and Group API Requests
* Title
* aggregationSchemeId
* householdSetId
* isMrio
* folderId
* LastImpactRunId
#### Endpoint
**GET {{api_domain}}api/v1/impact/project/Shared**


### Share Project with Users (Put)
Shares project with other users
#### Parameters
* array of email addresses (in body)
```
["EmailAddressOfUserToShareProjectWith", "EmailAddressOfUserToShareProjectWith", ...]
```
#### Response
* status code
#### Endpoint
**Put {{api_domain}}api/v1/impact/project/{{projectId}}/share**


### Transfer Project to User (Patch)
Transfers project ownership to another user
#### Parameters
* email address (in body)
```
{
    "Email": "EmailAddressOfUserToTransferProjectTo"
}
```
#### Response
* status code
#### Endpoint
**Patch {{api_domain}}api/v1/impact/project/{{projectId}}/transfer**


### Share Folder with Users (Put)
Shares folder with other users
#### Parameters
* array of email addresses (in body)
```
["EmailAddressOfUserToShareFolderWith", "EmailAddressOfUserToShareFolderWith", ...]
```
#### Response
* status code
#### Endpoint
**Put {{api_domain}}api/v1/impact/folder/{{folderId}}/share**


### Update Project (Put)
If you wish to edit the values of an existing project, you may do so with this endpoint.  We do not currently allow for aggregationSchemeId or householdSetId to be changed on a project, because any existing events or groups are specific to those values, and would be incompatible with other aggregationSchemeId’s or householdSetId’s.
#### Parameters
* Project Id (In URL)
* Title
* isMrio (Optional)
* folderId (Optional)
#### Response
* Id - This will be used on all subsequent Project, Event, and Group API Requests
* Title
* aggregationSchemeId
* householdSetId
* isMrio
* folderId
#### Endpoint
**PUT {{api_domain}}api/v1/impact/project/{{project id}}**


### Duplicate Project (Put)
You can duplicate a project using this endpoint.
#### Parameters
* Project Id (In URL)
#### Response
* Project Id
* Title
#### Endpoint
**POST {{api_domain}}api/v1/impact/project/{{project id}}/duplicate**


### Delete Project (DELETE)
Use this endpoint to delete a project.
#### Parameters
Project Id (In URL)
#### Response
A status code of 200 if the project has been successfully deleted.
#### Endpoint
**DELETE {{api_domain}}api/v1/impact/project/{{projectGUID}}**


### Get Event Types (Get)
This endpoint returns a list of valid event type options that can be used for the project.
#### Parameters
* Project Id (In Url)
#### Response
An array of event types (string) to use with Get Project Specification and Create Event endpoints. Options will be specific to the industry set used to create the project. Possible returns include:
* IndustryEmployment
* IndustryOutput
* IndustryEmployeeCompensation
* IndustryProprietorIncome
* IndustryContributionAnalysis
* CommodityOutput
* LaborIncome
* HouseholdIncome
* IndustrySpendingPattern
* InstitutionalSpendingPattern
* IndustryImpactAnalysis
* CustomIndustryImpactAnalysis
* InternationalIndustryImpactAnalysis
* CustomInternationalIndustryImpactAnalysis
#### Endpoint
**POST {{api_domain}}api/v1/impact/project/{{projectGUID}}/eventtype**


### Get Project Specification (Get)
Use this endpoint to get event type specifications, such as industry codes for industry change events and commodity codes for commodity output change events.
### Parameters
* Project Id (In URL)
* Event Type (In URL)
#### Response
A list of specifications data containing the following fields:
* Code
* Name
#### Endpoint
**GET {{api_domain}}api/v1/impact/project/{{projectGUID}}/eventtype/{{eventtype}}/specification**

---
# Spending Patterns
- There are three types of Spending Patterns: **Industry**, **Institution**, and **Custom**
- There are several endpoints that let you query for existing Spending Patterns as well as uploading new ones

## Spending Pattern Details and Commodities
- This endpoint returns the details and commodities for a given Spending Pattern

#### Request
- `GET {{api_domain}}api/v1/impact/spending-patterns/{{aggregationSchemeId}}/{{spendingPatternType}}/{{specificationCode}}`
	- `aggregationSchemeId` (number, required): Aggregation Scheme
	- `spendingPatternType` (text, required): `Industry`, `Institution`, or `Custom`
	- `specificationCode` (number, required): Specification Code
- `GET {{api_domain}}api/v1/impact/spending-patterns/{{aggregationSchemeId}}/{{spendingPatternType}}/{{specificationCode}}?datasetId={{datasetId}}&regionHashId={{regionHashId}}`
	- `datasetId` (number, optional): Data Set Id, defaults to the latest Data Year
	- `regionHashId` (text, optional): Region Hash Id
	- *Note*: For `Institutional Household Spending Patterns` the `RegionHashId` is *required* as it is the Region where the base Spending Pattern will be pulled from

#### Response
- Returns the details about the Spending Pattern as well as the Commodities defined for it
```json
{
    "id": null,
    "eventId": null,
    "isIntermediateExpenditure": true,
    "isSamValue": true,
    "payingCode": 3,
    "title": "",
    "spendingPatternType": 12,
    "templateType": "Industry",
    "spendingPatternCommodities": [
        {
            "coefficient": 0.0006737514200153713,
            "commodityCode": 3001,
            "effect": "Indirect",
            "id": null,
            "isSamValue": true,
            "localPurchasePercentage": 1.0,
            "commodityDescription": "Oilseeds",
            "userSpendingPatternId": null,
            "isNew": false
        },
        ...
        {
            "coefficient": 7.378499325444009E-05,
            "commodityCode": 3526,
            "effect": "Indirect",
            "id": null,
            "isSamValue": true,
            "localPurchasePercentage": 1.0,
            "commodityDescription": "US Postal delivery services",
            "userSpendingPatternId": null,
            "isNew": false
        }
    ]
}
```

---
# Create Event (Post)
- Adds an Event to an existing Project

### Endpoint
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/event`

##### Request
- The existing Project's `guid` Id must be passed in the URL
- A `json` body that defines the event must be included
```json
{
    "impactEventType": "IndustryOutput",
    "title" : "Custom_Event_Title",
    "output" : 100000.01,
    "employment" : 20.25,
    "employeeCompensation" : 50000.23,
    "proprietorIncome" : 3400.233,
    "tags": ["Testing"]
}
```
- `impactEventType` (text, required) - See `Get Event Types` above for a list of valid Event Types
- `title` (text, required) - A unique-per-project title for this Event
- `output` (number, optional except for `IndustryOutput` events) - The total output value for this Event
- `employment` (number, optional except for `IndustryEmployment` events) - The total number of people employed
- `employeeCompensation` (number, optional except for `IndustryEmployeeCompensation` events) - The total compensation paid to non-proprietor employees
- `proprietorIncome` (number, optional except for `IndustryProprietorIncome` events) - The total compensation paid to proprietors - Not applicable to International industry sets
- `tags` (array of text, optional): Additional tags to associate with this Event

###### Additional Request Parameters
- These should only be used if you are adding an Event that is marginable, such as a Retail or Wholesale Industry
- Percentage
- DataSetId
- MarginType (`PurchaserPrice`, `ProducerPrice`)

##### Industry Impact Analysis json
```json
{
    "impactEventType": "IndustryImpactAnalysis",
    "IndustryCode" : 1,
    "IntermediateInputs": 56,
    "TotalEmployment": 3,
    "EmployeeCompensation": 4,
    "ProprietorIncome": 5,
    "WageAndSalaryEmployment" : 1,
    "ProprietorEmployment" : 2,
    "TotalLaborIncome" : 9,
    "OtherPropertyIncome" : 34,
    "TaxOnProductionAndImports" : 23,
    "TotalOutput": null,
    "title": "IndustryImpactAnalysis_api",
    "LocalPurchasePercentage": 1,
    "IsSam": false,
    "SpendingPatternDatasetId": 87,
    "SpendingPatternValueType": "IntermediateExpenditure",
    "SpendingPatternCommodities": null,
    "Tags": [],
    "IsLocalEmployeeCompensation": false
}
```
##### International Industry Impact Analysis json
```json
{
    "impactEventType": "InternationalIndustryImpactAnalysis",
    "IndustryCode" : 5,
    "IntermediateInputs": 5000000,
    "TotalEmployment": 24,
    "EmployeeCompensation": 4000000,
    "WageAndSalaryEmployment" : 24,
    "TotalLaborIncome" : 4000000,
    "GrossOperationSurplus" : 500000,
    "OtherTaxOnProductionAndImports" : 500000,
    "TotalOutput": 10000000,
    "title": "InternationalIndustryImpactAnalysis_api",
    "LocalPurchasePercentage": 1,
    "IsSam": false,
    "SpendingPatternDatasetId": 95,
    "SpendingPatternRegionUrid": 1861222,
    "SpendingPatternValueType": "IntermediateExpenditure",
    "Tags": [],
    "SpendingPatternCommodities": [],
    "IsLocalEmployeeCompensation": false
}
```
###### Custom Industry Impact Analysis Json
```json
{
    "impactEventType": "CustomIndustryImpactAnalysis",
    "title": "CustomIndustryImpactAnalysis_API_Example",
    "SpendingPatternDatasetId": 96,
    "SpecificationCode" : 21059,
    "WageAndSalaryEmployment" : 10,
    "ProprietorEmployment" : 2,
    "TotalEmployment": 12,
    "EmployeeCompensation": 40000,
    "ProprietorIncome": 100000,
    "TotalLaborIncome" : 140000,
    "TaxOnProductionAndImports" : 2300,
    "OtherPropertyIncome" : 3400,
    "IntermediateInputs": 5600,    
    "TotalOutput": null,
    "LocalPurchasePercentage": 1,
    "IsSam": false,
    "SpendingPatternValueType": "IntermediateExpenditure",
    "SpendingPatternCommodities": null,
    "Tags": ["Testing"]
    "isLocalEmployeeCompensation": false
}
```

###### Custom International Industry Impact Analysis Json
```json
{
  "impactEventType": "CustomInternationalIndustryImpactAnalysis",
  "title": "CustomInternationalIndustryImpactAnalysis_API_Example",
  "SpendingPatternDatasetId": 95,
  "SpecificationCode" : 21089,
  "IntermediateInputs": 5000000,
  "TotalEmployment": 24,
  "EmployeeCompensation": 4000000,
  "WageAndSalaryEmployment" : 24,
  "TotalLaborIncome" : 4000000,
  "GrossOperationSurplus" : 500000,
  "OtherTaxOnProductionAndImports" : 500000,
  "TotalOutput": 10000000,
  "LocalPurchasePercentage": 1,
  "IsSam": false,
  "SpendingPatternValueType": "IntermediateExpenditure",
  "Tags": ["Testing"],
  "spendingPatternCommodities": null,
  "isLocalEmployeeCompensation": false
}
```

### Create Event - Requests (no Commodities)
- To use an existing Spending Pattern, simply submit an Event Create request without specifying the `SpendingPatternCommodities` (omit the property or set it to `null`)

#### Industry Spending Pattern
```json
{
    "ImpactEventType": "IndustrySpendingPattern",
    "Title" : "ImpactApi - Industry Spending Pattern Example",
    "Tags": ["Example"],
    "Output": 147000,
    "IndustryCode": 1,
    "LocalPurchasePercentage": 1.0,
    "IsSam": true,
    "SpendingPatternDatasetId": 96,
    "SpendingPatternValueType": "IntermediateExpenditure"
}
```

#### Institutional Spending Pattern (non-Household)
```json
{
    "impactEventType": "InstitutionalSpendingPattern",
    "title": "ImpactApi - Institutional Spending Pattern Example - Gov",
    "tags": ["Example"],
    "value": 30000,
    "institutionCode": 11002,
    "localPurchasePercentage": 1,
    "isSam": true,
    "spendingPatternDatasetId": 96
}
```

#### Institutional Spending Pattern (Household)
```json
{
    "impactEventType": "InstitutionalSpendingPattern",
    "title": "ImpactApi - Institutional Spending Pattern Example - Household",
    "tags": ["Example"],
    "value": 13000000,
    "institutionCode": 10007,
    "localPurchasePercentage": 1,
    "isSam": true,
    "spendingPatternDatasetId": 96,
    "SpendingPatternRegionUrid": 1819520
}
```

#### Custom Spending Pattern
```json
{
    "impactEventType": "CustomSpendingPattern",
    "title": "ImpactApi - Custom Spending Pattern Example",
    "tags": ["Testing"],
    "value": 75000,
    "specificationCode": 21059,
    "spendingPatternDatasetId": 96
}
```

### Create Event - Requests w/Commodities
- In order to specify your own commodity information, simply add an additional property to any of the above Spending Pattern Events in order to modify the commodities used for the Event
```json
"SpendingPatternCommodities": [
        {
            "coefficient": 0.0006157221001664674,
            "commodityCode": 3001,
            "effect": "Indirect",
            "isSamValue": true,
            "localPurchasePercentage": 1,
            "commodityDescription": "Oilseeds"
        },
        ...
        {
            "coefficient": 0.15,
            "commodityCode": 3003,
            "effect": "Indirect",
            "isSamValue": false,
            "localPurchasePercentage": 0.75,
            "commodityDescription": "Vegetables and melons"
        },
		...
        {
            "coefficient": 0.00006742998924789797,
            "commodityCode": 3526,
            "effect": "Indirect",
            "isSamValue": true,
            "localPurchasePercentage": 1,
            "commodityDescription": "US Postal delivery services"
        }
    ]
```


##### Response
- Regardless of the type of Event sent through this endpoint (and whether or not it had custom Commodities specified), the return response will be the fully-hydrated Event's json
- An example from a Industry Output event:
```json
{
    "output": 100000.01,
    "employment": 20.25,
    "employeeCompensation": 50000.23,
    "proprietorIncome": 3400.233,
    "industryCode": 0,
    "marginType": "ProducerPrice",
    "percentage": null,
    "datasetId": null,
    "id": "5339adf1-f1c9-4b59-982c-55945ec1ca72",
    "projectId": "3b7ad1e0-3d3c-11ef-aaf6-1266878a14f1",
    "impactEventType": "IndustryOutput",
    "title": "IndustryOutput_api",
    "tags": ["Example"],
    "spendingPatternCommodities": [
        {
            "coefficient": 0.0006157221001664674,
            "commodityCode": 3001,
            "commodityDescription": "Oilseeds",
            "isSamValue": true,
            "isUserCoefficient": false,
            "localPurchasePercentage": 1.0
        },
        ...
	]
}
```
- Any value passed in the original Request will be exactly the same in the Response
- `projectId` (guid) - This is the `guid` for the Project
- `id` (guid) - This is the `guid` for the Event


---
### Get Event (Get)
#### Parameters
* projectId (in URL)
* eventId (in URL)
#### Response
* Output
* Employment
* employeeCompensation
* proprietorIncome
* IndustryCode
* Id - this is the event id, and will be used for associating an event with a group
* projectId
* impactEventType
* title
#### Endpoint
**GET {{api_domain}}api/v1/impact/project/{{project id}}/event/{{event id}}**

---
## Update Events
- You can also update existing Events (including changing them entirely from one type to another)
- This endpoint supports all the same Impact Event Types as `Event Create` (above)
	- A list of these supported types can be acquired through `Get Event Types` (below)

---
##### Request
- `PUT {{api_domain}}api/v1/impact/project/{{projectGuid}}/event/{{eventGuid}}`
	- Along with the `api_domain`, `projectGuid`, and `eventGuid`, a `json` body must be included that defines the changes to the event.
	- This `json` body is exactly the same as for the `Event Create` endpoint (above)
	  - Also supports editing Spending Patterns by sending through a list of commodities (as above)
```json
{
    "impactEventType": "CustomSpendingPattern",
    "title": "ImpactApi - Example - CustomSpendingPattern - Updated",
    "value": 123000.78,
    "specificationCode": 21059,
    "spendingPatternDatasetId": 96,
    "tags": ["Updated"]
}
```

##### Response
- As with the `Event Create` endpoint, the response from `Event Update` is the fully-hydrated `json` representation of the Event after it has been updated


---
### Delete Event (Delete)
Use this endpoint to delete an event.
#### Parameters
* Project Id (In Url)
* Event Id (In Url)
#### Response
Status Code 200 if event successfully deleted.
#### Endpoint
**DELETE {{api_domain}}api/v1/impact/project/{{projectGUID}}/event/{{eventGUID}}**


### Import Events (POST)
Use this endpoint along with the [Event Template](https://support.implan.com/hc/en-us/articles/360040713754-Using-the-Event-Template) to import events created in an excel file.
#### Parameters
Project Id (In URL)
#### Response
A status code of 200 if the event or events were successfully created.
#### Endpoint
**POST {{api_domain}}api/v1/impact/project/import/{{projectGUID}}**


### Create Group (Post)
#### Parameters
* Id (Optional)
* ProjectId (In URL)
* Title
* HashId or URID (required)
* Dollar Year
* DatasetId
* ScalingFactor (Optional - defaults to 1)
* GroupEvents (Optional)
#### Response
* id
* projectId
* hashId
* urid
* userModelId
* modelId
* title
* dollarYear
* scalingFactor
* dataSetId
* groupEvents
#### Endpoint
**POST {{api_domain}}api/v1/impact/project/{{project_guid}}/group**


### Get Group (Get)
#### Parameters
* Project ID (In Url)
#### Response
* id
* projectId
* hashId
* urid
* userModelId
* modelId
* title
* dollarYear
* scalingFactor
* dataSetId
* groupEvents
#### Endpoint
**GET {{api_domain}}api/v1/impact/project/{{project id}}/group/**


### Update Group (Put)
#### Parameters
* Id - Group ID (In URL)
* ProjectId (In Url)
* Title
* HashId or URID (required)
* Dollar Year
* DatasetId
* ScalingFactor (Optional - defaults to 1)
* GroupEvents (Optional)
#### Response
* id
* projectId
* hashId
* urid
* userModelId
* modelId
* title
* dollarYear
* scalingFactor
* dataSetId
* groupEvents
#### Endpoint
**PUT {{api_domain}}api/v1/impact/project/{{project id}}/group/{{group id}}**


### Delete Group (DELETE)
Use this endpoint to delete a group.
#### Parameters
* Project Id (In Url)
* Group Id (In Url)
#### Response
Status Code 200 if group was successfully deleted
#### Endpoint
**DELETE {{api_domain}}api/v1/impact/project/{{projectGUID}}/group/{{groupGUID}}**


## Run Impact (Post)
#### Parameters
* Project Id (in Url)
#### Response
* Run Id 
#### Endpoint
**PUT {{api_domain}}api/v1/impact/{{project id}}**


## Cancel Impact Run (Put)
#### Parameters
* Run Id
#### Response
* Confirmation
#### Endpoint
**PUT {{api_domain}}api/v1/impact/cancel/{{runId}}**


## Run Status (Get)
To provide an asynchronous environment, IMPLAN has developed an endpoint that you can poll for status updates. It is recommended to poll at an interval of 30 seconds to check for status. 
#### Parameters:
* Bearer Token
* Run Id (in URL)
#### Response
* Status code
#### Endpoint
**GET {{api_domain}}api/v1/impact/status/{{runId}}**
* Will return “Unknown”,  “New”,  “InProgress”,  “ReadyForWarehouse” , “Complete”, “Error”


# Results
After running an impact, you have these different options to get results.

## Dollar Years (GET)
This endpoint provides a list of possible dollar year deflators that can be applied to the results in many of the endpoints that follow.
#### Parameters
* Aggregation Scheme Id
* Dataset Id
#### Response
* Array of valid dollar years for the given aggregation scheme and dataset combo
#### Endpoint
**GET {{api_domain}}api/v1/dollar-years/{{aggregationSchemeId}}/{{datasetId}}**

# Deflators
## Get Deflators
- This endpoint retrieves a list of Deflators

### Parameters
- `Bearer Token`
- `aggregationSchemeId` (required)
- `dataSetId` (required)
- `deflatorType` (required)
  - Valid deflator types are:
    - **1** - Industry
    - **2** - Commodity
    - **4** - Other Institution
    - **7** - Household
    - **8** - Trade Institution
    - **9** - Value Added Factor
### Response
- A `json` array of deflator information, broken down into `dollar_year`, `code`, `value`, and `description` for all deflators matching the **Parameters**
```json
[
    {
        "dollar_year": 1997,
        "code": 1,
        "value": 0.598,
        "description": "Oilseed farming"
    },
    ...
    {
        "dollar_year": 2060,
        "code": 546,
        "value": 1.098,
        "description": "* Employment and payroll of federal govt, non-military"
    }
]
```
### Endpoint
- `GET {{api_domain}}api/v1/deflators/:aggregationSchemeId/:dataSetId/:deflatorType`


---
## Result Totals
- To provide an asynchronous environment, IMPLAN has developed an endpoint that you can call to return the final results when the analysis run has been completed.
#### Parameters
* Bearer Token
* User Email Address
* Analysis Run Id (Obtained from Impact Analysis Endpoint)
* Dollar Year (Optional) - Overrides the Dollar Year only for Results
#### Response
The API response when the impact analysis is complete will provide Direct, Indirect, and Induced estimates for the following outputs:
* Total Output
* Total Employment
* Total Wage and Salary Employment
* Total Proprietor Employment
* Total Labor Income
* Total Employee Compensation
* Total Proprietor Income
* Total Other Property Income
* Total Taxes on Production and Imports
* Total Federal Taxes
* Total State Taxes
* Total County Taxes
* Total Sub-County General Taxes
* Total Sub-County Special District Taxes
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/{{runId}}**
**GET {{api_domain}}api/v1/impact/results/{{runId}}?dollarYear=2020**

Call after Status API request returns “Complete”

Will return.
```
[{
	"runId": 5923,
	"regionName": "group 1",
	"dataYear": "2019",
	"impactType": "Direct",
	"impactTypeId": 1,
	"output": 24.0,
	"employment": 4.0,
	"wagesalaryemployment": 2.4822851604905343,
	"proprietoremployment": 1.5177148395094657,
	"laborIncome": 7.0,
	"employeeCompensation": 2.0,
	"proprietorIncome": 5.0,
	"otherPropertyTypeIncome": 0.0,
	"taxOnProductionAndImports": 8.0,
	"subCountyGeneralTaxes": 1.101089247979291,
	"subCountySpecialDistrictsTaxes": 0.028253130986610593,
	"countyTaxes": 2.5595949962726197,
	"stateTaxes": 3.8802588214347797,
	"federalTaxes": 1.7467052842402941,
	"totalTaxes": 9.315901480913599
}, {
	"runId": 5923,
	"regionName": "group 1",
	"dataYear": "2019",
	"impactType": "Indirect",
	"impactTypeId": 2,
	"output": 9.699506942871064,
	"employment": 7.400741336145475E-05,
	"wagesalaryemployment": 4.8929139183874765E-05,
	"proprietoremployment": 2.5078274177579972E-05,
	"laborIncome": 3.1328411658052837,
	"employeeCompensation": 2.639137394626877,
	"proprietorIncome": 0.49370377117840725,
	"otherPropertyTypeIncome": 1.5189950934401746,
	"taxOnProductionAndImports": 0.328375904808993,
	"subCountyGeneralTaxes": 0.0459388732807516,
	"subCountySpecialDistrictsTaxes": 0.0011637874191108516,
	"countyTaxes": 0.10656839299602032,
	"stateTaxes": 0.24216331544802466,
	"federalTaxes": 0.6572300301071354,
	"totalTaxes": 1.053064399251043
}, {
	"runId": 5923,
	"regionName": "group 1",
	"dataYear": "2019",
	"impactType": "Induced",
	"impactTypeId": 3,
	"output": 8.249318632893182,
	"employment": 5.4272050051040594E-05,
	"wagesalaryemployment": 4.1573718824725244E-05,
	"proprietoremployment": 1.2698331226315353E-05,
	"laborIncome": 2.535111474066722,
	"employeeCompensation": 2.2261088294006215,
	"proprietorIncome": 0.30900264466610067,
	"otherPropertyTypeIncome": 1.8113055734548382,
	"taxOnProductionAndImports": 0.39273146899403416,
	"subCountyGeneralTaxes": 0.05462384320448541,
	"subCountySpecialDistrictsTaxes": 0.0013901409115902555,
	"countyTaxes": 0.12680935896957896,
	"stateTaxes": 0.2560977675589298,
	"federalTaxes": 0.5652103372346008,
	"totalTaxes": 1.0041314478791852
}]
```

## Detail Economic Indicators Export (Get)
This endpoint will provide Detailed Economic Indicators from an Impact Analysis
#### Parameters
* Bearer Token
* Analysis Run Id 
* Optional Filter Parameters
  * Filter Types
    * Year (dollar year)
    * Regions
    * Groups
    * Events
    * EventTags
#### Response
The API response when the analysis is complete will provide a CSV response with following fields:
* OriginRegion
* DestinationRegion
* EventName
* IndustryCode
* IndustryDescription
* ImpactType
* Output
* Employment
* WageAndSalaryEmployment
* ProprietorEmployment
* EmployeeCompensation
* ProprietorIncome
* TaxesOnProductionAndImports
* OtherPropertyIncome
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/ExportDetailEconomicIndicators/{{runId}}**
#### Example with Filters
**GET {{api_domain}}api/v1/impact/results/ExportDetailEconomicIndicators/{{runId}}?year=2023&impacts=Indirect**


## Detail Taxes Export (Get)
This endpoint will provide Detailed Tax Results from an Impact Analysis
#### Parameters
* Bearer Token
* Analysis Run Id 
* Optional Filter Parameters
  * Filter Types
    * Year (dollar year)
    * Regions
    * Groups
    * Events
    * EventTags
#### Response
The API response when the analysis is complete will provide a CSV response with following fields:
* GroupName
* EventName
* ModelName
* TaxSplitDescription
* ImpactType
* TransferCode
* TransferDescription
* PayingTypeCode
* PayingTypeDescription
* Value
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/DetailedTaxes/{{runId}}**
#### Example with Filters
**GET {{api_domain}}api/v1/impact/results/DetailedTaxes/{{runId}}?year=2023&impacts=Indirect**


## Summary Economic Indicators Export  (Get)
This endpoint will provide Summary Economic Indicators from an Impact Analysis
#### Parameters
* Bearer Token
* Analysis Run Id
* Optional Filter Parameters
  * Filter Types
    * Year (dollar year)
    * Regions
    * Groups
    * Events
    * EventTags
#### Response
The API response when the analysis is complete will provide a CSV response with following fields:
* GroupName
* EventName
* ModelName
* Impact
* Employment
* LaborIncome
* ValueAdded
* Output
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/SummaryEconomicIndicators/{{runId}}**
#### Example with Filters
GET {{api_domain}}api/v1/impact/results/SummaryEconomicIndicators/{{runId}}?year=2023&impacts=Indirect

---

## Summary Taxes Export
- This endpoint will provide Summary Tax Results from an Impact Analysis, and works with US, Canadian, and International projects.

#### Request
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/{{runId}}`
    - This endpoint is used for US regions
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/can/{{runId}}`
    - This endpoint is used for Canadian regions
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/intl/{{runId}}`
    - This endpoint is used for International regions
- `RunId` is the last successful Run Id from running the Impacts for a Project
- Optional filters can be included in the path with `?{{name}}={{value}}` and `&{{name}}={{value}}` as usual:
    - `year` (number): The dollar year for the Report
    - `regions` (list of strings): Filter for which Regions to include in the Report
    - `impacts` (list of Impact Type) [`Direct`, `Indirect`, `Induced`]
    - `groups` (list of string): Which Groups to include
    - `events` (list of string): Which Events to include
    - `eventTags` (list of string): A filter for events to only include ones that have any of the specified Tags

#### Response
- The API response when the analysis is complete will provide a CSV File response
- For US projects, the CSV will include the following columns:
    - GroupName
    - EventName
    - ModelName
    - Impact
    - SubCountyGeneral
    - SubCountySpecialDistricts
    - County
    - State
    - Federal
    - Total
- For Canadian projects, the CSV will include the following columns:
    - GroupName
    - EventName
    - ModelName
    - Impact
    - Federal
    - ProvincialAndTerritorial
    - Local
    - Indigenous
    - CanadaPensionPlan
    - QuebecPensionPlan
    - GeneralGovernmentsTotal 
      - The General Governments Total is a summation of all the other listed sub tax category impacts, therefore the other tax values should never be added to the General Governments Total values. Results are not available in the sub tax categories for impacts run with Data Years 2020 and older.
- For International projects, the CSV will include these columns:
    - GroupName
    - EventName
    - ModelName
    - Impact
    - Total
---


## Estimated Growth Percentage
This endpoint will provide estimated industry growth percentage data from an Impact Analysis.
#### Parameters
* Bearer Token
* Analysis Run Id
* Dollar Year (in body)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/EstimatedGrowthPercentage/{{runId}}**


## Impact Occupation (Get)
This endpoint will provide occupation results from an impact analysis.
#### Parameters
* Bearer Token
* Analysis Run Id 
* Occupation Aggregation Level (in body)
* Occupation Data Year (in body)
* Dollar Year (in body)
* Industry Code (in body)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
#### Response
The API response when the analysis is complete will provide a CSV response with following fields:
* Occupation Code
* Occupation
* Wage and Salary Employment
* Wage and Salary Income
* Supplements to Wages and Salaries
* Employee Compensation
* Hours Worked
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/ImpactOccupation/{{runId}}**


## Impact Occupation Averages (Get)
This endpoint will provide occupation results averages from an impact analysis.
#### Parameters
* Bearer Token
* Analysis Run Id 
* Occupation Aggregation Level (in body)
* Occupation Data Year (in body)
* Dollar Year (in body)
* Industry Code (in body)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
#### Response
The API response when the analysis is complete will provide a CSV response with following fields:
* Occupation Code
* Occupation
* Average Wage and Salary Income
* Average Supplements to Wages and Salaries
* Average Employee Compensation
* Average Hours per Year
* Average Wage and Salary Income per Hour
* Average Supplements to Wages and Salaries per Hour
* Average Employee Compensation per Hour
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/ImpactOccupationAverages/{{runId}}**


## Impact Occupation Core Competencies (Get)
This endpoint will provide occupation core competencies results from an impact analysis.
#### Parameters
* Bearer Token
* Analysis Run Id 
* Occupation Aggregation Level (in body)
* Occupation Data Year (in body)
* Industry Code (in body)
* Occupation Code (in body)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
#### Response
The API response when the analysis is complete will provide a zip file with a collection of CSV files with different core competency results data.
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/ImpactOccupationCoreCompetencies/{{runId}}**


## Environment Impact Industry Summary (Get)
This endpoint will provide environment category impact results by industry from an impact analysis.
#### Parameters
* Bearer Token
* Analysis Run Id
* Dollar Year (in body)
* Environment Release String (in body)
* Environment Name (in body; *optional)
* Environment Categories (in body; *optional)
* Industry Code (in body; *optional)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
* NaicsAggregationSchemeId (in body; *optional; only works with impacts run using the default U.S. Data aggregation scheme)
#### Response
The API response when the analysis is complete will provide a CSV file with environment category impact data by industry.
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/EnvironmentIndustrySummary/{{runId}}**


## Environment Impact Industry Details (Get)
This endpoint will provide detailed environment name environmental output impact results from an impact analysis.
#### Parameters
* Bearer Token
* Analysis Run Id
* Dollar Year (in body)
* Environment Release String (in body)
* Environment Name (in body; *optional)
* Environment Categories (in body; *optional)
* Industry Code (in body; *optional)
* Regions (in body; *optional)
* Impacts (in body; *optional)
* Group Names (in body; *optional)
* Event Names (in body; *optional)
* Event Tags (in body; *optional)
* NaicsAggregationSchemeId (in body; *optional; only works with impacts run using the default U.S. Data aggregation scheme)
#### Response
The API response when the analysis is complete will provide a CSV file with detailed environment impact data. There is a 5000 row limit to the amount of data returned.
#### Endpoint
**GET {{api_domain}}api/v1/impact/results/EnvironmentImpactIndustryDetails/{{runId}}**


# Folders
These endpoints allow for the creation and management of folders for organizing projects. The folder id associated with a created folders can be used as part of the Project Post and Put endpoints to assign projects to folders.

## Create Folder (Post)
This endpoint will create a new folder. Include a parent id value in the body to create a folder inside of a previously created folder.
#### Parameters
* Title (in body; required)
* ParentId (int body; optional)
#### Response
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**POST {{api_domain}}api/v1/impact/folder**


## Get Folders (Get)
This endpoint returns all folders created by the user.
#### Parameters
none
#### Response
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/folder**


## Get Folder (Get)
This endpoint returns details for a specific folder.
#### Parameters
* Id (In Url)
#### Response
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/folder/{{folderId}}**


## Get Folder's Folders (Get)
This endpoint returns a list of folders assigned to a specific folder.
#### Parameters
* Id (In Url)
#### Response
An array of objects, each containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/folder/{{folderId}}/folders**


## Get Folder's Projects (Get)
This endpoint returns a list of projects assigned to a specific folder.
#### Parameters
* Id (In Url)
#### Response
An array of objects, each containing the following properties:
* Id
* Title
* AggregationSchemeId
* HouseholdSetId
* IsMrio
* FolderId
* LastImpactRunId
#### Endpoint
**GET {{api_domain}}api/v1/impact/folder/{{folderId}}/projects**


## Update Folder (Put)
This endpoint updates a specific folder. Use this endpoint to update a folder's title or assign a parent folder id.
#### Parameters
* Id (In Url)
* Id (In Body; Required, must match Id in Url)
* Title (Required but can match current title)
* ParentId (Optional; cannot equal id)
#### Response
An array of objects, each containing the following properties:
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**PUT {{api_domain}}api/v1/impact/folder/{{folderId}}**


## Delete Folder (Delete)
Use this endpoint to delete a folder. Note, if the directory contains projects, the projectHandlingType parameter must be passed with one of two possible values (Delete or MoveToRoot).
#### Parameters
* Id (In Url)
* projectHandlingType (required if folder directory contains projects. Pass either "Delete" or "MoveToRoot")
#### Response
Status Code 200 if folder was successfully deleted
#### Endpoint
**DELETE {{api_domain}}api/v1/impact/folder/{{folderId}}**

**DELETE {{api_domain}}api/v1/impact/folder/:folderId?projectHandlingType=Delete**

**DELETE {{api_domain}}api/v1/impact/folder/:folderId?projectHandlingType=MoveToRoot**


## Shared Folders 
The following endpoints allow the user to review folders that have been shared with them.
## Get Shared Folders (Get)
This endpoint returns all folders shared with the user.
#### Parameters
none
#### Response
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/shared-folders**


## Get Shared Folder (Get)
This endpoint returns details for a specific folder.
#### Parameters
* Id (In Url)
#### Response
An object containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/shared-folders/{{folderId}}**


## Get Shared Folder's Folders (Get)
This endpoint returns a list of folders assigned to a specific folder.
#### Parameters
* Id (In Url)
#### Response
An array of objects, each containing the following properties:
* Id
* Title
* Created (date)
* OwnerId
* ParentId
#### Endpoint
**GET {{api_domain}}api/v1/impact/shared-folders/{{folderId}}/folders**


## Get Shared Folder's Projects (Get)
This endpoint returns a list of projects assigned to a specific folder.
#### Parameters
* Id (In Url)
#### Response
An array of objects, each containing the following properties:
* Id
* Title
* AggregationSchemeId
* HouseholdSetId
* IsMrio
* FolderId
* LastImpactRunId
#### Endpoint
**GET {{api_domain}}api/v1/impact/shared-folders/{{folderId}}/projects**


# Appendix

## Code Examples

### Authentication - Getting the Bearer Token - for non-SSO, non-M2M customers:

#### C# example
```
var options = new RestClientOptions("{{api_domain}}")
{
  MaxTimeout = -1,
};
var client = new RestClient(options);
var request = new RestRequest("/{{env}}/auth", Method.Post);
request.AddHeader("Content-Type", "text/plain");
var body = @"{  ""username"": """",   ""password"": """" }
" + "\n" +
@"";
request.AddParameter("text/plain", body,  ParameterType.RequestBody);
RestResponse response = await client.ExecuteAsync(request);
Console.WriteLine(response.Content);
```

#### Java Example
```
Unirest.setTimeouts(0, 0);
HttpResponse<String> response = Unirest.post("{{api_domain}}{{env}}/auth")
  .header("Content-Type", "text/plain")
  .body("{  \"username\": \"\",   \"password\": \"\" }\r\n")
  .asString();
```

#### Node Example
```
var request = require('request');
var options = {
  'method': 'POST',
  'url': '{{api_domain}}{{env}}/auth',
  'headers': {
    'Content-Type': 'text/plain'
  },
  body: '{  "username": "",   "password": "" }\r\n'

};
request(options, function (error, response) {
  if (error) throw new Error(error);
  console.log(response.body);
});
```

####  Python Example
```
import http.client

conn = http.client.HTTPSConnection("{{api_domain}}")
payload = "{  \"username\": \"\",   \"password\": \"\" }\r\n"
headers = {
  'Content-Type': 'text/plain'
}
conn.request("POST", "/{{env}}/auth", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

#### R Example
```
library(RCurl)
headers = c(
  "Content-Type" = "text/plain"
)
params = "{  \"username\": \"\",   \"password\": \"\" }\r\n"
res <- postForm("{{api_domain}}{{env}}/auth", .opts=list(postfields = params, httpheader = headers, followlocation = TRUE), style = "httppost")
cat(res)
```