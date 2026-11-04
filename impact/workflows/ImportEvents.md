# ImpactApi - Import Events Workflow
- Fills a project from IMPLAN's Event Template workbook in one upload. It is the same file the Upload Template button takes in IMPLAN Cloud, so you can analyze your own events without changing any code.
- [Import Events](https://github.com/Implan-Group/api/wiki/Import-Events)
- Support: [Using the Event Template](https://support.implan.com/hc/en-us/articles/360040713754), which describes every column on every sheet

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 Fill in the template
- The workflow creates its project on the current default US Aggregation Scheme, so the workbook must be the blank template for that scheme's Industry Set. The `identifiers` workflow, and Step 2 of this one, print which Industry Set that is. The templates for other Industry Sets are rejected
- The blank templates, by Industry Set:
	- [US 528](https://support.implan.com/hc/article_attachments/31846310653723)
	- [US 546](https://support.implan.com/hc/article_attachments/28726382924059)
	- [Canada 235](https://support.implan.com/hc/article_attachments/34805745157147)
	- [Canada 236](https://support.implan.com/hc/article_attachments/49510601287323)
	- [International](https://support.implan.com/hc/article_attachments/28726664391451)
- The template is strict
	- Each event type has its own sheet. The Industry sheet is the simplest: an Event Name, a Specification (the industry code), and one value such as Output
	- Keep the formats the blank template shows: a `100%` cell means 100%, not 100
	- Give every event a value, and leave no formulas in the cells
	- Check that every sheet you are not using is empty. A row left on any sheet is imported as an event, and the US 528 blank these samples were built from had a test row on its Industry Spending Pattern sheet
	- Keep one upload to about 500 events
- Groups are optional
	- Fill the Groups sheet with a FIPS code, a data year, and a dollar year to have the upload create groups. A state's FIPS code is five digits there, such as `41000` for Oregon; a county's is five digits either way, such as `41019`
	- If you fill the Groups sheet, fill the Group Events sheet too. The upload does not assign events to groups on its own, and a group with no events cannot be run
	- Leave both sheets empty to import only the events, and add groups afterwards with [Create Group](https://github.com/Implan-Group/api/wiki/Create-Group) or in IMPLAN Cloud

---
## 🔽 Run it
- Run the `import-events` workflow from the C#, Python, or R folder with `--workbook` and the path to your file. Each folder's README gives the exact command. Without `--workbook` it uploads the example in that folder's `data/event_template.xlsx`, a fictional timber panel plant in Douglas County, Oregon
- Every run creates a new project before uploading. If the upload is refused, the error message names what to fix, and the empty project it created stays in your account; delete it in IMPLAN Cloud
- When the groups have events, the workflow finishes by printing the `run-impact-analysis` command that runs the project

---
## 🔽 What it does
1. Checks that the workbook exists, and prints where to download a blank template if it does not
2. Resolves the current default US Aggregation Scheme, Dataset, and Household Set
3. Creates an empty project ([Create Project](https://github.com/Implan-Group/api/wiki/Create-Project))
4. Uploads the workbook as a multipart form, in a field named `excelFile` ([Import Events](https://github.com/Implan-Group/api/wiki/Import-Events))
5. Reads back the events and groups the upload created ([Get Events](https://github.com/Implan-Group/api/wiki/Get-Events), [Groups](https://github.com/Implan-Group/api/wiki/Groups))
