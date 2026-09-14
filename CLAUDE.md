# Impact API samples: rules for `sampleCode/` and `impact/workflows/`

This file is the contract for anyone, human or agent, editing the sample code or the workflow docs. The reader-facing orientation is `sampleCode/README.md`.

Sources of truth, in order:

1. The generated OpenAPI 3.1 spec for Impact API v1 in the `ui_api` repository (`C:\git\ui_api`, folder `UiApi/openapi/`), with its Postman collection beside it. It is produced from the controllers, validated against the API Gateway export, and carries request and response schemas, required fields, and every status an endpoint returns. Use the INT build, `ImpactApi_version1.external.int.json`, for the contract: it reflects the error-code corrections that will be in production by the time updated samples are published, so what a sample sees on INT today is what a reader sees on production later. The samples still target the production host, `https://api.implan.com`. Where a sample and the spec disagree, the spec wins.
2. The [wiki](https://github.com/Implan-Group/api/wiki), checked out at `C:\git\github\api.wiki`, for narrative and page names to link.
3. The `External.Api` controllers in `ui_api` when the spec text is ambiguous.

The hand-maintained `IMPLAN-API.postman_collection.json` at this repository's root is older than the generated collection and is not a source of truth for the samples.

One set of workflows, implemented once per language, each version tailored to its language but doing the same thing with the same example data. If a workflow is not in the list in section 5 it does not belong in a language folder, and if it is in the list every language folder must have it.

---

## 1. Rules every sample follows

A language folder that departs from one of these needs a comment saying why.

**Endpoints and authentication**

- Base URL is `https://api.implan.com`. Every endpoint is under `/api/v1/` except authentication.
- Authenticate with `POST /api/auth` and a JSON body of lowercase `username` and `password`. The response body is the token, already prefixed with `Bearer `. Send it as the `Authorization` header on every other request.
- Every language caches the token to a local file and reuses it; requesting a new token on every run is not acceptable, and repeated authentication requests can get an account throttled or banned. The pattern is: load the cached token if the file exists; verify it with one cheap call (`GET /api/v1/region/RegionTypes`); only if there is no file or the verification fails, post credentials, write the new token to the file, and continue. A token is valid for 24 hours. On a 401 mid-run, refresh once and retry the request once. The cache file is `implan_auth.jwt` next to the entry point and is gitignored (`*.jwt` is already in the root `.gitignore`). Never print or log the token. The reference implementation is Python's existing `AuthHelper` (`get_bearer_token`, `_validate_token`, `get_fresh_token`); the R procedural helper's `getImplanAuth` follows the same idea with a timestamp. C# has no cache today and must add one.
- Credentials come from a `.env` file next to the entry point with two variables, `IMPLAN_USERNAME` and `IMPLAN_PASSWORD`. Same names in all three languages. `.env` is gitignored; each folder ships a `.env.example`.

**Identifiers are resolved at run time, never hardcoded**

- United States: take the Industry Set whose `isDefault` is true; its `defaultAggregationSchemeId` is the Aggregation Scheme; the Dataset for that scheme whose `isDefault` is true is the Dataset. Print all three so the reader sees what was chosen.
- Canada and International: filter Aggregation Schemes by `mapCode` (`CAN` or `INTL`) and a description containing `Unaggregated`, take the one with the highest `industrySetId`, then its default Dataset.
- Industries are looked up by code and the description is checked against the expected text; a mismatch stops the workflow with both values printed. Codes differ between families (Full-service restaurants is 509 in 546 Industries and 491 in 528 Industries), which is why the check exists.
- Household Set is the first entry of the chosen scheme's `householdSetIds`.
- Dollar year is the current calendar year, computed when the workflow runs.

**Request shape**

- `GET /api/v1/IndustryCodes/{aggregationSchemeId}` takes no query string; the scheme already implies the Industry Set. Only `GET /api/v1/IndustryCodes` accepts `industrySetId`.
- There is no public single-Industry-Set endpoint. Filter the list from `GET /api/v1/industry-sets` client side.
- `GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}` requires a JSON body even though it is a GET. All five filter arrays (`regions`, `impacts`, `groupNames`, `eventNames`, `eventTags`) must be present; send `[]` for no filter. API Gateway forwards GET bodies. Comment this at the call site.
- Groups must include `dollarYear`; the API has no default and a group without one produces a run that never attaches.
- Titles for projects, events, groups, and combined regions must be unique per user and must not contain `& | ; % * ? ! = ' " ^ #`. Samples use the prefix `ImpactApi Sample - ` plus a timestamp.

**Waiting for the API**

- Impact status: poll `GET /api/v1/impact/status/{runId}` every 15 to 30 seconds. `Complete` means proceed. `Error` and `UserCancelled` are terminal failures. A 404 means the run never attached and is also terminal. Give up after 15 minutes with a message that names the run id.
- Combined-region build: poll `GET /api/v1/region/user/{hashId}` (the single-region endpoint, not the list) every 15 seconds until `modelBuildStatus` is `Complete`; treat `Error` as terminal; give up after 10 minutes.
- Respect the published throttles (Region Models 5 per minute, Industry Codes and Datasets 10 per minute, Batch 6 per minute). Bulk workflows sleep between calls and never issue one status request per region.

**Errors**

- Every non-2xx response carries RFC 9457 problem details. Read `title`, `detail`, `status`, and `traceId`, print them, and stop. Never continue past a failed request, and never let a failure surface as a null-reference or subscript error somewhere else.
- Logging goes to the console and to a `logs/` file (gitignored). Request and response bodies are logged; the `Authorization` header is redacted.

**Housekeeping**

- Every workflow that creates objects ends by printing what it created (project id, event ids, group ids, region hash ids) so the reader can find and delete them in IMPLAN Cloud.
- Each language targets its current release at the time the sample is updated, stated in the folder README with the date it was verified.
- The Instant and Batch APIs are never shown in these samples.

---

## 2. Commenting standard

The code is the tutorial. A reader should be able to follow a workflow file top to bottom without opening the wiki, and should know exactly which wiki page to open when they want more.

- Every file starts with a header comment: what the file is for, which workflow it belongs to, and the wiki page or pages it relies on.
- Every workflow is written as numbered steps, each introduced by a comment that says what the step achieves and why it is needed before the next one.
- Every API call is preceded by a comment giving the HTTP method, the gateway path with placeholders, and the wiki page name. Example: `GET /api/v1/datasets/{aggregationSchemeId}` (wiki: Dataset by Aggregation Scheme).
- Comments explain intent and constraints, not syntax. "We need the default dataset because region hash ids are dataset-specific" is a comment; "loop over datasets" is not.
- Where the API has a quirk the sample works around (GET with a body, the ignored `industrySetId`, the quoted status string some HTTP clients receive), the comment states the quirk plainly so nobody removes the workaround.
- Plain ASCII, Oxford commas, and the wiki's terminology (Aggregation Scheme, Dataset, Industry Set, Region, Group, Event, Impact Run).

---

## 3. README standard for each language folder

Each language README has these sections in this order.

1. **What this is.** Two sentences and a link to `sampleCode/README.md`.
2. **Prerequisites.** The runtime or interpreter, the exact version verified, where to download it, and the one command that proves it is installed. Recommended editor with install link.
3. **Install dependencies.** The exact command, and the manifest file it reads (the `.csproj` at the folder root, `requirements.txt`, or the R package list).
4. **Configure.** Copy `.env.example` to `.env` and fill in the two variables. Say where the token cache and logs are written.
5. **Run.** One command per workflow, in list order, and how to pass a project id to the workflows that need one.
6. **What you should see.** The console output shape for a successful run, and where exported CSV files land.
7. **Troubleshooting.** What 401, 403, 409, 422, 429, and 503 mean from this API and what to do about each; the throttles; the user-regions list returning 503 for accounts with many custom schemes; and that a 503 from `POST /api/auth` usually means either the authentication service is briefly unavailable (wait a minute and retry) or API access has not been enabled on the account (contact the Customer Success Manager), as the IMPLAN Support article "How to Use the IMPLAN API with R: Obtaining Your API Token" explains.
8. **Links.** Wiki home, the wiki pages used, and support.

---

## 4. Shared example data

Same in every language so outputs can be compared side by side.

| Item | Value | Resolved how |
| --- | --- | --- |
| Aggregation Scheme, Dataset, Household Set | default US family | rule in section 1 |
| Industry for output events | code 1, `Oilseed farming` | code plus description check |
| Industry for the restaurant example | `Full-service restaurants` | description lookup, code printed |
| Household income specifications | `10002` (15-30k) and `10005` (50-70k) | from the specification endpoint, checked by code |
| Regions for groups | `Oregon`, `Wisconsin`, `North Carolina` | state children of the top-level region, matched by description |
| Regions to combine | `Lane County, OR` and `Douglas County, OR` | county children, matched by description |
| Event values | Industry Output 1,000,000; Industry Impact Analysis intermediate inputs 500,000, employee compensation 250,000, proprietor income 50,000, employment 4 wage-and-salary plus 1 proprietor; Household Income 25,000 and 125,000 | literals, commented |
| Dollar year | current calendar year | computed |
| Reports downloaded | Summary Economic Indicators, Detailed Economic Indicators, Summary Taxes, Detailed Taxes, Estimated Growth Percentage | fixed set |

---

## 5. Layout, naming, and the workflow list

There are exactly three folders under `sampleCode/`, named for the language and nothing else: `CSharp`, `Python`, and `R`. No sub-project folders, no variant folders. The entry point, the manifest (`.csproj`, `requirements.txt`, or the R package list), the `.env.example`, and the README sit at the folder root.

Every language keeps the same three layers so a reader who knows one folder can navigate the others. The endpoint files are named for the wiki's sidebar sections: Aggregation Schemes, Datasets, Industries, Regions and Regional Data Exports, Impacts with Events, Groups, and Projects, and Impact Results.

| Layer | C# (`CSharp/`) | Python (`Python/`) | R (`R/`) |
| --- | --- | --- | --- |
| Entry point | `Program.cs` | `main.py` | `main.R` |
| Endpoints (one file per wiki section) | `Endpoints/` | `endpoints/` | `endpoints/` |
| Models (request and response shapes) | inside `Endpoints/` | `models/` | `models/` |
| Services (REST, auth, JSON, logging, polling) | `Services/` | `utilities/` | `utilities/` |
| Workflows (one file per workflow) | `Workflows/` | `workflows/` | `workflows/` |
| Configuration | `.env.example` | `.env.example` | `.env.example` |

Naming: the workflow names are the same words in every language, spelled the way that language spells things. C# uses PascalCase files, classes, and methods; Python uses lower_snake_case modules and functions; R follows the tidyverse style guide with lower_snake_case files and functions. Inside each folder the code is written the way a native reader of that language expects, not as a transliteration of another language.

Library choices: C# uses `HttpClient` plus `System.Text.Json` (or the current RestSharp, if kept, at its current release); Python uses `requests` and `python-dotenv`; R uses `httr2` with the native `|>` pipe and `jsonlite`, matching the IMPLAN Support article "How to Use the IMPLAN API with R: Obtaining Your API Token", which is the first thing an R user finds. The R code is plain functions grouped by file, not S4 classes: `req_auth_bearer_token()` for the token (it redacts the token when a request is printed), `req_error()` to turn problem-details bodies into R errors, `req_retry()` for the auth service's transient 503, and `req_throttle()` in the bulk workflows to stay inside the published rate limits.

| # | Workflow | C# | Python | R | Narrative doc |
| --- | --- | --- | --- | --- | --- |
| 1 | Authentication | `AuthenticationWorkflow.cs` | `authentication_workflow.py` | `authentication_workflow.R` | wiki Authentication |
| 2 | Identifiers | `IdentifiersWorkflow.cs` | `identifiers_workflow.py` | `identifiers_workflow.R` | `impact/workflows/Identifiers.md` (new) |
| 3 | Regions | `RegionsWorkflow.cs` | `regions_workflow.py` | `regions_workflow.R` | `impact/workflows/Regions.md` |
| 4 | CombineRegions | `CombineRegionsWorkflow.cs` | `combine_regions_workflow.py` | `combine_regions_workflow.R` | `impact/workflows/CombineRegions.md` |
| 5 | CreateProject | `CreateProjectWorkflow.cs` | `create_project_workflow.py` | `create_project_workflow.R` | `impact/workflows/CreateProject.md` |
| 6 | MultiEventToMultiGroup | `MultiEventToMultiGroupWorkflow.cs` | `multi_event_to_multi_group_workflow.py` | `multi_event_to_multi_group_workflow.R` | `impact/workflows/MultiEventToMultiGroup.md` |
| 7 | RunImpactAnalysis | `RunImpactAnalysisWorkflow.cs` | `run_impact_analysis_workflow.py` | `run_impact_analysis_workflow.R` | `impact/workflows/RunImpactAnalysis.md` |
| 8 | BulkFromCsv | `BulkFromCsvWorkflow.cs` | `bulk_from_csv_workflow.py` | `bulk_from_csv_workflow.R` | `impact/workflows/BulkFromCsv.md` (new) |
| 9 | RegionalExports | `RegionalExportsWorkflow.cs` | `regional_exports_workflow.py` | `regional_exports_workflow.R` | `impact/workflows/RegionalExports.md` (new) |
| 10 | ImportEvents | `ImportEventsWorkflow.cs` | `import_events_workflow.py` | `import_events_workflow.R` | `impact/workflows/ImportEvents.md` (new) |
| 11 | MrioProject | `MrioProjectWorkflow.cs` | `mrio_project_workflow.py` | `mrio_project_workflow.R` | `impact/workflows/MrioProject.md` (new) |
| 12 | AdvancedEvents | `AdvancedEventsWorkflow.cs` | `advanced_events_workflow.py` | `advanced_events_workflow.R` | `impact/workflows/AdvancedEvents.md` (new) |

Workflows 1 through 7 are the core set. Workflows 8 through 12 are the extended set: 8 comes from the former R procedural script, 9 from the former Python download scripts, and 10 through 12 were added on 2026-09-14 because each traces to a current IMPLAN Support topic (the Event Template, MRIO, and Contribution Analysis and Spending Pattern events) that no sample covered. Adding a language means one more column in these two tables, one folder with these layers, and one README written to section 3. Adding a workflow means adding it to every language and to this table.

The wiki's Getting Started page is a ten-step process; the core workflows are that process cut into runnable pieces: step 1 is Authentication; steps 2 and 4 are Identifiers; step 3 is Regions and CombineRegions; steps 5 through 7 are CreateProject and MultiEventToMultiGroup; steps 8 through 10 are RunImpactAnalysis.

---

## 6. Workflow specifications

Each entry gives the goal, the steps, the endpoints with their wiki page, what the workflow needs, what it produces, and what "done" looks like. Endpoint paths are the public gateway paths. Wiki links are `https://github.com/Implan-Group/api/wiki/` plus the page name with spaces as hyphens.

### 1. Authentication

Goal: obtain a bearer token once, cache it, and prove it works.

Steps: read `.env`; if a cached token exists, verify it; otherwise post credentials, store the token, verify it. Print only "authenticated" and the cache location.

| Endpoint | Wiki page |
| --- | --- |
| `POST /api/auth` | Authentication |
| `GET /api/v1/region/RegionTypes` (verification only) | Get Region Types |

Needs: `.env`. Produces: token cache file. Done when: a second run reuses the cached token without posting credentials.

### 2. Identifiers

Goal: show how every id the other workflows need is discovered from the API, and print the resolved values.

Steps: list Industry Sets and pick the default; list Aggregation Schemes and pick the default scheme for that set; list Datasets for the scheme and pick the default; list Industry Codes for the scheme and show the code-plus-description check; list Region Types; then apply the Canada and International rule and print the resolved scheme, dataset, and household set for `CAN` and `INTL` as well, so the three map codes sit side by side. The Canada considerations doc in `impact/workflows` is folded into this workflow's narrative rather than kept separate.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/industry-sets` | Get Industry Sets |
| `GET /api/v1/aggregationSchemes` | Aggregation Schemes |
| `GET /api/v1/datasets/{aggregationSchemeId}` | Dataset by Aggregation Scheme |
| `GET /api/v1/IndustryCodes/{aggregationSchemeId}` | Industry Codes by Aggregation Scheme |
| `GET /api/v1/region/RegionTypes` | Get Region Types |

Needs: token. Produces: a printed table of the resolved ids. Done when: the printed scheme, dataset, and household set match what IMPLAN Cloud shows as current.

### 3. Regions

Goal: navigate the region hierarchy and the user's own regions.

Steps: top-level region for the default scheme and dataset; its state children; one state's county children filtered with `regionTypeFilter`; a single region by hash id; the user's combined and customized regions for the scheme and dataset; one user region by hash id.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}` | Regions - Top Level |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children` and `.../{hashId}/children?regionTypeFilter=` | Regional Children |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/{hashId}` | Get Region by Id |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/user` | Get User Regions by Aggregation Scheme |
| `GET /api/v1/region/user/{hashId}` | Get User Region |

