# Impact API - Create Project Workflow
- This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Further detail on additional workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us)
- Projects are the top level of organization for an analysis and contain the specifics of the Aggregation Scheme, Household Set, MRIO status, and folder placement.
- This document describes the basic IMPLAN ImpactAPI workflow to create a Project, add Events, and link Events and Regions in Groups

### Notes:
- All API Endpoints require a valid JWT Bearer Token ([JWT.IO](https://jwt.io/))
  - Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section of the primary Readme to review authentication steps
- Variables for endpoints will appear inside of double-braces, those must be replaced with valid values before execution
  - e.g. `{{api_domain}}` should be replaced with `https://api.implan.com/`
  - See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information
- Endpoints that combine IMPLAN's economic data with other data are limited to only those datasets to which those other data are available. (This primarily effects Canada + International customers)


---
## Aggregation Schemes
- [Impact Readme - Aggregation Schemes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#aggregation-schemes)
- The first step to create a Project is to find the Aggregation Scheme
- `GET {{api_domain}}api/v1/aggregationSchemes`
- `GET {{api_domain}}api/v1/aggregationSchemes?industrySetId={{industry_set_id}}`
  - The `industrySetId` is an optional filter that can be applied to limit the returned Aggregation Schemes further
  - [Impact Readme - Industry Sets](https://github.com/Implan-Group/api/blob/main/impact/readme.md#industry-sets)
- Returns a `json` array of valid Aggregation Schemes
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
        "description": "Custom Scheme",
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
- `mapCode` (text): A code to describe
- `status` (text): Whether or not this aggregation scheme has been built yet


---
## Create Project
- Once you have chosen your Aggregation Scheme Id and one of its Household Set Ids, you can create your Project

#### Project Json
- The `json` representation of a Project looks like this:
```json
{
    "id": "deadbeef-2600-1337-cafe-123456789abc",
    "title": "Project Title",
    "aggregationSchemeId": 8,
    "householdSetId": 1,
    "isMrio": false,
    "folderId": null,
    "lastImpactRunId": null
},
```
- `id` (guid): The unique identifier for this Project
- `title` (text): The unique description for this Project
- `aggregationSchemeId` (number): The Aggregation Scheme this Project is using
- `householdSetId` (number): The Household Set this Project is using
- `isMrio` (boolean): Whether or not this Project is using Multi-Region Input/Output (MRIO) Analysis
- `folderId` (number, optional): If present, the identifier of the Folder that the Project is located under in IMPLAN Cloud
- `lastImpactRunId` (number, optional): If an Impact Analysis has already been performed for this Project, the Id of the last one (used for querying Analysis status)

### Create Project
- [Impact Readme - Create Project](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-project-post)
- This endpoint creates a Project and returns basic information about it, including a unique identifier `projectId` (guid) to be used in other API requests.
- `POST {{api_domain}}api/v1/impact/project`
  - Returns a `json` Project


---
## Add Project Events

#### Industry Codes
- [Impact Readme - Industry Codes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#industry-codes-endpoint-get)
- With a Project created, you will next need to determine an industry code to use for your event. A list of industries that can be utilized for your analysis. Events created later will require reference to one of the industry codes (`code`) returned here.
- `GET {{api_domain}}api/v1/IndustryCodes/{{aggregationSchemeId}}`
  - Returns a `json` array of Industries
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

#### Event Types
- [Impact Readme - Event Types](TODO)
- There are many types of Events that can be added to a Group, this endpoint retrieves a list of them
- `GET {{api_domain}}api/v1/impact/project/{{projectId}}/eventtype`
  - The Project Id for the created Project must be passed into this endpoint in order to filter the results to only applicable Events
- This endpoint returns an array of the names of valid Event Types
	- _e.g. `IndustryOutput`, `IndustrySpendingPattern`, ..._

### Add Events
- [Impact Readme - Create Events](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-event-post)
- With a new Project and Industry Code(s) in hand, you can now create Events.
- This endpoint creates an Event in the Project specified and returns information about it, including an event identifier `eventId` (guid). 
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/event`
  - You must pass in the full guid `Project Id` obtained above
  - A `json` body must be included that defines the Event
    ```json
    {
      "impactEventType": "IndustryOutput",
      "title" : "IndustryOutput Event 01",
      "industryCode": 1,
      "output" : 100000,
      "employment" : 20.25,
      "employeeCompensation" : 50000.23,
      "proprietorIncome" : 3400.233,
      "tags": ["Testing"],
    }
    ```
    - `ImpactEventType` (text): The type of the Event to add
      - TODO: ENDPOINT
      - Common options: `IndustryOutput`, `IndustryEmployment`, `IndustryEmployeeCompensation`, `IndustryProprietorIncome`
    - `title` (text): The name of the Event
    - `industryCode` (number): The Industry's Code
    - `output` (number): Total Industry Output
    - `employment` (number): Total Industry Employment
    - `employeecompensation` (number): Total Employee Compensation
    - `proprietorincome` (number): Total Proprietor Income
    - `tags` (array of texts): Additional Tags to associate with the Event
- This endpoint will return the fully hydrated Event `json` (see below)

#### Event Json
- The `json` that needs to be sent is different for each `Impact Event Type`
- All Events have some `json` in common:
  ```json
  {
    "id": "deadbeef-f5be-458f-8efc-3b50ac0e5b1a",
    "projectId": "deadbeef-f5be-458f-8efc-3b50ac0e5b1a"
    "impactEventType": "IndustryOutput",
    "title": "EVENT TITLE",
    "tags": [],
  }
  ```
  - `id` (guid): Unique identifier for this Event
  - `projectId` (guid): Unique identifier for the Project this Event belongs to
  - `impactEventType` (text): The specific Impact Event Type for this event. 
    - _Note:_ Each Impact Event Type has slightly different input/output Properties, see below.
  - `title` (text): Unique-per-Project description of this Event
  - `tags` (array of text, optional): Additional Tags to associate with this Event
  
#### Additional Industry Output Event Json
- [support.implan.com](https://support.implan.com/hc/en-us/articles/360051441834-Industry-Events)
```json
{
  "output": 1000000.00,
  "employment": 500.00,
  "employeeCompensation": 100.00,
  "proprietorIncome": 65.14,
  "industryCode": 1,
  "marginType": null,
  "percentage": null,
  "datasetId": 96,  
}
```
  - `output` (number, optional): Total output value of this Industry Output Event
  - `employment` (number, optional): Total employment value
  - `employeeCompensation` (number, optional): Total employee compensation
  - `proprietorIncome` (number, optional): Total proprietor compensation
  - `industryCode` (number): The Industry's Code (see above)
  - `marginType` (text, optional): See [Implan Support](support.implan.com)
  - `percentage` (number, optional): See [Implan Support](support.implan.com)
  - `datasetId` (number, optional): The Dataset Id (see above)

#### Additional Industry Impact Analysis Event Json
- [support.implan.com](https://support.implan.com/hc/en-us/articles/4414451454491-Industry-Impact-Analysis-Detailed-Events)
```json
{
  "industryCode": 1,
  "intermediateOutputs": 100.10,
  "totalEmployment": 50.2,
  "employeeCompensation": 147.30,
  "proprietorIncome": 5000.00,
  "wageAndSalaryEmployment": 700.00,
  "proprietorEmployment": 134.00,
  "totalLaborIncome": 9500.50,
  "otherPropertyIncome": 700.00,
  "taxOnProductionAndImports": 14900.80,
  "localPurchasePercentage": 1.0,
  "totalOutput": 1500000.00,
  "isSam": false,
  "spendingPatternDatasetId": null,
  "spendingPatternValueType": "Output",
  "spendingPatternCommodities": [
    {
      "coefficient": 1.0,
      "commodityCode": 3011,
      "commodityDescription": "Beef cattle",
      "isSamValue": false,
      "isUserCoefficient": false,
      "localPurchasePercentage": 1.0,
    },
    ...
  ]
}
```


---
## Locate Regions
- All region data in IMPLAN are unique based upon the Aggregation Scheme, Dataset (data year), and geographic demarcation (zip, county, state, etc...).
- The unique regional identifiers used with the IMPLAN API are:
  - [HashID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#hashid)
  - [URID](https://github.com/Implan-Group/api/blob/main/impact/readme.md#urid)
    - URIDs are slowly being depreciated, prefer HashIds whenever possible
- One or the other of the above identifiers are used for calls to build combined Regions, pull Region data, and assign to Groups for Impacts.

#### Datasets
- To explore Regions further, a Dataset Id is required -- this specifies the Data Year
- `GET {{api_domain}}api/v1/datasets`
- `GET {{api_domain}}api/v1/datasets/{{aggregationSchemeId}}`
  - Use this endpoint to further filter the Datasets by Aggregation Scheme Id
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

#### Region Json
- The `json` response from regional endpoints is either a single Region or an Array of Regions, shaped like this:
  - _Note: Some information may be `null` as it is not relevant for the Region_
  - _e.g. Combined Regions will have a `null` `fipsCode`_
```json
{
    "hashId": "Rgxp4eA3xK",
    "urid": null,
    "userModelId": 9601,
    "description": "Workflow - Regions",
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


## Region Endpoints

### Region Types
- `GET {{api_domain}}api/v1/region/RegionTypes`
  - Returns a `json` array of Regions

### Top-Level Region
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}`
  - Returns the `json` representation of the Top-Level Region for a given Aggregation Scheme and Dataset
  - This is usually the Country that matches the Dataset (e.g. US, Canada)

### Region Children
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children`
  - Returns a `json` array of all of the Children Regions in a Dataset
    - This will include _all_ children (zip, county, state, msa)
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/children?regionTypeFilter={{regionType}}`
  - On optional `regionTypeFilter` can be specified to limit the returned Regions

### User Regions
- `GET {{api_domain}}api/v1/region/{{aggregationSchemeId}}/{{datasetId}}/user`
  - Returns a `json` array of all of the User-defined Regions in a Dataset
  - This includes all customized and combined Regions


---
## Add Groups
- [Impact Readme - Create Group](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-group-post)
- Groups represent the Region and timeframe in which an Event takes place. Use the following endpoints to arrange Groups in your project. Reference the `ProjectId` and `EventId`s from the created Project and Events where required.
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/group`
  - `project_id` (guid): The Guid from the created Project
  - A `json` body must be included that defines the Group

#### Group Json
```json
{
  "id": "deadbeef-edbb-4fca-8f8b-1c9779cd1588",
  "projectId": "deadbeef-92d9-45e0-a8b8-e29d83d2a64e",
  "hashId": "Rgxp4eA3xK",
  "urid": 1819520,
  "userModelId": null,
  "modelId": 14998,
  "title": "Sample Group 1",
  "dollarYear": 2024,
  "scalingFactor": 1.0,
  "datasetId": 96,
  "groupEvents": [
    {
      "eventId": "deadbeef-7eec-4241-bc82-d58f65fac4f0",
      "scalingFactor": 1.0
    },
    ...
  ],
}
```
- `id` (guid): Unique identifier for this Group, will be created during the `CreateGroup` endpoint call -- do not specify in incoming body
- `projectId` (guid): The Project's GUID Identifier -- does not need to be in incoming body as it is passed as an Url parameter
- `hashId` (text, optional): The HashId for the Region to associate with this Group
- `urid` (number, optional): The URID for the associated Region
- `userModelId` (number, optional): The User Model Id for the associated Region
- `modelId` (number, optional): The Model Id for the associated Region
  - Only one of `HashId`, `Urid`, `UserModelId`, or `ModelId` should be specified in the Request Body -- `HashId` is the preferred option
- `title` (text): Unique-per-Project Name for this Group
- `dollarYear` (number): The Dollar Year for the Group (same as 4-digit year)
- `scalingFactor` (number): Percentage (0.0 .. 1.0) of Scaling to apply to this Group
- `datasetId` (number): The Data Set Id for the Group (see above)
- `groupEvents` (json-array): An array of the Events to associate with this Group
  - `eventId` (guid): The guid Id for the Event to associate
  - `scalingFactor` (number): Percentage (0.0 .. 1.0) of Scaling to apply to this Event


---
## Finishing Up
- Once a Project has been created, one or more Events have been added, and then one or more Groups have been added to link those Events to Regions, your Impact can be executed.
- See `RunImpactAnalysis.md` in the same folder as this document in order to see the Workflow around executing a Project Impact Analysis