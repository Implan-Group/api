# ImpactApi - Run Impact Analysis Workflow
- Once a Project has been created and Events and Groups have been added, the Impact Analysis can be run in order to produce results
- [Impact Readme - Run Impact](https://github.com/Implan-Group/api/blob/main/impact/readme.md#run-impact-post)

### 🗈 Notes
- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
	- Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
- Variables required for Endpoint calls will appear inside of double-braces (`{{}}`) and they must be replaced with valid values before the Request is sent
	- _e.g._ `{{api_domain}}` should be replaced with `https://api.implan.com/` for Public Production requests
	- See the [Development Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#development-variables) section of the Readme for more information


---
## 🔽 Find the Project
- There are several ways to search through all the Projects that your User has access to
- The goal is to find:
  - The Project's `Id`, used to run Analysis
  - The Project's `LastImpactRunId`, which is used to retrieve Reports

---
### Project Json
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
### Get All Projects
- If you want to look at all Projects that you created

##### Request
- `GET {{api_domain}}api/v1/impact/project`

##### Response
- Returns an array of `json` Projects (see Project Json above)

---
### Get a Specific Project
- If you want the details for a specific Project

##### Request
- `GET {{api_domain}}api/v1/impact/project/{{projectId}}`

##### Response
- Returns a single Project Json (see above)

---
### Get All Projects Shared With Me
- If you want to look at all Projects that have been shared with you

##### Request
- `GET {{api_domain}}api/v1/impact/project/shared`

##### Response
- Returns an array of `json` Projects (see Project Json above)


---
## 🔽 Execute the Impact
- Once you have located the `Project Id` for the Project you can run an Analysis on it

---
### Impact Run
- Starts an Impact Analysis

##### Request
- `POST {{api_domain}}api/v1/impact/{{projectId}}

##### Response
- Returns an `Impact Run Id` (number) that is used to query for Analysis Status

---
### Impact Status
- Once you have the Impact Run Id, you can query the system to see when it completes
- More complex Analysis can take a while to run. It is recommended to create a polling loop to check the status every few minutes until it returns `Complete`

##### Request
- `GET {{api_domain}}api/v1/impact/status/{{impactRunId}}`

##### Response
  - Will return the Status (text) of the Project's Impact Analysis Run
  - One of `Unknown`, `New`, `InProgress`, `ReadyForWarehouse`, `Complete`,`Error`, or `UserCancelled`

---
### Cancellation
- If the Impact seems to be taking an unusually long time to run or you want to make changes, you can also Cancel a running Impact Analysis

##### Request
- `PUT {{api_domain}}api/v1/impact/cancel/{{impactRunId}}`

##### Response
 - Will return `"Analysis run cancelled."` if the Analysis was successfully stopped


---
## 🔽 Examine the Results
- Once the `status` of an Impact Run is `Complete`, the results of that Impact can be retrieved

---
## 📒 Comma-Delimited Text (CSV) Reports
- All of the Endpoints in this section return a `text` response which is the CSV report itself
- You can save the results to a file with the `.csv` extension and open it with Microsoft Excel or Google Sheets in order to view

---
### Summary Economic Indicators
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#summary-economic-indicators-export--get)

##### Request
- `GET {{api_domain}}api/v1/impact/results/SummaryEconomicIndicators/{{impactRunId}}`

##### Response
 - Will return the CSV report as text

---
### Summary Tax Results
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#summary-taxes-export-get)

##### Request
- `GET {{api_domain}}api/v1/impact/results/SummaryTaxes/{{impactRunId}}`

##### Response
 - Will return the CSV report as text

---
### Detailed Economic Indicators
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#detail-economic-indicators-export-get)

##### Request
- `GET {{api_domain}}api/v1/impact/results/ExportDetailEconomicIndicators/{{impactRunId}}`

##### Response
 - Will return the CSV report as text

---
### Detailed Tax Results
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#detail-taxes-export-get)

##### Request
- `GET {{api_domain}}api/v1/impact/results/DetailedTaxes/{{impactRunId}}`

##### Response
 - Will return the CSV report as text

---
### Estimated Growth Percentage
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#estimated-growth-percentage)

##### Request
- `GET {{api_domain}}api/v1/impact/results/EstimatedGrowthPercentage/{{impactRunId}}`
- A `json` body must be included that helps to filter the response data
```json
{
      "dollarYear": 2024,
      "regions": [{"REGION_1_NAME", "REGION_2_NAME"}],
      "impacts": [{"Direct", "Indirect", "Induced"}],
      "groupNames": [{"GROUP_1_NAME", "GROUP_2_NAME"}],
      "eventNames": [{"EVENT_1_NAME", "EVENT_2_NAME"}],
      "eventTags": [{"EVENTTAG1", "EVENTTAG2"}]
  }
  ```
  - `dollarYear` (number): Required Dollar Year to use when calculating the report
  - `regions` (text array, optional): A list of names of the Regions to include in the report
  - `impacts` (text array, optional): Additional filters on the Impact Type
    - Can only be `Direct`, `Indirect`, or `Induced`
  - `groupNames` (text array, optional): A list of names of the Groups to include in the report
  - `eventNames` (text array, optional): A list of names of the Events to include in the report
  - `eventTags` (text array, optional): A list of Event Tags, only Events with those Tags will be included in the report

##### Response
 - Will return the CSV report as text