Needs: token, ids from workflow 2. Produces: printed region summaries. Done when: Oregon, Wisconsin, and North Carolina are found by description and their hash ids printed.

### 4. CombineRegions

Goal: combine two counties into one region and wait for its model to build.

Steps: find the two counties by description; post the combined build with `hashIds` and a unique description; poll the single user-region endpoint until `Complete`; print the new hash id.

| Endpoint | Wiki page |
| --- | --- |
| `POST /api/v1/region/build/combined/{aggregationSchemeId}` | Combine Regions |
| `GET /api/v1/region/user/{hashId}` (polling) | Get User Region |

Needs: token, ids. Produces: a built combined region. Done when: the poll returns `Complete` within the timeout and the region appears under the user's regions.

### 5. CreateProject

Goal: the minimum path from nothing to a runnable project.

Steps: create the project with the resolved scheme and household set; list the event types valid for it; add one Industry Output event and one Industry Impact Analysis event for Oilseed farming; find Oregon; add one group for Oregon with both events and the current dollar year; read the project back.

| Endpoint | Wiki page |
| --- | --- |
| `POST /api/v1/impact/project` | Create Project |
| `GET /api/v1/impact/project/{projectId}/eventtype` | Get Event Types |
| `POST /api/v1/impact/project/{projectId}/event` | Create Event |
| `POST /api/v1/impact/project/{projectId}/group` | Create Group |
| `GET /api/v1/impact/project/{projectId}` | Get Project |

