# Impact API - Create Project Workflow
- This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Further detail on additional workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us)

## Overview
- Projects are the top level of organization for an analysis and contain the specifics of the aggregation scheme, household set, MRIO status, and folder placement.
- This document describes the basic IMPLAN ImpactAPI workflow to create a Project
- Variables for endpoints will appear inside of double-brackets, those must be replaced with valid values before execution
  - e.g. `{{api_domain}}`
  - See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information

#### Authorization
- Note that all API Endpoints require a valid JWT Bearer Token ([JWT.IO](https://jwt.io/))
  -	Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section of the primary Readme to review authentication steps

#### Data Limitations
- Endpoints that combine IMPLAN's economic data with other data are limited to only those datasets to which those other data are available. (This primarily effects Canada + International customers)


## Workflow

#### Find a Region and Industry to Study
- All region data in IMPLAN are unique based upon the Aggregation Scheme, Dataset (data year), and geographic demarcation (zip, county, state, etc...).
- The unique regional identifiers used with the IMPLAN API are:
  - [HashID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#hashid)
  - [URID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#urid)
    - URIDs are slowly being depreciated, prefer HashIds whenever possible
- One or the other of the above identifiers are used for calls to build combined regions, pull region data, and assign to groups for impacts.

### Aggregation Schemes
- As the region identifiers are specific to both Aggregation Scheme and Dataset, both need to be determined before finally pulling a specific region identifier.
- This endpoint will return a list of all aggregation schemes available for use.

#### Endpoints
- `GET {{api_domain}}api/v1/aggregationSchemes`
- `GET {{api_domain}}api/v1/aggregationSchemes?industrySetId={{industry_set_id}}`
  - The `industrySetId` is an optional filter that can be applied to limit the returned Aggregation Schemes further
  - See [Industry Sets](https://github.com/Implan-Group/api/blob/main/impact/readme.md#industry-sets) in the main Readme
##### Response
- A `json` array of valid Aggregation Schemes
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
        "id": 1099,
        "description": "PHX-11434 - UDFA1",
        "industrySetId": 8,
        "householdSetIds": [
            1
        ],
        "mapCode": "US",
        "status": "Complete"
    }
]
```
- `id` (number): Aggregation Scheme Identifier
- `description` (text): Description of the aggregation scheme
- `industrySetId` (number): Industry Set Identifier
- `householdSetIds` (array of numbers): Valid Household Set Identifiers that can be used with this aggregation scheme
- `mapCode` (text): 
- `status` (text): Whether or not this aggregation scheme has been built yet


### Project Creation
- Once you have chosen your Aggregation Scheme Id and Household Set Id, you can create your Project
- This endpoint creates a Project and returns basic information about it, including a unique identifier `projectId` (guid) to be used in other API requests.

#### Endpoint
- `POST {{api_domain}}api/v1/impact/project`
  - [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-project-post)
  - A `json` body must be included that defines the Project:
  ```json
  {
    "title": "(text)",
    "aggregationSchemeId": (number),
    "householdSetId": (number),
  }
  ```
  
##### Response
```json
{
    "id": "(guid)",
    "title": "(text)",
    "aggregationSchemeId": (number),
    "householdSetId": (number),
    "isMrio": (boolean),
    "folderId": (number?),
    "lastImpactRunId": (number?)
}
```
  - `id` (guid): The unique Project Identifier, used for subsequent requests
  - `title` (text): The same Title that was specified in the original POST
  - `aggregationSchemeId` (number): The Aggregation Scheme Id that was originally specified
  - `householdSetId` (number): The Household Set Id that was originally specified
  - `isMrio` (boolean): Whether or not this is an MRIO Project
  - `folderId` (number, optional): If this Project is located under a Folder, this is the Identifier for that folder
  - `lastImpactRunId` (number, optional): If this Project has had an Impact run, the Identifier of that last Impact (defaults to `null`)


### Industry Codes
- With a Project created, you will next need to determine an industry code to use for your event. A list of industries that can be utilized for your analysis. Events created later will require reference to one of the industry codes (`code`) returned here.

#### Endpoints
- `GET {{api_domain}}api/v1/IndustryCodes/{{aggregationSchemeId}}`
##### Response
- A `json` array of industries
```json
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
	},
	...
]
```


### Events
- With a new Project and Industry Code(s) in hand, you can now create Events.
- This endpoint creates an Event in the Project specified and returns information about it, including an event identifier `eventId` (guid). 

#### Endpoints
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/event`
  - You must pass in the full guid Project Id obtained above
  - A `json` body must be included that defines the Event
    - [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-event-post)
  ```json
  {
    "impactEventType": "IndustryOutput",
    "title" : "IndustryOutput Event 01",
    "industryCode": 1,
    "output" : 100000,
    "employment" : 20.25,
    "employeeCompensation" : 50000.23,
    "proprietorIncome" : 3400.233,
    "tags": ["Testing"]
  }
  ```
  - `ImpactEventType` (text): The type of the Event to add
    - (endpoint to retrieve DNE)
    - Common options: `IndustryOutput`, `IndustryEmployment`, `IndustryEmployeeCompensation`, `IndustryProprietorIncome`
  -  `title` (text): The name of the Event
  -  `industryCode` (number): The Industry's Code
  -  `output` (number): Total Industry Output
  -  `employment` (number): Total Industry Employment
  -  `employeecompensation` (number): Total Employee Compensation
  -  `proprietorincome` (number): Total Proprietor Income
  -  `tags` (array of texts): Additional Tags to associate with the Event
    - _Note:_ See the Impact Readme for further description of when these properties are required

##### Response
- This endpoint will return the `json` for the full Event:
```json
{
  "output": 100000.0,
  "employment": null,
  "employeeCompensation": null,
  "proprietorIncome": null,
  "industryCode": 1,
  "marginType": "ProducerPrice",
  "percentage": null,
  "datasetId": null,
  "id": "142cb62c-f5be-458f-8efc-3b50ac0e5b1a",
  "projectId": "3be62e74-feab-4fcd-8401-e899deb00958",
  "impactEventType": "IndustryOutput",
  "title": "Industry Output",
  "tags": []
}
```
  - You will need the `id` when defining Groups


### Datasets
- To explore Regions further, a Dataset Id is required -- this specifies the Data Year

#### Endpoints
- `{{api_domain}}api/v1/datasets`
- `{{api_domain}}api/v1/datasets/{{aggregationSchemeId}}`
  - Use this endpoint to further filter the Datasets by Aggregation Scheme Id
##### Response
- A `json` array of valid Datasets
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


### Region Selection
- Once Aggregation Scheme Id and Dataset Id have been determined, use the following region endpoints to peruse base region data and pull HashIds for your region(s) of interest.
- [Building Regions](https://github.com/Implan-Group/api/blob/main/impact/readme.md#building-regions)
- [Customizing Regions](https://github.com/Implan-Group/api/blob/main/impact/readme.md#customizing-regions)

#### Endpoints
- `GET {{api_domain}}api/v1/region/RegionTypes`
  - Returns a `json` array of text that describes all the Region Types that can be used for filtering
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}`
  - Returns the top-level Region that matches the Aggregation + Dataset
    - This is usually the country (e.g. US, Canada)
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/children`
  - Returns all children regions that match the Aggregation + Dataset
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/children?regionTypeFilter={{regionType}}
  - You can include an optional `regionTypeFilter` to specify which type(s) of children region(s) to return
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{dataSetId}}/user`
  - Returns all combined and customized Regions that the current User has access to
##### Response
```json
{
    "hashId": "A2xqd6R4Vq",
    "urid": 1647029,
    "userModelId": null,
    "description": "United States (US Totals)",
    "modelId": 12165,
    "modelBuildStatus": "Complete",
    "employment": 195672800.00000054,
    "output": 40716417742635.2,
    "valueAdded": 23315081000000.004,
    "aggregationSchemeId": 8,
    "datasetId": 87,
    "datasetDescription": "2021",
    "fipsCode": null,
    "provinceCode": null,
    "m49Code": "840",
    "regionType": "Country",
    "hasAccessibleChildren": false,
    "regionTypeDescription": "Country",
    "geoId": "840",
    "isMrioAllowed": false
}
```

### Groups
- Groups represent the Region and timeframe in which an Event takes place. Use the following endpoints to arrange Groups in your project. Reference the `ProjectId` and `EventId`s from the created Project and Events where required.

#### Endpoints
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/group`
  
  - `project_id` (guid): The Guid from the created Project
  - A `json` body must be included that defines the Group
  ```json
  { 
  	projectId = "2dc00b71-302e-4b79-8f78-bddd69cb2e82", 
  	title = "Sample Group 1", 
  	datasetId = 96, 
  	dollarYear = 2024,  	
  	hashId = "15b869ZOxy", 
  	groupEvents = [
      { 
        eventId = "8b71fbd1-592b-414a-95ef-9b534b9a246d"
      }
  	]
  }
  ```
  - `projectId` (guid): The Guid of the Project to associate this Group with
  - `title` (text): Unique-per-Project Title of this Group
  - `datasetId` (number): The Dataset to use
  - `dollarYear` (number): The Dollar Year to use
  - `hashId` (text): The HashId for the Region to associate with this Group
  - `groupEvents` (array): An array of Events to associate with this Group
    - `eventId` (guid): The Guid of the Event to associate with this Group