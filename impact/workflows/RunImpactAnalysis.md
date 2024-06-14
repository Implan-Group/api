# Impact API - Run Impact Analysis Workflow
- This document is a supplement to the [Impact ReadMe](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Further detail on additional workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us)

### Notes:
- All API Endpoints require a valid JWT Bearer Token ([JWT.IO](https://jwt.io/))
  -	Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section of the primary Readme to review authentication steps
- Variables for endpoints will appear inside of double-braces, those must be replaced with valid values before execution
  - e.g. `{{api_domain}}` should be replaced with `https://api.implan.com/`
  - See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information

---
# Workflow Overview
- Once a Project has been created and Events and Groups have been added, the Impact Analysis can be run in order to produce results
- [Impact Readme - Run Impact](https://github.com/Implan-Group/api/blob/main/impact/readme.md#run-impact-post)

---
## Find the Project
- There are several ways to search through all the Projects that your User has access to
- The goal is to find:
  - The Project's `Id`, used to run Analysis
  - The Project's `LastImpactRunId`, which is used to retrieve Reports

### Get All Projects
- If you want to look at all Projects that you created
- `GET {{api_domain}}api/v1/impact/project`
  - Returns a `json` array of Projects

### Get a Specific Project
- If you want the details for a specific Project
- `GET {{api_domain}}api/v1/impact/project/{{projectId}}`
  - Returns the Project that has the given Project Id (if one exists)

### Get All Projects Shared With Me
- If you want to look at all Projects that have been shared with you
- `GET {{api_domain}}api/v1/impact/project/shared`
  - Returns a `json` array of Projects

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


---
### Run the Impact
- Once you have located the Project Id for the Project you can run an Analysis on that Project
- `POST {{api_domain}}api/v1/impact/{{projectId}}`
  - Will return a Impact Run Id (number) that can be used to query for Analysis Status
  

---
### Wait for the Impact to Complete
- Once you have the Impact Run Id, you can query the system to see when it completes
- `GET {{api_domain}}api/v1/impact/status/{{impactRunId}}`
  - Will return a `text` status about the Impact Analysis
  - One of `Unknown`, `New`, `InProgress`, `ReadyForWarehouse`, `Complete`,`Error`, or `UserCancelled`
- Since this can take a while, it is recommended to create a polling loop to check the status every few minutes until it returns `Complete`

#### Cancellation
- If the Impact seems to be taking an unusually long time to run or you want to make changes, you can also Cancel a running Impact Analysis
- `PUT {{api_domain}}api/v1/impact/cancel/{{impactRunId}}`
  - Will return `"Analysis run cancelled."` if the Analysis was successfully stopped

---
## Examine the Results
- Once the `status` of an Impact Run is `Complete`, the results of that Impact can be retrieved

---
### Comma-Delimited Text (CSV) Reports
- All of the EndPoints in this section return a `text` response which is the CSV report itself

#### Summary Economic Indicators
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#summary-economic-indicators-export--get)
- `GET {{api_domain}}api/v1/impact/results/SummaryEconomicIndicators/{{impactRunId}}`

#### Summary Tax Results
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#summary-taxes-export-get)
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/{{impactRunId}}`

#### Detailed Economic Indicators
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#detail-economic-indicators-export-get)
- `GET {{api_domain}}api/v1/impact/results/ExportDetailEconomicIndicators/{{impactRunId}}`

#### Detailed Tax Results
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#detail-taxes-export-get)
- `GET {{api_domain}}api/v1/impact/results/DetailedTaxes/{{impactRunId}}`


#### Estimated Growth Percentage
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#estimated-growth-percentage)
- `GET {{api_domain}}api/v1/impact/results/EstimatedGrowthPercentage/{{impactRunId}}`
  - A `json` body must be included that helps to filter the response data
  ```json
  {
      "dollarYear": 2024,
      "regions": [{"Region1Name", "Region2Name"}],
      "impacts": [{"Direct", "Indirect", "Induced"}],
      "groupNames": [{"Group1Name", "Group2Name"}],
      "eventNames": [{"Event1Name", "Event2Name"}],
      "eventTags": [{"EventTag1", "EventTag2"}]
  }
  ```
  - `dollarYear` (number): Required Dollar Year to use when calculating the report
  - `regions` (text array, optional): A list of names of the Regions to include in the report
  - `impacts` (text array, optional): Additional filters on the Impact Type
    - Can only be `Direct`, `Indirect`, or `Induced`
  - `groupNames` (text array, optional): A list of names of the Groups to include in the report
  - `eventNames` (text array, optional): A list of names of the Events to include in the report
  - `eventTags` (text array, optional): A list of Event Tags, only Events with those Tags will be included in the report