The workflow takes an optional map code, default `US`. With `CAN` it resolves the Canadian scheme and dataset, uses a Canadian industry and province, and otherwise runs the same steps; with `INTL` it uses the country children endpoint for the region step, because international schemes have no top-level region.

Needs: token, ids. Produces: a project id, two event ids, one group id, all printed. Done when: workflow 7 can run the project.

### 6. MultiEventToMultiGroup

Goal: the same events applied to several regions, the common "compare states" shape.

Steps: take an existing empty project id (or create one with the workflow 5 code); read the Household Income specifications and check codes 10002 and 10005; add one Industry Output event for Full-service restaurants and two Household Income events; find the three states; add one group per state containing all three events.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/impact/project/{projectId}/eventtype/HouseholdIncome/specification` | Get Event Specifications |
| `POST /api/v1/impact/project/{projectId}/event` | Create Event |
| `POST /api/v1/impact/project/{projectId}/group` | Create Group |

Needs: token, ids, a project id. Produces: three event ids and three group ids. Done when: the project shows three groups with three events each.

### 7. RunImpactAnalysis

Goal: run a project, wait correctly, and download every standard report.

Steps: list the user's projects and shared projects, read the target project; start the run; poll status with the timeout and terminal-state rules; show how to cancel (code present, not executed by default); download the five reports to `reports/{project title}/` as `.csv`, passing the current dollar year where the endpoint accepts one; print the run id and the folder.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/impact/project`, `GET /api/v1/impact/project/shared`, `GET /api/v1/impact/project/{projectId}` | Get Projects, Get Shared Projects, Get Project |
| `POST /api/v1/impact/{projectId}` | Run Impact Analysis |
| `GET /api/v1/impact/status/{runId}` | Get Impact Status |
| `PUT /api/v1/impact/cancel/{runId}` | Cancel Impact |
| `GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}` | Results - Summary Economic Indicators |
| `GET /api/v1/impact/results/ExportDetailEconomicIndicators/{runId}` | Results - Detailed Economic Indicators |
| `GET /api/v1/impact/results/SummaryTaxes/{runId}` | Results - Summary Taxes |
| `GET /api/v1/impact/results/DetailedTaxes/{runId}` | Results - Detailed Taxes |
| `GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}` with JSON body | Results - Estimated Growth Percentage |

