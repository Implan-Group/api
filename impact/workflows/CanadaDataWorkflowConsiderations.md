# Canada Data Workflow Considerations
This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md) and contains workflow instructions and considerations for those seeking to work with Canadian data.
This document describes the basic IMPLAN workflow as it relates the IMPLAN's Impact API. More detail on additional IMPLAN workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us).

## Overview
### Authorization
Please note that all API endpoint requests presented in this document require a bearer token. Please see the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the ReadMe, to review authentication steps. A token is valid for 24 hours and must be cached and reused.

### Domain References
See the [Production Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#production-variables) section of the ReadMe for information regarding the `{{api_domain}}` variables used in this document.

### Data Limitations
Endpoints that combine IMPLAN's economic data with other data are limited to only those datasets to which those other data are available. For Canadian data, that means API endpoints reporting the following types of data are not available:
* Environment
* Occupation

## Workflow
### Find a Region and Industry to Study
All region data in IMPLAN are unique based on the Aggregation Scheme, Dataset (data year), and geographic demarcation. The unique region identifiers used for interacting with the IMPLAN API are:
* [URID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#urid)
* [HashID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#hashid)

One or the other of the above identifiers are used for calls to build combined regions, pull region data, and assign to groups for impacts.

### Aggregation Schemes Endpoint (Get)
As the region identifiers are specific to both Aggregation Scheme and Dataset, both need to be determined before finally pulling a specific region identifier. This endpoint will return a list of aggregation schemes available for use.
For Canadian analyses, only aggregation schemes with a `MapCode` of `CAN` are valid. Also take note of the scheme's `householdSetIds`, as one of them will be required for creating a project later in the process.
Each Canadian Aggregation Scheme lists its own Household Sets, and the value differs by scheme, so read it from the scheme you chose rather than carrying one between them.

Two Canadian industry vintages are in use. Scheme 12 (235 Unaggregated Canada) is the older one and appears in the example below; scheme 17 (236 Unaggregated Canada) is the newer. Resolve the scheme at runtime rather than hardcoding either, by taking the newest Industry Set with a `mapCode` of `CAN` and using the Unaggregated scheme built on it.
#### Parameters
* Bearer Token
* IndustrySetId (optional filter)
#### Response (List)
* Id (Aggregation Scheme Id)
* Description
* Industry Set Id
* Household Set Ids []
* Map Code
* Status
#### Sample Response
```
[   …
	{
		"id": 12,
		"description": "235 Unaggregated Canada",
		"industrySetId": 10,
		"householdSetIds": [
                    4
		],
		"mapCode": "CAN",
		"status": "Complete"
	},
    …
]
```
#### Endpoint
**GET {{api_domain}}api/v1/aggregationschemes?industrySetId={{industrySetId}}**


### Dataset Endpoint (Get)
Use the desired Aggregation Scheme Id with this endpoint to pull a list of available datasets.
#### Parameters
* Bearer Token
* Aggregation Scheme Id (URL Parameter)
#### Response (List)
* Data Set ID (Number)
* Data Set Description (Text)
* Default Data Set (Boolean - only 1 record in the list should be true)

Dataset Ids belong to one Aggregation Scheme and are not ordered by year, so never carry an Id from one scheme to another and never assume the newest is last in the list. Read the list for the scheme you are using and take the entry flagged `isDefault`. The Ids and years below are one scheme's list at one point in time, shown to illustrate the shape of the response; IMPLAN publishes a new data year annually, so yours will differ.
#### Sample Response
```json
[
	{
		"id": 86,
		"description": "2017",
		"isDefault": false
	},
	{
		"id": 88,
		"description": "2018",
		"isDefault": false
	},
	{
		"id": 89,
		"description": "2019",
		"isDefault": false
	},
	{
		"id": 93,
		"description": "2020",
		"isDefault": true
	}
]
```
#### Endpoint
**GET {{api_domain}}api/v1/datasets/{{aggregationSchemeId}}**

### Region Selection Endpoints
With Aggregation Scheme Id and Dataset Id determined, use the following region endpoints to peruse base region data and pull URID and Hash Ids for your region(s) of interest.
* [Top Level Region (GET)](https://github.com/Implan-Group/api/blob/main/impact/readme.md#top-level-region)
  * For Canadian data, the endpoint described here will return data for Canada.
* [Top Level Region Children (GET)](https://github.com/Implan-Group/api/blob/main/impact/readme.md#top-level-region-children)
  * For Canadian data, the endpoint described here return a list of data for Canadian Provinces.
  * If using the `regionType` parameter option to filter the list of returned regions, use `State` to filter on Canadian Provinces and `County` to filter on Candian Economic Regions.
* [User Custom and Combined Regions (GET)](https://github.com/Implan-Group/api/blob/main/impact/readme.md#user-custom-and-combined-regions-get)
  * The endpoint described here will return a list of combined and/or customized models for the provided Aggregation Scheme Id and Dataset Id.

### Region Building and Customizing Endpoints
For analyses requiring the combination of Provinces or customization of underlying economic data, see
* [Building Regions](https://github.com/Implan-Group/api/blob/main/impact/readme.md#building-regions)
* [Customizing Regions](https://github.com/Implan-Group/api/blob/main/impact/readme.md#customizing-regions)

### Region Data Exports
The [Region Data Exports](https://github.com/Implan-Group/api/blob/main/impact/readme.md#regional-data-exports) section of the readme covers all current endpoints available for exporting region level data. As with 
the region selection endpoints, these endpoints rely on the URID or Hash Id discussed above.


### Industry Codes (Get)
Use the following endpoint to pull a list of industries that can be utilized for your analysis. Events created later will require reference to one of the industry codes (`code`) returned here.
#### Parameters
* Bearer Token
* Aggregation Scheme Id (URL Parameter)
#### Response (List)
* Industry Id
* Industry Code
* Industry Description
#### Sample Response
```
[
	{
		"id": 5221,
		"code": 1,
		"description": "Crop production (except cannabis, greenhouse, nursery and floriculture production)"
	},
	{
		"id": 5222,
		"code": 2,
	"description": "Greenhouse, nursery and floriculture production (except cannabis)"
	}, …
]
```
#### Endpoint
**GET {{api_domain}}api/v1/IndustryCodes/{{aggregationSchemeId}}**


## Arrange an Impact Analysis
To run an impact analysis, the following 3 steps must be completed first:
1. Creating a Project
2. Creating one or more Events
3. Creating one more Groups

### Creating a Project
Projects are the top level of organization for an analysis and contain the specifics of the aggregation scheme, household set, MRIO status, and folder placement. Below are the primary endpoints required for setting up a project.
* [Create Project (POST)](https://github.com/Implan-Group/api/tree/main/impact#create-project-post)
  * Creates a project and returns basic information about the project, including a unique identifier `ProjectId` (GUID) to be used in other API requests.
  * Sample Body Request:
  ```
  {
    "Title" : "Sample Canada Project",
    "AggregationSchemeId" : 12,
    "HouseholdSetId" : 4,
    "FolderId": 6883,
    "IsMrio": false
  }
* [Get Project (GET)](https://github.com/Implan-Group/api/tree/main/impact#get-projects-get)
  * Returns basic information about the project referenced by the `ProjectId`.
* [Update Project (PUT)](https://github.com/Implan-Group/api/tree/main/impact#update-project-put)
  * Updates basic information about the project referenced by the `ProjectId`.
* [Delete Project (DELETE)](https://github.com/Implan-Group/api/tree/main/impact#delete-project-delete)
  * Deletes the project referenced by the `ProjectId`.

Note: the base ReadMe file contains additional [endpoints](https://github.com/Implan-Group/api/blob/main/impact/readme.md#get-projects-shared-with-user-get) for working with projects, such as duplicating and sharing projects. 
For information on using folders, see the [Folders](https://github.com/Implan-Group/api/tree/main/impact#folders) section of the Readme. 

### Creating Events
Events represent the economic activity taking place and come in different forms. Below are the primary endpoints required for setting up events. Reference the `ProjectId` from the created project where required.
* [Create Event (POST)](https://github.com/Implan-Group/api/tree/main/impact#create-event-post)
  * Creates an event in the project specified and returns information about the event, including an event identifier `EventId` (GUID). This endpoint also makes use of an `IndustryCode` body parameter.
  * Sample Body Request:
  ```
  {
    "ImpactEventType": "IndustryOutput",
    "Title" : "Industry Output",
    "Output" : 100000.01,
    "IndustryCode": 1,
    "Employment" : 20.25,
    "EmployeeCompensation" : 50000.23,
    "ProprietorIncome" : 3400.233,
    "Tags": []
  }
* [Get Event (GET)](https://github.com/Implan-Group/api/tree/main/impact#create-event-post)
  * Gets the event specified by the `EventId`.
* [Update Event (PUT)](https://github.com/Implan-Group/api/tree/main/impact#update-events)
  * Updates the event specified by the `EventId`.
* [Delete Event (DELETE)](https://github.com/Implan-Group/api/tree/main/impact#delete-event-delete)
  * Deletes the even specified by the `EventId`.

### Creating Groups
Groups represent the region and timeframe in which an event takes place. Use the following endpoints to arrange groups in your project. Reference the `ProjectId` and `EventId`s from the created project and events where required.
* [Create Group (POST)](https://github.com/Implan-Group/api/tree/main/impact#create-group-post)
  * Creates a group that contains a reference to a project, a region, and to 1 or more events. Returns a group identifier `GroupId` (GUID).
  * Sample Body Request:
  ```json
  {
    "projectId": "32cf4b69-1b04-443a-a450-cc88e18e6905",
    "title": "Sample Group 1",
    "hashId": "5Oad9R1PbZ",
    "dollarYear": 2024,
    "datasetId": 93,
    "scalingFactor": 1,
    "groupEvents": [
      {
        "eventId": "6741df0d-c26c-44cf-9992-8aab695efd91",
        "scalingFactor": 1
      }
    ]
  }
  ```
  * The field is `scalingFactor`, one word and camelCase. `"Scaling Factor"` with a space is not a field this API defines
  * Always set `dollarYear`. There is no server-side default, and a Group stored without one produces an impact run that never attaches to the project, which surfaces later as a `404` from the status endpoint rather than as an error here
* [Get Group (GET)](https://github.com/Implan-Group/api/tree/main/impact#get-group-get)
  * Returns data on the group specified by the `GroupId`.
* [Update Group (PUT)](https://github.com/Implan-Group/api/tree/main/impact#update-group-put)
  * Updates the group specified by the `GroupId`.
* [Delete Group (DELETE)](https://github.com/Implan-Group/api/tree/main/impact#delete-group-delete)
  * Deletes the group specified by the `GroupId`.


### Run an Impact
Running an impact analysis requires a project with at least 1 event and one 1 group with a group event. Use the following endpoints to trigger an impact analysis, check impact analysis status, and cancel an impact analysis run.
* [Run an Impact (POST)](https://github.com/Implan-Group/api/tree/main/impact#run-impact-post)
  * Initiates an IMPLAN Analysis engine request for the project specified. Returns a `RunId` (INT) to be used with the next two endpoints and with all endpoints related to pulling impact analysis results.
* [Cancel Impact Run (PUT)](https://github.com/Implan-Group/api/tree/main/impact#cancel-impact-run-put)
  * Cancels the analysis run specified by the `RunId`.
* [Run Status (GET)](https://github.com/Implan-Group/api/tree/main/impact#run-status-get)
  * Gets the status of the analysis run specified by the `RunId`.


### Pulling Results from an Analysis
The [Results](https://github.com/Implan-Group/api/tree/main/impact#results) section of the readme covers all current endpoints available for exporting analysis results level data. These endpoints rely on the `RunId` discussed above.
#### Limitations
As mentioned at the top of this document, endpoints returning data regarding environment or occupation data are not available to Canadian based analyses.