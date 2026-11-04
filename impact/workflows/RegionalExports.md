# ImpactApi - Regional Exports Workflow
- Downloads one regional data export, such as a Region's industry overview, for every Region of a type: every MSA, every county, or every state. An export describes a Region's economy as it already is, so it needs no project and no impact run, only a built Region.
- [Regional Data Exports](https://github.com/Implan-Group/api/wiki/Regional-Data-Exports)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 Choose what to download
- `--region-type` picks the Regions: `Msa` by default, or `County`, `State`, and the other values [Get Region Types](https://github.com/Implan-Group/api/wiki/Get-Region-Types) lists
- `--export-name` picks the export: `RegionOverviewIndustries` by default ([Region Data - Overview Industries](https://github.com/Implan-Group/api/wiki/Region-Data---Overview-Industries)), or `region-general-algebraic-modeling-single-file` for the single-file GAMS export ([Region Data - GAMS](https://github.com/Implan-Group/api/wiki/Region-Data---GAMS)), saved as `.gms`
	- Any other export that needs only the Region works the same way. Use the last segment of its route, such as `StudyAreaDataIndustrySummary` or `study-area-data-aggregate-ixi-sam`. Routes are case-sensitive, so copy the name exactly from its wiki page
	- The occupation, environment, and multiplier exports also need a JSON body or another parameter, which this workflow does not send
- `--limit` caps how many Regions are processed. It is 10 by default so a first run is short; `--limit 0` processes them all
- Each folder's README gives the exact command

---
## 🔽 Run it
- Run the `regional-exports` workflow from the C#, Python, or R folder
- The files land in `reports/`, in a folder named for the export, the Aggregation Scheme, and the Dataset, one file per Region named for its description
- A file already on disk is skipped, so running again resumes a long job instead of starting over, and picks up Regions that were still building last time
- It holds every request to five a minute, the published limit for Region model builds. Listing Regions and downloading exports do not count against that limit, but holding everything to it keeps the workflow simple and safely inside it. Every county in the country takes many hours at that pace

---
## 🔽 What it does
1. Resolves the current default US Aggregation Scheme and Dataset
2. Lists the Regions of the chosen type with one call. Each Region in that list carries its `modelBuildStatus`, so the list and the build state cost one request between them instead of one status request per Region ([Regional Children](https://github.com/Implan-Group/api/wiki/Regional-Children))
3. Requests models for the Regions that are not built, 25 at a time, waiting 30 seconds after each batch ([Build and Return Regions](https://github.com/Implan-Group/api/wiki/Build-and-Return-Regions))
4. Downloads the export for each Region by its HashId ([Regional Data Exports](https://github.com/Implan-Group/api/wiki/Regional-Data-Exports))
	- A `409 Conflict` titled "Model not built" means the Region's model has not finished building yet. It is counted as not ready, not as a failure, and the next run picks it up
5. Prints how many files it downloaded, how many were already on disk, and how many were not ready