Needs: token, a project id with at least one group. Produces: five CSV files that open in a spreadsheet. Done when: all five files exist and the first line of each is a CSV header, not JSON.

### 8. BulkFromCsv (extended)

Goal: drive many builds and runs from input files, the way an analyst batches work. Ported from the former R procedural script.

Steps: read `state_based.csv`, `county_based.csv`, and `demo_events.csv`; resolve each FIPS code to a region by walking the state and county children (cached locally); create or reuse a combined region per model name and wait for each build; create or reuse a folder; for each model create a project in the folder, add Industry Output and Commodity Output events from the CSV, add one group, run, wait, and download the four indicator and tax reports; finally create one "all models" project with a group per region. Sleep between calls to stay inside the throttles.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/impact/folder`, `POST /api/v1/impact/folder` | Projects (folders) |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children`, `.../{hashId}/children` | Regional Children |
| `POST /api/v1/region/build/combined/{aggregationSchemeId}`, `GET /api/v1/region/user/{hashId}` | Combine Regions, Get User Region |
| `POST /api/v1/impact/project` with `folderId` | Create Project |
| `POST /api/v1/impact/project/{projectId}/event` (`IndustryOutput`, `CommodityOutput`) | Create Event |
| Group, run, status, and the four CSV reports as in workflows 5 and 7 | as above |

