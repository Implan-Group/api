# Overview

This document is intended to provide a developer guide for the API that IMPLAN has developed for creating economic models and  generating impacts via API.  This API is intended to eventually replicate the functionality of IMPLAN Cloud, allowing you to embed IMPLAN into your applications and workflows.  

This document assumes a working knowledge of the IMPLAN Cloud and its workflow, which can be found on [support.implan.com](https://support.implan.com/hc/en-us/categories/360002245673-IMPLAN-Basics).  


## Getting Started

To help you get started running economic impact analysis, this section will provide a quick overview of the implan workflow after you’ve completed the [Authentication](#authentication---retrieving-bearer-access-token).


### Find a region and industry to study

In order to run an economic impact analysis, you will first need to identify the [Data Year (Dataset)](#dataset-endpoint-get) on when the impact will take place, the [Industry](#industry-codes-endpoint-get) that will change, and the [Region](#region-model-endpoint-get) where the impact will take place. 


### Create a project, define groups and events

After determining your Region(s), Datasets, and Industries, you can create a [Project](#create-project-post), add [Events](#create-event-post) to the project, and add [Groups](create-group-post) to the project with associated Events.


### Run an Impact on your project

Once your project has been defined, you can [Run an Impact](#run-impact-post) on your project.  Depending on the size of your project based on the number of events and groups, your project may take a few seconds or a few minutes to complete.  While waiting, you can poll for the [status](#run-status-get) of your project’s impact run. We recommend a polling frequency of 30 seconds. 


### Export Results of the Impact

Once your project’s impact run has completed, you may export the [Results](#results) based on the impact run id.  


## Glossary

You can find a detailed [Glossary](https://support.implan.com/hc/en-us/categories/1500000107962-Glossary) of economic terms on [support.implan.com](https://support.implan.com/hc/en-us/categories/1500000107962-Glossary), including [Events and Groups](https://support.implan.com/hc/en-us/sections/360011253094-E-H), but in this section you will find terms unique to the API.  


### URID

URID stands for Universal Region Identifier, and refers to a unique identifying number specific to a single implan region, such as a country, state, metropolitan statistical area (MSA), county, congressional district, or zip code.


### HashID


### AggregationSchemeId 


### HouseholdSetId


## Postman Collection

We have created a Postman collection with reference calls per section in this document to help with implementation.  IMPLAN will provide credentials in a separate correspondence.  The latest Postman Collection is available for download below at:

[https://github.com/Implan-Group/api/blob/main/Implan-API.postman_collection.json](https://github.com/Implan-Group/api/blob/main/Implan-API.postman_collection.json) 


## Development Variables

The following variables can be used while developing against the IMPLAN API. Following development, please transition to Production Variables below.


<table>
  <tr>
   <td>Item
   </td>
   <td>Reference Value
   </td>
   <td>Development Value
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
   <td>Environment
   </td>
   <td>{{env}}
   </td>
   <td>beta/
   </td>
  </tr>
  <tr>
   <td>User Email
   </td>
   <td>{{email}}
   </td>
   <td>Same as beta-app.implan.com
   </td>
  </tr>
  <tr>
   <td>User Password
   </td>
   <td>{{password}}
   </td>
   <td>Same as beta-app.implan.com
   </td>
  </tr>
</table>



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
   <td>Environment
   </td>
   <td>{{env}}
   </td>
   <td>n/a - leave blank
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



# Authentication - Retrieving Bearer access token


## General Authentication Architecture

It’s recommended that you implement a backend solution to communicate with the IMPLAN API.  You will need to include a bearer token when sending requests to the IMPLAN API.  This bearer token will be valid for 24 hours and it is expected that you will cache this token while it’s valid. 


## Token Caching

The “access_token” is good for 24 hours.  It is required that you cache this token and use the token to make additional requests to the IMPLAN API.  Requesting excessive tokens  (eg. Getting a new token for every request) is not necessary and is not supported, and may incur additional cost or temporary disabling of your account if you exceed 1000 tokens per month.  Requesting additional tokens is supported for use cases such as system reboots.  Excessive access_token requests are not supported.


## Examples

Some code examples for obtaining the authentication token are provided in the [Appendix](#appendix).

## Endpoint
**POST https://{{api_domain}}/auth**

## Expected Response

The expected response will be in this format:

![alt_text](/images/auth_response.png "auth response")

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

**GET https://{{api_domain}}/api/v1/datasets**


## Region Model Endpoint (Get)

Since region model id’s and underlying data can change each year, you will need to provide a Data Set ID as an input.  The Endpoint response will include a list of Region Names, Types, and Model ID’s.   The response may be cached.

The Regions that will be accessible by this API endpoint will include the regions purchased in their data subscription.


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

Take a dataset id from the dataset API request and use it for the model’s API request

**GET https://{{api_domain}}/api/v1/models?datasetId=77 **


## Industry Codes Endpoint (Get)

**Use with project analysis endpoints.  **The Industries supported by this API will be the current standard IMPLAN 546 Industry scheme. This response may be cached.  A list of those industries can be found here: [https://support.implan.com/hc/en-us/articles/360034896614-546-Industries-Conversions-Bridges-Construction-2018-Data](https://support.implan.com/hc/en-us/articles/360034896614-546-Industries-Conversions-Bridges-Construction-2018-Data)

In 2022, the BEA will redefine the North American Industry Classifications System (NAICS) codes. This change will result in a change to the IMPLAN industry scheme for the 2023 IMPLAN data release. The API will then be updated to include these new industry designations when that data is added to the system.


#### Parameters



* Bearer Token


#### Response (List)



* Industry Id 
* Industry Codes
* Industry Description

Will return Industries
```
[

    {

        "id": 4638,

        "code": 1,

        "description": "Oilseed farming"

    },

    {

        "id": 4639,

        "code": 2,

        "description": "Grain farming"

    }

]
```

#### Endpoint

**GET https://{{api_domain}}/api/v1/IndustryCodes**


# Regions


## Getting Regional Data

If you need to download study area data or obtain regional information to build regions, these endpoints will be helpful.


### Top Level Region (Get)

This endpoint will return the top most region for an aggregation scheme and  dataset.  You may use the [URID](#urid) of this in Get Region Children by Urid.  


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)


#### Endpoint

**GET https://{{api_domain}}/api/v1/region/{aggregationSchemeId}/{dataSetId}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Top Level Region Children (Get)

This endpoint will return all children regions for the top most region returned from Get Top Level Region, along with the same data points.  


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)


#### Endpoint

**GET https://{{api_domain}}/api/v1/region/{aggregationSchemeId}/{dataSetId}/children**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### User Custom and Combined Regions (Get)

This endpoint will return all combined and custom regions that a user created by aggregation scheme and data set. 


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)


#### Endpoint

**GET https://{{api_domain}}/api/v1/region/{aggregationSchemeId}/{dataSetId}/user**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Get Regions by Urid (Get)

This endpoint allows a user to pull high level region information by a specific urid, within an aggregation scheme and data set.  


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)
* URID (in URL)


#### Endpoint

**GET https://{{api_domain}}/api/v1/region/{aggregationSchemeId}/{dataSetId}/{urid}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Get Regions Children by Urid (Get)

This endpoint allows a user to pull high level region information for all children regions directly under a specific urid, within an aggregation scheme and data set.  It will only pull direct children descendants, so if a country urid is provided, this will return states. If a state is provided, it will return Counties, MSA’s, and Congressional Districts.  


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Data Set ID (in URL)
* URID (in URL)


#### Endpoint

**GET https://{{api_domain}}/api/v1/region/{aggregationSchemeId}/{dataSetId}/{urid}/children**

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

**POST https://{{api_domain}}/api/v1/region/build/batch/{aggregationSchemeId}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


### Build Combined Region - Batch (POST)

This endpoint will allow a user to build multiple combined regions  by providing the urids to combine and an aggregation scheme.  Specify the aggregation scheme id in the url, and the list of urids separated by a comma in the body.


#### Parameters



* Bearer Token
* Aggregation Scheme ID (in URL)
* Description (in body)
* URID (in body)
* Optional - Type of Request Body (CSV/JSON)
    1. If you would prefer to upload your URID’s in a CSV format, you may do so by specifying CSV for the {type} parameter


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

**POST https://{{api_domain}}/api/v1/region/build/batch/combined/{aggregationSchemeId}/{type}**

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

**POST https://{{api_domain}}/api/v1/region/build/combined/{aggregationSchemeId}**

**Note:** the default Aggregation Scheme ID is 8 for Unaggregated 546 Industries


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

**POST https://{{api_domain}}/api/v1/impact/project**


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

**GET https://{{api_domain}}/api/v1/impact/project/{{project id}}**


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

**PUT https://{{api_domain}}/api/v1/impact/project/{{project id}}**


### Create Event (Post)


#### Parameters



* Project Id (In URL)
* ImpactEventType
    * IndustryEmployment
    * IndustryOutput
    * IndustryEmployeeCompensation
    * IndustryProprietorIncome 
* Title
* industryCode
* Output (Optional, unless event type is IndustryOutput)
* Employment (Optional, unless event type is IndustryEmployment)
* EmployeeCompensation (Optional, unless event type is IndustryEmployeeCompensation)
* ProprietorIncome (Optional, unless event type is IndustryProprietorIncome)


#### Parameters for a Marginable Event

These should only be used if you are adding an event that is marginable, such as a retail or wholesale industry.  



* Percentage
* DataSetId
* MarginType (PurchaserPrice, ProducerPrice)


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

**POST https://{{api_domain}}/api/v1/impact/project/{{project id}}/event**


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

**GET https://{{api_domain}}/api/v1/impact/project/{{project id}}/event/{{event id}}**


### Update Event (Put)


#### Parameters



* Project Id (In URL)
* Event Id (In URL)
* ImpactEventType
    * IndustryEmployment
    * IndustryOutput
    * IndustryEmployeeCompensation
    * IndustryProprietorIncome 
* Title
* industryCode
* Output (Optional, unless event type is IndustryOutput)
* Employment (Optional, unless event type is IndustryEmployment)
* EmployeeCompensation (Optional, unless event type is IndustryEmployeeCompensation)
* ProprietorIncome (Optional, unless event type is IndustryProprietorIncome)


#### Parameters for a Marginable Event

These should only be used if you are adding an event that is marginable, such as a retail or wholesale industry.  



* Percentage
* DataSetId
* MarginType (PurchaserPrice, ProducerPrice)



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

**PUT https://{{api_domain}}/api/v1/impact/project/{{project id}}/event/{{event id}}**


### Create Group (Post)

#### Parameters

* Id (Optional)
* ProjectId (In URL)
* Title
* HashId (Optional*)
* URID (Optional* )
* Dollar Year
* DatasetId
* ScalingFactor (Optional - defaults to 1)
* GroupEvents (Optional)

*NOTE: HashId or URID must be supplied, but both are not required.

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
**POST https://{{Domain}}/v1/impact/project/{{project_guid}}/group**

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
**GET https://{{Domain}}/v1/impact/project/{{project id}}/group/**

### Update Group (Put)

#### Parameters

* Id - Group ID (In URL)
* ProjectId (In Url)
* Title
* HashId (Optional*)
* URID (Optional* )
* Dollar Year
* DatasetId
* ScalingFactor (Optional - defaults to 1)
* GroupEvents (Optional)

*NOTE: HashId or URID must be supplied, but both are not required.

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
**PUT https://{{Domain}}/v1/impact/project/{{project id}}/group/{{group id}}**

## Run Impact (Post)


#### Parameters

* Project Id (in Url)


#### Response

* Run Id 


#### Endpoint
**PUT https://{{Domain}}/v1/impact/{{project id}}**

## Run Status (Get)

To provide an asynchronous environment, IMPLAN has developed an endpoint that you can poll for status updates. It is recommended to poll at an interval of 30 seconds to check for status. 


#### Parameters:

* Bearer Token
* Run Id (in URL)


#### Response
* Status code

#### Endpoint

**GET https://{{api_domain}}/api/v1/impact/status/{runId}**


* Will return “Unknown”,  “New”,  “InProgress”,  “ReadyForWarehouse” , “Complete”, “Error”


# Results

After running an impact, you have these different options to get results.


## Results Totals (GET)

To provide an asynchronous environment, IMPLAN has developed an endpoint that you can call to return the final results when the analysis run has been completed.  


#### Parameters



* Bearer Token
* User Email Address
* Analysis Run Id (Obtained from Impact Analysis Endpoint)


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

**GET https://{{api_domain}}/api/v1/impact/results/{runId}**

Call after Status API request returns “Complete”

Will return.
```

        [


            {


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


            },


            {


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


            },


            {


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


            }


        ]
```

## Detail Economic Indicators Export (Get)

This endpoint will provide Detailed Economic Indicators from an Impact Analysis 


#### Parameters



* Bearer Token
* Analysis Run Id 


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

**GET https://{{api_domain}}/api/v1/impact/results/ExportDetailEconomicIndicators/{runId}**


## Detail Taxes Export (Get)

This endpoint will provide Detailed Tax Results from an Impact Analysis 


#### Parameters



* Bearer Token
* Analysis Run Id 


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

**GET https://{{api_domain}}/api/v1/impact/results/DetailedTaxes/{runId}**


## Summary Economic Indicators Export  (Get)

This endpoint will provide Summary Economic Indicators from an Impact Analysis 


#### Parameters



* Bearer Token
* Analysis Run Id 


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

**GET https://{{api_domain}}/api/v1/impact/results/SummaryEconomicIndicators/{runId}**


## Summary Taxes Export (Get)

This endpoint will provide Summary Tax Results from an Impact Analysis 


#### Parameters



* Bearer Token
* Analysis Run Id 


#### Response

The API response when the analysis is complete will provide a CSV response with following fields:



* GroupName
* EventName
* ModelName
* Impact
* SubCountyGeneral
* SubCountySpecialDistricts
* County
* State
* Federal
* Total


#### Endpoint

**GET https://{{api_domain}}/api/v1/impact/results/SummaryTaxes/{runId}**


# Appendix


## Code Examples to retrieve tokens


### C# example
```
var options = new RestClientOptions("https://{{api_domain}}")
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

### Java Example
```
Unirest.setTimeouts(0, 0);
HttpResponse<String> response = Unirest.post("https://{{api_domain}}/{{env}}/auth")
  .header("Content-Type", "text/plain")
  .body("{  \"username\": \"\",   \"password\": \"\" }\r\n")
  .asString();
```

### Node Example
```
var request = require('request');
var options = {
  'method': 'POST',
  'url': 'https://{{api_domain}}/{{env}}/auth',
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

###  Python Example
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
	
### R Example
```
library(RCurl)
headers = c(
  "Content-Type" = "text/plain"
)
params = "{  \"username\": \"\",   \"password\": \"\" }\r\n"
res <- postForm("https://{{api_domain}}/{{env}}/auth", .opts=list(postfields = params, httpheader = headers, followlocation = TRUE), style = "httppost")
cat(res)
```
