# ImpactApi - Create Project Workflow
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#impacts)
- Projects are the top level of organization for an analysis and contain the specifics of the Aggregation Scheme, Household Set, MRIO status, and folder placement.
- Inside the project, you will define the Events, which are the changes to an economy that you want to analyze, and the Groups, which are the Regions and time frame the changes take place. 

### 🗈 Notes
- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
	- Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
- Variables required for Endpoint calls will appear inside of double-braces (`{{}}`) and they must be replaced with valid values before the Request is sent
	- _e.g._ `{{api_domain}}` should be replaced with `https://api.implan.com/` for Public Production requests
	- See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information


---
## 🔽 Create the Project
- To create a Project, you need to acquire an Aggregation Scheme Id and a Household Set Id

---
### Get / Filter Aggregation Schemes
- [Impact Readme - Aggregation Schemes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#aggregation-schemes)
- The first step to create a Project is to find the Aggregation Scheme

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
### Initialize Project
- Once you have chosen your Aggregation Scheme Id and one of its Household Set Ids, you can create your Project
- [Impact Readme - Create Project](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-project-post)
- This endpoint creates a Project and returns basic information about it, including a unique identifier `projectId` (guid) to be used in other API requests.

##### Request
- `POST {{api_domain}}api/v1/impact/project`
- A `json` Project definition must be included in the body:
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

##### Response
- Returns the `json` for the newly created Project (see Project Json above)


---
## 🔽 Gather Event Information
- In order to populate a Project with Events, there are several endpoints that can be used to get the information needed to populate one

---
### Industry Codes
- [Impact Readme - Industry Codes](https://github.com/Implan-Group/api/blob/main/impact/readme.md#industry-codes-endpoint-get)
- With a Project created, you will next need to determine an industry code to use for your event. A list of industries that can be utilized for your analysis. Events created later will require reference to one of the industry codes (`code`) returned here.

##### Request
- `GET {{api_domain}}api/v1/IndustryCodes/{{aggregationSchemeId}}`

##### Response
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

---
### Event Types
- [Impact Readme - Event Types](TODO)
- There are many types of Events that can be added to a Group, this endpoint retrieves a list of them

##### Request
- `GET {{api_domain}}api/v1/impact/project/{{projectId}}/eventtype`
  - The `Project Id` for the created Project must be passed into this endpoint in order to filter the results to only applicable Events

##### Response
- This endpoint returns a `json` array of the names of valid Event Types
```json
[  
  "IndustryOutput",  
  "IndustryEmployment",  
  "IndustryEmployeeCompensation",  
  "IndustryProprietorIncome",  
  "IndustryImpactAnalysis",  
  "IndustryContributionAnalysis",  
  "CommodityOutput",  
  "LaborIncome",  
  "HouseholdIncome",  
  "IndustrySpendingPattern",  
  "InstitutionalSpendingPattern"  
]
```


---
## 🔽 Add the Events
- [Impact Readme - Create Events](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-event-post)
- With a new Project and Industry Code(s) in hand, you can now create Events.

---
### 📄 Event Json
- The `json` that needs to be sent is different for each `Impact Event Type`
- All Events have some `json` in common:
  ```json
  {
    "id": "deadbeef-f5be-458f-8efc-3b50ac0e5b1a",
    "projectId": "deadbeef-f5be-458f-8efc-3b50ac0e5b1a",
    "impactEventType": "IndustryOutput",
    "title": "EVENT TITLE",
    "tags": [],
  }
  ```
  - `id` (guid): Unique identifier for this Event
  - `projectId` (guid): Unique identifier for the Project this Event belongs to
  - `impactEventType` (text): The specific Impact Event Type for this event. 
    - _Note:_ Each Impact Event Type has slightly different input/output Properties
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
  "intermediateOutputs": 500000,
  "totalEmployment": 5,
  "employeeCompensation": 250000,
  "proprietorIncome": 50000,
  "wageAndSalaryEmployment": 4,
  "proprietorEmployment": 1,
  "totalLaborIncome": 300000,
  "otherPropertyIncome": 100000,
  "taxOnProductionAndImports": 100000,
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
### Add Event
- This endpoint creates an Event in the Project specified and returns information about it, including a Guid event identifier `eventId`

##### Request
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/event`
  - A `json` body must be included that defines the Event (see Event Json above)

##### Response
- Returns the fully-hydrated Event's Json (see above)


---
## 🔽 Locate Regions
- See the `Regions.md` Workflow document located in the same directory as this one for a complete overview on Regions and Searching for them


---
## 🔽 Define Project Groups
- [Impact Readme - Create Group](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-group-post)
- Groups represent the Region and timeframe in which an Event takes place. Use the following endpoints to arrange Groups in your project. Reference the `ProjectId` and `EventId`s from the created Project and Events where required.

### Group Json
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
### Add Group

##### Request
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/group`
  - A `json` body defining the Group must be passed (see Group Json above)

##### Response
- A fully-hydrated `json` Group will be returned (see Group Json above)


---
## Finishing Up
- Once a Project has been created, one or more Events have been added, and then one or more Groups have been added to link those Events to Regions, your Impact can be executed.
- See `RunImpactAnalysis.md` in the same folder as this document in order to see the Workflow around executing a Project Impact Analysis