Needs: token, the three CSV files (shipped with the sample). Produces: one folder of projects in IMPLAN Cloud and one results folder per run locally. Done when: every project in the folder has a completed run and a results folder.

### 9. RegionalExports (extended)

Goal: download a regional data export for many regions without one status request per region. Ported from the former Python download scripts. The export is a parameter (default `RegionOverviewIndustries`, plus the single-file GAMS export), so the other exports under the wiki's Regional Data Exports section (environment, occupation, multipliers, SAM tables) can be pulled by naming them, without new workflows.

Steps: optionally read a list of custom regions to combine (CSV with a region name and FIPS codes) and build them as in workflow 4; list the target regions (all MSAs, or all counties); check which are already built with one call; build the rest with `build-and-return` and wait; download the Region Overview Industries CSV and the single-file GAMS export per region into `reports/`, skipping files that already exist, and pausing between requests to respect the throttles.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/children?regionTypeFilter=` | Regional Children |
| `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/built` | Get Built Regions |
| `POST /api/v1/region/build-and-return/{aggregationSchemeId}` | Build and Return Regions |
| `GET /api/v1/regions/export/{aggregationSchemeId}/RegionOverviewIndustries?hashId=` | Regional Data Exports |
| `GET /api/v1/regions/export/{aggregationSchemeId}/region-general-algebraic-modeling-single-file?hashId=` | Region Data - GAMS |

Needs: token, ids, optional custom-region CSV. Produces: one CSV and one `.gms` per region. Done when: a rerun downloads nothing new and reports the count already present.

### 10. ImportEvents (extended)

Goal: populate a project from the official IMPLAN Event Template workbook instead of one event call at a time. This is how analysts already move work from spreadsheets into IMPLAN Cloud, and the API accepts the same file.

Steps: create an empty project with the workflow 5 code; upload the filled template that ships with the sample (`data/event_template_us528.xlsx`: two Industry Output events on the Industry sheet, each with an event tag; one group on the Groups sheet identified by FIPS code; the assignments on the Group Events sheet) as a multipart form upload in a field named `excelFile`; on a 400, print the validation details the API returns, because the template is strict about formats; read back the project's events and groups and print their ids. The template family must match the project's Industry Set (US 528, US 546, Canada 235 or 236, International); the sample downloads nothing, it ships the filled copy and links the blank ones.

| Endpoint | Wiki page |
| --- | --- |
| `POST /api/v1/impact/project` | Create Project |
| `POST /api/v1/impact/project/import/{projectId}` (multipart, field `excelFile`) | Import Events |
| `GET /api/v1/impact/project/{projectId}/event` | Get Events |
| `GET /api/v1/impact/project/{projectId}/group` | Groups |

Needs: token, ids, the shipped workbook. Produces: a project with the workbook's events and groups, ids printed. Done when: the read-back lists match the workbook and workflow 7 can run the project. Support reference: "Using the Event Template".

### 11. MrioProject (extended)

Goal: multi-regional input-output analysis, where an event in one region produces effects in another linked region. No earlier sample ever set `isMrio`.

Steps: resolve ids; find Oregon and Wisconsin and check `isMrioAllowed` on both; create the project with `isMrio` true; add one Industry Output event for Oilseed farming; add a group for Oregon containing the event and a group for Wisconsin with no events, so anything reported for Wisconsin is spillover from Oregon (if the API refuses an empty group at run time, give Wisconsin a second, much smaller event and say so in the comment; confirm during implementation); run with the workflow 7 code; download Summary Economic Indicators twice, once filtered to Oregon and once to Wisconsin, and print the two totals side by side.

| Endpoint | Wiki page |
| --- | --- |
| `POST /api/v1/impact/project` with `isMrio: true` | Create Project |
| `POST /api/v1/impact/project/{projectId}/event` | Create Event |
| `POST /api/v1/impact/project/{projectId}/group` (twice) | Create Group |
| `POST /api/v1/impact/{projectId}`, `GET /api/v1/impact/status/{runId}` | Run Impact Analysis, Get Impact Status |
| `GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?regions=` | Results - Summary Economic Indicators |

Needs: token, ids. Produces: a completed MRIO run and two filtered CSVs. Done when: the Wisconsin-filtered report is non-empty although Wisconsin had no direct event. Support reference: "MRIO: Introduction to Multi-Regional Input-Output Analysis".

### 12. AdvancedEvents (extended)

Goal: the two event types analysts reach for after Industry Output, plus event tags and tag-filtered results.

Steps: create a project with the workflow 5 code; add an Industry Contribution Analysis event (`impactEventType` `IndustryContributionAnalysis`, Full-service restaurants, `output` 1,000,000, `isOutputPercentage` false, tag `contribution`); fetch the default Industry spending pattern for Oilseed farming with the resolved dataset, change one commodity's coefficient and mark it `isUserCoefficient`, and add an Industry Spending Pattern event (`impactEventType` `IndustrySpendingPattern`, `output` 1,000,000, `spendingPatternValueType` `Output`, `spendingPatternDatasetId` the resolved dataset, `spendingPatternCommodities` the edited list, tag `spending`); add one group for Oregon with both events; run with the workflow 7 code; download Summary Economic Indicators filtered by `eventTags=contribution` and again by `eventTags=spending`, and Estimated Growth Percentage with `eventTags` in its body; print which events each report contains.

| Endpoint | Wiki page |
| --- | --- |
| `GET /api/v1/impact/project/{projectId}/eventtype` | Get Event Types |
| `GET /api/v1/impact/spending-patterns/{aggregationSchemeId}/Industry/{industryCode}?datasetId=` | Spending Pattern by Id |
| `POST /api/v1/impact/project/{projectId}/event` (twice) | Create Event |
| `POST /api/v1/impact/project/{projectId}/group` | Create Group |
| `POST /api/v1/impact/{projectId}`, `GET /api/v1/impact/status/{runId}` | Run Impact Analysis, Get Impact Status |
| `GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}?eventTags=` | Results - Summary Economic Indicators |
| `GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}` with `eventTags` in the JSON body | Results - Estimated Growth Percentage |

Needs: token, ids. Produces: a completed run and two tag-filtered reports. Done when: each filtered report contains only its tagged event. Support references: "Industry Contribution Events", "Industry Spending Pattern Events", "Event Tags".

---

## 7. Endpoints the samples deliberately do not cover

Update, delete, duplicate, share, and transfer for projects, events, and groups; folder sharing; Institutional, Household, and Custom spending patterns; Industry Impact Analysis (Custom) and the International variants; custom aggregation schemes; the Instant and Batch APIs. They are documented in the wiki. Adding one means adding it to all languages and to section 5.
