# Impact API - Run Impact Analysis Workflow
- This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Further detail on additional workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us)

### Notes:
- All API Endpoints require a valid JWT Bearer Token ([JWT.IO](https://jwt.io/))
  -	Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section of the primary Readme to review authentication steps
- Variables for endpoints will appear inside of double-brackets, those must be replaced with valid values before execution
  - _e.g. `{{api_domain}}`_
  - See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information

---
## Overview
- Once a Project has been created and Events and Groups have been added, the impact analysis can be run in order to produce results
- [Impact Readme - Run Impact](https://github.com/Implan-Group/api/blob/main/impact/readme.md#run-impact-post)

---
## Workflow
- To run an Impact, you must first locate the Project that you wish to run the Impact for

### Search Projects
- There are several ways to search through all the Projects that your User has access to

#### Get All Projects
- If you want to look at all Projects that you created
- `GET {{api_domain}}api/v1/impact/project`
  - Returns a `json` array of Projects

#### Get a Specific Project
- If you want the details for a specific Project
- `GET {{api_domain}}api/v1/impact/project/{{projectId}}`
  - Returns the Project that has the given guid Project Id (if one exists)

#### Get All Projects Shared With Me
- If you want to look at all Projects that have been shared with you
- `GET {{api_domain}}api/v1/impact/project/shared`
  - Returns a `json` array of Projects

#### Project Json
- The `json` representation of a Project looks like this:
```json
{
    "id": "deadbeef-36e0-11ee-9af5-12fa59c0e2d9",
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


---
### Run the Impact
- Once you have located the Project Id for the Project you wish to run an Impact Analysis upon, you can launch the analysis
- `POST {{api_domain}}api/v1/impact/{{projectId}}`
  - Will return a `number` Impact Run Id that can be used to query for analysis status)

---
### Wait for the Impact to Complete
- Once you have the Impact Run Id, you can query the system to see when it completes
- `GET {{api_domain}}api/v1/impact/status/{{impactRunId}}`
  - Will return a `text` status about the Impact Analysis
  - One of `Unknown`, `New`, `InProgress`, `ReadyForWarehouse`, `Complete`,  or`Error`
- Since this can take a while, it is recommended to create a polling loop to check the status every few minutes until it returns `Complete`

---
### Examine the Results
- Once the `status` of an Impact Run is `Complete`, the results of that Impact can be retrieved

#### Summary Economic Indicators
- `GET {{api_domain}}api/v1/impact/results/SummaryEconomicIndicators/{{impactRunId}}`
  - Returns non-`json` text that is a CSV (comma-delimited values) Summary Report of the Economic Indicators

#### Summary Tax Results
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/{{impactRunId}}`
  - Returns non-`json` text that is a CSV (comma-delimited values) Summary Report of the Tax Results

#### Detailed Economic Indicators
- `GET {{api_domain}}api/v1/impact/results/ExportDetailEconomicIndicators/{{impactRunId}}`
  - Returns non-`json` text that is a CSV (comma-delimited values) Detailed Report of the Economic Indicators

#### Detailed Tax Results
- `GET {{api_domain}}api/v1/impact/results/DetailedTaxes/{{impactRunId}}`
  - Returns non-`json` text that is a CSV (comma-delimited values) Detailed Report of the Tax Results