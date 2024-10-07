# ImpactApi - Multi-Event to Multi-Group Workflow
- Sometimes for an advanced Project, several Events are created and then all of them are assigned to several Groups
- The workflow here demonstrates an easy way of looping through Regions in order to accomplish this task.

### 🗈 Notes

- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md) and to the C# example workflow in `MultiEventToMultiGroupWorkflow.cs`
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
  - Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
- Variables required for Endpoint calls will appear inside of double-braces (`{{}}`) and they must be replaced with valid values before the Request is sent
  - _e.g._ `{{api_domain}}` should be replaced with `https://api.implan.com/` for Public Production requests
  - See the [Production Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#production-variables) section of the Readme for more information

## 🔽 Create your Project

- Please see the `CreateProject.md` workflow for an overview on creating the Project. 
- A valid `guid` Project Id is required for most of the steps in this workflow.

---
## 🔽 Locate Regions
- See the `Regions.md` Workflow document for a complete overview on Regions and Searching for them
- For this example, we're going to creating one Group for each Region, so more than one Regional `Urid` will be required

---
## 🔽 Gather Additional Event Information
- Some Events, like Household Income Events, require an additional Specification Code

### Get Project Specification
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#get-project-specification-get)
- For a given Project, this endpoint retrieves valid Specification Codes for any given Event Type

##### Request
- `GET {{api_domain}}api/v1/impact/project/{{projectGuid}}/eventtype/{{eventType}}/specification`
  - `projectGuid` - The `guid` Id for the existing Project
  - `eventType` - The `text` Event Type to get Specification Codes for
  	- See `Event Types` in the `CreateProject.md` workflow for the endpoint to get these Types

##### Response
- Returns a list of Specification Codes appropriate for Events of the given Type that could be added to the given Project
- Example output from `HouseholdIncome` event type:
```json
[
    {
        "code": "10001",
        "name": "10001 - Households LT15k"
    },
    {
        "code": "10002",
        "name": "10002 - Households 15-30k"
    },
    {
        "code": "10003",
        "name": "10003 - Households 30-40k"
    },
    {
        "code": "10004",
        "name": "10004 - Households 40-50k"
    },
    {
        "code": "10005",
        "name": "10005 - Households 50-70k"
    },
    {
        "code": "10006",
        "name": "10006 - Households 70-100k"
    },
    {
        "code": "10007",
        "name": "10007 - Households 100-150k"
    },
    {
        "code": "10008",
        "name": "10008 - Households 150-200k"
    },
    {
        "code": "10009",
        "name": "10009 - Households GT200k"
    }
]
```
	- `code` (number) - The Specification Code
	- `name` (text) - A description of what the Spec Code represents

---
## 🔽 Add the Events
- [Impact Readme - Create Events](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-event-post)
- Once the Project exists, you can start by creating all of the Events that are to be assigned to the Groups
- See the `CreateProject` workflow document for more Event information

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

#### Additional Household Income Event Json
- [support.implan.com](https://support.implan.com/hc/en-us/articles/360052212413-Household-Income-Events)
- Household Income Events require a `HouseholdIncome` Event Type and a valid `Specification Code` (see above)
```json
{
    "ImpactEventType": "HouseholdIncome",
    "Title" : "ImpactApi - HouseholdIncomeEvent - Example",
    "HouseholdIncomeCode": 10001,
    "Value" : 100000.01,
    "Tags": []
}
```

---
## 🔽 Define Project Group per Region
- [Impact Readme - Create Group](https://github.com/Implan-Group/api/blob/main/impact/readme.md#create-group-post)
- Groups represent the Region and timeframe in which an Event takes place. Use the following endpoints to arrange Groups in your project. Reference the `ProjectId` and `EventId`s from the created Project and Events where required.
- For every Region the Events are to be run in, a Group needs to be created. Multiple Events can be added to a single Group by specifying each's Id in an array:

### Group Json
```json
{
  "projectId": "deadbeef-92d9-45e0-a8b8-e29d83d2a64e",
  "hashId": "Rgxp4eA3xK",
  "title": "ImpactApi - Example - Group 1",
  "dollarYear": 2024,
  "datasetId": 96,
  "groupEvents": [
    {
      "eventId": "3366781B-7261-466C-A6AC-5D63BC08F1B5"
    },
    {
      "eventId": "548391D5-51AC-4704-9972-B7561006930D"
    },
    {
      "eventId": "E964EE78-350E-4717-B44B-85D37BE9637F"
    }
  ],
}
```
- `projectId` (guid): The Project's GUID Identifier -- does not need to be in incoming body as it is passed as an Url parameter
- `hashId` (text, optional): The HashId for the Region to associate with this Group
- `title` (text): Unique-per-Project Name for this Group
- `dollarYear` (number): The Dollar Year for the Group (same as 4-digit year)
- `datasetId` (number): The Data Set Id for the Group (see above)
- `groupEvents` (json-array): An array of the Events to associate with this Group
  - `eventId` (guid): The guid Id for the Event to associate

---
### Add Groups to Project
- Loop through each Region, create a Group for each that contains all of the Events, and then add that Group to the Project

##### Request
- `POST {{api_domain}}api/v1/impact/project/{{project_id}}/group`
  - A `json` body defining the Group must be passed (see Group Json above)

##### Response
- A fully-hydrated `json` Group will be returned (see Group Json above)

---
## Finishing Up

- Once a Project has been created, the Events have been added, and then Groups have been added to link those Events to Regions, your Impact can be executed.
- See `RunImpactAnalysis.md` in the same folder as this document in order to see the Workflows around executing a Project Impact Analysis