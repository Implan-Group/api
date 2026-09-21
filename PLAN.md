# IMPLAN Impact API sample workflows: full review

Date: 2026-09-14
Repo reviewed: `C:\git\github\github_api` at `a15e312` (https://github.com/Implan-Group/api)
Backend used as ground truth: `C:\git\ui_api` at `d9efcc35` (`main`), project `External.Api` (Impact API v1)
Reviewer: Claude, at Timothy Jay's request.

**Where this stands (resume here).** See section 16, which is the current state. Sections 1 through 15 are the original review and the decisions that came out of it; they are kept as the record of why the rebuild looks the way it does, and are no longer a description of the tree.

---

## 1. Verdict

None of the seven sample folders runs end to end as shipped. Every folder has at least one blocker that is independent of API drift, and every folder also carries stale identifiers and at least one wrong API usage.

| Folder | Runs as shipped? | Blockers | Headline |
| --- | --- | --- | --- |
| `sampleCode/CSharp` | No | 3 | Compiles (0 errors, 23 warnings). Debug build never authenticates. `CreateProjectWorkflow` throws on an industry-set lookup that no longer matches. `Program.cs` chains a workflow that needs a real project GUID. |
| `Python - General` | No | 3 | Imports and compiles clean. Report CSVs are written as Python byte literals. Industry code 509 is the wrong industry for scheme 14. Deserializing an Industry Impact Analysis event fails on a field the API now returns. |
| `Python - GAMS Download` | Probably, slowly | 0 | Structurally sound. Dead code, a double fetch of all counties, and one status GET per county before any download. |
| `Python - Regional Overview Download` | Probably, slowly | 0 | Same design as GAMS. One status GET per MSA. Credentials as literals in `main.py`. |
| `R - Object Oriented` | No (static analysis) | 4 | Unset S4 slots serialize as `[]` and `{}` and will be rejected. Class-name collision on `Event`. Three files make API calls when sourced. Hardcoded pre-reorg path. Prints the bearer token on every call. |
| `R - Procedural` | Closest to working (static analysis) | 0 | No HTTP error handling on create or run. Status loop ignores `Error` and then downloads results of a failed run. |
| `R - Updated` | No (static analysis) | 4 | `program.R` uses `path` before it exists. Demo script sources a file that is not in the repo. Two workflows reference constants nothing defines. Depends on files that only exist in `R - Object Oriented`. |
| `impact/workflows/*.md` | n/a | n/a | Invalid JSON in three docs, one wrong field name, broken anchors in every doc, stale IDs. |

Recommendation in one sentence: keep C#, `Python - General`, and one R implementation built on the Procedural helper, fold the two Python download scripts into `Python - General` as workflow examples, delete `R - Object Oriented` and `R - Updated` once their scenarios are ported, then fix the blockers and stale IDs listed below and run each folder end to end once. Section 13 has the ordered plan and section 14 has the questions I need answered first.

---

## 2. What I checked, and what I did not

Evidence labels used throughout:

- **[build]**: compiled or linted locally.
- **[live]**: read-only call through the IMPLAN MCP server on 2026-09-14. Correction added the same day: `health_check` reports that this session's MCP server is `IMPLAN DEV`, environment `dev`, loading `ImpactApi_version1.external.int.json`, so every [live] value came from the INT environment, not production. INT is expected to carry the same reference data (schemes, datasets, industry sets, industry codes) as production, but that is unverified until the Python step-1 run hits `https://api.implan.com` with real credentials. Treat [live] as "observed on INT".
- **[backend]**: read from `External.Api` controllers, DTOs, `OpenApi/route-map.json`, or the gateway export.
- **[inferred]**: framework or library behavior reasoned from source, not observed. Each one names what would close it.
- **[static]**: R code read without an interpreter. R is not installed on this machine.

Done:

- Read every file under `sampleCode/` (C#, three Python folders, three R folders), `impact/workflows/*.md`, the sample readmes, and the relevant parts of `impact/readme.md`.
- Built the C# project in a scratch copy with the .NET 10 SDK (target `net8.0`): 0 errors, 23 warnings [build].
- Compiled every Python file with Python 3.14, ran pyflakes in a scratch venv, and imported every `Python - General` module [build].
- Compared every client model to the current backend DTO (`ProjectModel`, `GroupModel`, `GroupEventModel`, `EventModel` and subtypes, `ExternalRegionCard`, `RegionCard`, `CombinedBuildRequest`, `ImpactResultsExportRequest`, `ExternalAggregationScheme`, `ApiDataset`, `IndustrySet`) [backend].
- Mapped every URL the samples call to `route-map.json` and the gateway export [backend].
- Pulled live aggregation schemes, datasets for schemes 8, 14, 12, and 13, industry sets, industry codes for schemes 8 and 14, region types, and the state children for scheme 14 [live].

Not done:

- No end-to-end run against the API. The MCP server holds the credentials, so I could not drive the samples' own HTTP clients. Every "would fail at runtime" claim below is either [build], [backend], or [inferred], and is labeled.
- No R execution. All R findings are [static].
- The Postman collection, the legacy `impact/readme.md`, the `batch/` docs, and the Google Sheets pages were not reviewed beyond incidental observations (section 12).

---

## 3. Ground truth snapshot

Every value marked [live] in this section was read from the INT environment through the DEV MCP server (see the label definitions in section 2). Confirm against production during the first Python run before treating the industry-set descriptions, default dataset ids, and the 491/509 code difference as production facts.

### 3.1 Aggregation schemes and datasets [live]

| Scheme | Description | Industry set | Household sets | Default dataset | Note |
| --- | --- | --- | --- | --- | --- |
| 8 | 546 Unaggregated | 8 | [1] | 96 (2022) | Older US family. Used by all C# and R OO/Updated workflows. |
| 14 | 528 Unaggregated | 12 (the only `isDefault: true` industry set) | [1] | 124 (2024) | Current US family. Samples that use it hardcode dataset 98 (2023), which is still valid but no longer default. |
| 12 | 235 Unaggregated Canada | 10 | [4] | 100 (2021) | Superseded by scheme 17. |
| 17 | 236 Unaggregated Canada | 13 | [7] | not queried | Latest Canada. |
| 13 | 46 Unaggregated International | 11 | [5] | 95 (2020) | Superseded by scheme 18. |
| 18 | 51 Unaggregated International | 14 | [8] | not queried | Latest International. |

Industry set descriptions are now `546 Industries (US)`, `528 Industries (latest US)`, `235 Industries (Canada)`, `236 Industries (latest Canada)`, `46 Industries (International)`, and `51 Industries (latest International)`. Nothing is described as plain `546 Industries` any more.

### 3.2 Industry codes the samples depend on [live]

| Code | Scheme 8 (546) | Scheme 14 (528) |
| --- | --- | --- |
| 1 | Oilseed farming | Oilseed farming |
| 3 | Vegetable and melon farming | Vegetable and melon farming |
| 491 | Nursing and community care facilities | Full-service restaurants |
| 509 | Full-service restaurants | Federal electric utilities |

### 3.3 Other facts the findings rely on

- Region type names are `Country`, `State`, `Msa`, `County`, `CongressionalDistrict`, `Zipcode` [live]. Query-string enum binding is case-insensitive, so `COUNTY` also works, but `Congressional District` with a space does not.
- The gateway exposes both `POST /auth` and `POST /api/auth`, wired to the same integration [backend, gateway export]. The wiki documents `/api/auth`.
- `GET /api/v1/IndustryCodes/{aggregationSchemeId}` has no `industrySetId` parameter; the query string is ignored [backend, `IndustryCodesController.GetIndustryCodesByAggregationSchemeAsync`].
- `GET /api/v1/industry-sets/{industrySetId}` is marked `[ApiExplorerSettings(IgnoreApi = true)]` with the comment "gateway exposes only the industry-sets list". The gateway export confirms only `/api/v1/industry-sets` exists [backend].
- `GET /api/v1/impact/status/{RunId}` returns `ActionResult<string>`. The published spec lists both `text/plain` and `application/json` for the 200 [live, `describe_api_endpoint`]. With `RespectBrowserAcceptHeader` left at its default, MVC ignores an `Accept` header that contains `*/*` and picks the first formatter that can write a string, which is `text/plain`. A client whose `Accept` header lacks `*/*` gets a JSON string with quotes. RestSharp sends no `*/*` (quoted `"Complete"`); `requests` and `httr` send `*/*` (bare `Complete`) [inferred; close it by capturing one status response per client].
- `GET /api/v1/impact/results/EstimatedGrowthPercentage/{RunId}` requires a JSON body of type `ImpactResultsExportRequest`; all five filter arrays are marked required and must be sent as `[]` [backend, live spec].
- The four CSV result endpoints take optional `year`, `regions`, `impacts`, `groups`, `events`, and `eventTags` query parameters. When `year` is omitted the dollar year falls back to the user's preference or the current calendar year [backend].
- `GroupModel.DollarYear` has no server default; a group saved without one produces a run id that never attaches [backend, XML doc]. All samples do send it.
- Combined-region builds return `modelBuildStatus: "New"`; the backend doc recommends polling `GET /api/v1/region/user/{hashId}` rather than the list [backend, `BuildCombinedController` remarks]. The list endpoint `GET /api/v1/region/{agg}/{ds}/user` returned HTTP 503 when I called it for scheme 14 during this review [live]. The `RegionUserController` remarks document that 503 for users with many custom schemes.
- `ExternalRegionCard` (returned by region reads, children, user regions, and the combined build) now includes `sgcFullerCode` [backend, live]. `RegionCard` (returned by `build-and-return`) is a richer shape that also carries `modelYearDescription`, `parentRegionIds`, `isCustomized`, `isCombined`, `isCustomizable`, `isCombinable`, `hasAccess`, `regionTypeSort`, and `congressionalSession` [backend].
- An `IndustryImpactAnalysis` event echoed back by the API carries `isLocalEmployeeCompensation`, `isFteEmployment`, `isWageAndSalary`, and `isContributionAnalysis`; none is `[JsonIgnore]` [backend, `IndustryImpactAnalysis.cs:61-74`].

---

## 4. Cross-cutting findings

These affect two or more languages. Per-language sections reference them by id.

**X1. Hardcoded identifiers are stale or wrong.** C#, R OO, and R Updated use scheme 8 / dataset 96 / spending-pattern dataset 87 (2021). Python uses scheme 14 / dataset 98 (2023) while 124 (2024) is the default, and points Canada and International at the superseded schemes 12 and 13. The `Python - General` complex example uses industry code 509 under scheme 14, which is Federal electric utilities, not restaurants (section 3.2). Fix: either resolve ids at runtime (scheme by `mapCode` plus description, dataset by `isDefault`, industry by code and description together) or centralize one constants block per sample with the 2026 values and a date stamp. I recommend runtime resolution in the "identifiers" example and a constants block everywhere else.

**X2. Industry-set lookup by description is broken everywhere it appears.** C# `CreateProjectWorkflow.cs:79`, R OO `CreateProjectWorkflow.R:87`, and R Updated `CreateProjectWorkflow.R:94` all match `"546 Industries"`. The live description is `546 Industries (US)`. C# throws. R produces `NA` and survives only because of X5.

**X3. Two auth paths in one repo.** C# `Authentication.cs:43`, `Python - General/utilities/auth_helper.py:51`, Regional Overview `implan_auth.py:51`, and both R helpers post to `/auth`. GAMS `auth_helper.py:51` posts to `/api/auth`. The wiki and the Postman collection document `/api/auth`. Both work today at the gateway. Standardize on `/api/auth` (question Q2). R OO also sends `Username` and `Password` in PascalCase; the documented body is lowercase (question Q3).

**X4. Impact-status polling has no timeout and no terminal-state handling** in C# (`RunImpactAnalysisWorkflow.cs:64-76`), `Python - General` (`impact_analysis_workflow_examples.py:44-55`), R OO (`RunImpactAnalysisWorkflow.R`), and R Procedural (`waitForProjectRunToComplete`). A run that ends in `Error` or `UserCancelled` loops forever (C#, Python, R OO) or silently falls through and downloads results of a failed run (R Procedural). R Updated handles both correctly; port that pattern everywhere. The spec text from `GetImpactStatus` also says a 404 means the run never attached and is terminal.

**X5. `industrySetId` is passed alongside the aggregation-scheme route and is ignored.** C# `IndustryCodeEndpoints.GetIndustryCodes`, Python `industry_endpoints.get_industry_codes`, and R OO `GetIndustryCodes` all append `?industrySetId=` to `/IndustryCodes/{aggregationSchemeId}`. The backend action has no such parameter. The samples and `CreateProjectWorkflow` comments imply it filters. Drop the parameter on that route, or use the no-scheme route when filtering by industry set.

**X6. `GetIndustrySet(id)` helpers target a route the gateway does not expose** (C# `IndustrySetEndpoints.GetIndustrySet`, Python `industry_endpoints.get_industry_set`, R OO `GetIndustrySet`). No workflow calls them, but they are public helpers that will 403 or 404. Delete them or filter the list client-side (question Q13).

**X7. Combined-region readiness is polled through the user-regions list.** C#, Python General, R OO, R Procedural, and R Updated all poll `GET /region/{agg}/{ds}/user` and search for the hash. The backend recommends `GET /api/v1/region/user/{hashId}`, and the list returned 503 during this review. None of the C#, Python General, or R OO loops has a timeout. C# `CombinedRegionWorkflow.cs:107` still carries a "TODO: This endpoint does not yet exist" comment for a single-region read that does exist. Add a `GetUserRegion(hashId)` helper in each language and poll that with a timeout.

**X8. Estimated Growth Percentage is a GET with a JSON body in every sample.** That is what the API requires (section 3.3). C# `ImpactResultEndpoints.cs:99` relies on RestSharp 111 sending a body on GET, Python relies on `requests`, R OO switches to `httr2` for this one call. None of them comments why. Add the comment, and confirm the gateway forwards GET bodies end to end (question Q6).

**X9. Region type documentation is wrong in code comments and docs.** C# `Region.cs:106`, C# `RegionalWorkflow.cs:49`, and `Regions.md` list `country, state, msa, county, Congressional District, zipcode`. Actual filter values are in section 3.3.

**X10. Every workflow doc links to `impact/readme.md` anchors that do not exist.** All six docs link `readme.md#authentication---retrieving-bearer-access-token`; the readme headings are `Authentication` and `Retrieving the Token (non-SSO, non-M2M)`. The top-level README declares the wiki canonical. Point the docs, the sample readmes, and code comments at wiki pages instead.

**X11. Repo hygiene.** No `requirements.txt` or `pyproject.toml` for any Python folder (the General readme lists `humps`, whose pip name is `pyhumps`). The MIT license header is duplicated into 60-plus source files; a single `LICENSE` already exists at the root. Three Python folders carry three diverged copies of `Region`, `CombineRegionRequest`, and `RegionType`. Three R folders overlap almost entirely. The wiki's Code Examples page says C# and Python are primary and R is limited; the repo does not reflect that.

**X12. Scale versus documented throttles.** `impact/readme.md` states Region Models at 5 requests per minute. GAMS and Regional Overview issue one region GET per county (about 3,100) or per MSA (about 390) before downloading anything. At the documented rate that is more than ten hours for counties. Either the throttle text is stale or the scripts are impractical (question Q5).

**X13. Error surfaces are poor in every language.** C# swallows HTTP errors and surfaces `ArgumentNullException`. Python raises `str` objects in nine places, which is itself a `TypeError`. R OO's `ThrowIfNull` only warns and returns `NULL`. R Procedural ignores status codes. The API returns RFC 9457 problem details on every error; every sample should print `title`, `detail`, and `traceId` and stop.

---

## 5. C# (`sampleCode/CSharp/ConsoleApp`)

Last substantive change 2024-12-19. Targets `net8.0`, RestSharp 111.4.1. Build: 0 errors, 23 warnings [build].

### Blockers

- **C1. Debug builds never authenticate.** `Workflows/AuthenticationWorkflow.cs:31-36` has an `#if DEBUG` block that calls `Rest.SetAuthentication("")` and returns before the credential code runs. `SetAuthentication` then validates by calling `GetRegionTypes`, which fails with an empty token, so the app dies with `AuthenticationException("Invalid Bearer Token")` on startup. Debug is the default for `dotnet run` and for F5 in Visual Studio and Rider. The compiler flags the dead code (CS0162 at line 46) [build]. Delete the block; read credentials from environment variables or user secrets.
- **C2. `CreateProjectWorkflow` throws on the industry-set lookup.** `Workflows/CreateProjectWorkflow.cs:79` uses `First(s => s.Description == "546 Industries")`; the live description is `546 Industries (US)`, so `First` throws `InvalidOperationException` [live]. See X2. Match on `Id == aggregationScheme.IndustrySetId` instead of on text.
- **C3. `Program.cs` as committed cannot complete.** Lines 42-43 run `CreateProjectWorkflow.Examples()` and then `MultiEventToMultiGroupWorkflow.Examples()`, which uses `Guid projectGuid = Guid.Empty` (`MultiEventToMultiGroupWorkflow.cs:57`). The specification call 404s and returns an empty array, then `AddEvent` 404s and `ThrowIfNull` throws. The other two workflows are commented out. Make `Program.cs` a menu or a sequence that threads the created project id through.

### Major

- **C4. HTTP errors are swallowed.** `Services/Rest.cs:99` and `:123` have `//ThrowOnError(response);` commented out, so every failure returns a null `Data` and callers hit `.ThrowIfNull()`, which throws `ArgumentNullException` whose message is the C# expression text. The problem-details body is only visible in the log file. Re-enable a throw that includes status code, `title`, `detail`, and `traceId` (X13).
- **C5. `RunImpact` returns 0 on failure.** `Endpoints/ImpactEndpoints.cs:44` has no `ThrowIfNull`, so a failed run (for example 409 from a project with no groups) yields run id 0 and the status loop polls `/impact/status/0` forever.
- **C6. Status polling.** `Workflows/RunImpactAnalysisWorkflow.cs:70` compares to the literal `"\"Complete\""` including quotes. That matches RestSharp's content negotiation (section 3.3) but is brittle and undocumented. Use `GetResponseData<string>` so the JSON string is deserialized, add a timeout, and treat `Error`, `UserCancelled`, and 404 as terminal (X4).
- **C7. Double request.** `Endpoints/Events/EventEndpoints.cs:38` keeps a leftover `string? c = Rest.GetResponseContent(request);` before the real call, so `GetEventsTypes` hits the API twice.
- **C8. Ignored query parameter.** `IndustryCodeEndpoints.GetIndustryCodes` sends `industrySetId` with the scheme route; `CreateProjectWorkflow.cs:76-77` implies it filters (X5).
- **C9. Unexposed route.** `IndustrySetEndpoints.GetIndustrySet(int)` (X6).
- **C10. Combined-region polling.** `CombinedRegionWorkflow.cs:107` stale TODO, list-endpoint polling, no timeout (X7). The hardcoded counties `Lane County, OR` and `Douglas County, OR` are fine.
- **C11. GET with body.** `ImpactResultEndpoints.cs:99` (X8). RestSharp 107 and later send the body on GET, but I did not observe it [inferred; close by logging the outgoing request once].
- **C12. Stale ids.** Scheme 8, dataset 96, spending-pattern dataset 87, `"2022"` at `CreateProjectWorkflow.cs:133` (X1). Still valid today, but 528 / 14 / 124 is the current family.

### Minor

- **C13. Dependency and framework.** RestSharp 111.4.1 has a known moderate vulnerability (NU1902, GHSA-4rr6-2v9v-wcpc) [build]. .NET 8 leaves support in November 2026; retarget `net10.0` and update the README, which still says Visual Studio 2022 and .NET Runtime 8.0.6 (question Q7).
- **C14. 23 nullable warnings**, mostly CS8618 on DTO string properties (`Region`, `AggregationScheme`, `IndustrySet`, `IndustryCode`, `DataSet`, `CombineRegionRequest`, `ImplanAuthentication`, `SpendingPatternCommodity`). Mark them `required`, nullable, or default to `""`. Also CS8602 at `Rest.cs:133`, CS8603 at `AggregationSchemeEndpoints.cs:50`, CS0169 unused `Rest._implanAuthentication`.
- **C15. Internal leakage.** `Endpoints/Regions/RegionEndpoints.cs:34` has an `#if LOCAL` branch using the internal `region-types` route, and the csproj declares a `Local` configuration. Remove both.
- **C16. Debug hook in production path.** `Services/Json.cs` installs `ThrowNullAssignedToNonNull` on every deserialization, so any `null` string from the API (for example `fipsCode` on a combined region) makes the whole response deserialize to null and surface as C4. Remove it or gate it behind a flag.
- **C17. Region type comments** at `Region.cs:106` and `RegionalWorkflow.cs:49` (X9).
- **C18. Auth request carries a placeholder token.** The `JwtAuthenticator("BAD_TOKEN")` is attached to the client used for `/auth`, so the login request goes out with `Authorization: Bearer BAD_TOKEN`. Harmless today; use a separate client or clear the authenticator. Also `/auth` versus `/api/auth` (X3).
- **C19. Missing overloads.** `IndustryEmploymentEvent`, `IndustryEmployeeCompensationEvent`, and `IndustryProprietorIncomeEvent` have models but no `AddEvent` overload. Replace the three overloads with one generic `AddEvent<TEvent>`.
- **C20. `MultiEventToMultiGroupWorkflow` household codes 10002 and 10005** are labeled 15-30k and 50-70k, which matches the specification names in the docs. Fine. The Python complex example got this wrong (P11).

---

## 6. `Python - General`

Python 3.12+ syntax (PEP 695 generics). Compiles, imports, and pyflakes-clean apart from unused names [build]. No requirements file.

### Blockers

- **P1. Report CSVs are written as byte literals.** `endpoints/report_endpoints.py:29, 46, 63, 80, 101` do `report_csv = str(content)` on `bytes`, producing the text `b'Group,Event\r\n...'` as a single line. Demonstrated locally: `str(b'Group,Event\r\n')` is `"b'Group,Event\\r\\n'"` [build]. Use `content.decode("utf-8")`. Every file the impact example exports is unusable.
- **P2. Wrong industry for the scheme.** `workflow_examples/complex_project_example.py:49` sends `industry_code=509` to a scheme 14 project; 509 is Federal electric utilities there, and the inline comment even says 491. Full-service restaurants is 491 in 528 [live] (X1).
- **P3. Industry Impact Analysis events cannot be deserialized.** `event_endpoints.add_event` rebuilds the response with `type(event)(**dict)`. The API echoes `isContributionAnalysis` (and `isLocalEmployeeCompensation`, `isFteEmployment`, `isWageAndSalary`) [backend, `IndustryImpactAnalysis.cs:61-74`]. `IndustryImpactAnalysisEvent.__init__` accepts the last three but not `is_contribution_analysis`, so the constructor raises `TypeError` on an unexpected keyword. `simple_project_workflow_example.py` adds this event type, so the simple example dies after creating the event. Same pattern threatens every model: subclasses of `Event` lack `**kwargs`, `Region` had to grow `sgc_fuller_code` already. Give every model a tolerant `from_dict` or accept `**kwargs`. [backend, not run live]

### Major

- **P4. `raise "string"` in nine places** (`endpoints/regional_endpoints.py:128`; `workflow_examples/simple_project_workflow_example.py:71, 97, 136`; `models/event_models.py:46, 71, 99, 141, 186, 217`). Raising a `str` is `TypeError: exceptions must derive from BaseException` [build], which masks the real condition. Raise `ValueError` or a custom exception (X13).
- **P5. Status polling** in `impact_analysis_workflow_examples.py:44-55` (X4).
- **P6. Combined-region polling** in `regional_workflow_examples.py:59-72` (X7).
- **P7. Three base URLs.** `utilities/rest_helper.py:17` accepts `base_url` and ignores it; `endpoints/endpoints_helper.py:16` hardcodes its own; `utilities/auth_helper.py:20` reads `IMPLAN_API_URL`. Setting the env var redirects only authentication.
- **P8. Debug leftovers and TODO.** `rest_helper.py:65` `print('debug')` fires on every non-string body; `:110` `print('DEBUG')` on 401 with a TODO instead of re-authenticating.
- **P9. Auth path** `/auth` (X3).
- **P10. Stale ids and comments.** Dataset 98 while 124 is default; `regional_workflow_examples.py:26` comment says "538 Unaggregated"; Canada 12/100 and International 13/95 are the superseded families (X1). `identifiers_workflow_example.py:66` hardcodes a project UUID and will 404 for anyone else.
- **P11. Wrong labels.** `simple_project_workflow_example.py:34` calls code 3 "Vegetable and fruit farming" (actual: Vegetable and melon farming) [live]; `:33` `industry_set_id` is assigned and never used. `complex_project_example.py:71-72` labels 10005 as "Households 50-75k"; the specification is 50-70k.
- **P12. Logging helper fragility.** `utilities/logging_helper.py:66` calls `json.dumps(request.body)` on `bytes` for non-JSON bodies (`TypeError`); `:78` does `"json" in response_content_type` and fails on a missing `Content-Type` header. Request logs go through `logging.debug` while `basicConfig` is `INFO`, so the console never shows them although the docstring says console and file.
- **P13. Packaging.** No `requirements.txt`; README lists `humps` (install name `pyhumps`) and "Python 3.13.5" while the code needs 3.12 or newer for PEP 695. Add a requirements file and state the minimum.
- **P14. `main.py` does nothing.** Every example call is commented out; running it authenticates and prints "Workflow Example(s) Have Completed". Make it a small CLI (argument selects the example) so a fresh clone does something visible.
- **P15. Ignored query parameter and unexposed route.** `industry_endpoints.get_industry_codes` (X5), `get_industry_set` (X6).

### Minor

- **P16.** `models/region.py:50` attribute typo `dateset_description`.
- **P17.** `logging.warn` is deprecated (`auth_helper.py:85`, `rest_helper.py:95`).
- **P18.** `auth_helper._validate_token` calls `requests.get` without a timeout.
- **P19.** pyflakes: unused imports in `main.py:6-10` and `identifiers_workflow_example.py:1, 9`; unused locals `main.py:44, 49`, `regional_workflow_examples.py:75`; f-strings without placeholders in `auth_helper.py:43`.
- **P20.** `group_models.Group` receives `group_events` as raw dicts on the way back; harmless but inconsistent with the typed model.

---

## 7. `Python - GAMS Download` and `Python - Regional Overview Download`

Both compile; pyflakes only reports placeholder-less f-strings [build]. They are near-copies of each other.

- **G1. Dead code and double fetch (GAMS).** `main.py:74-80` builds `fips_to_hashid` that nothing reads; `:76` and `:90` both fetch every US county. `int(county.fipsCode)` raises if any region lacks a FIPS code. Delete lines 74-80.
- **G2. One status GET per region before downloading.** GAMS checks every county (about 3,100); Regional Overview checks every MSA (about 390). Under the documented throttle this is impractical (X12). Alternatives: `GET /api/v1/region/{agg}/{ds}/built` once, or attempt the export and only build on a 400. The scripts already treat 400 as "probably unbuilt" in `get_region_overview_industries`.
- **G3. `build_batch_regions` returns `RegionCard`, not `ExternalRegionCard`.** The `build-and-return` response includes `modelYearDescription`, `parentRegionIds`, and other fields [backend]. Regional Overview's `Models/region.py` accepts `modelYearDescription`; GAMS's copy does not, so `Region(**item)` raises `TypeError` if that field is present in the response [backend, not run live]. Same tolerant-model fix as P3.
- **G4. `wait_for_region_build`** iterates `user_regions` which is `None` after any request error (`TypeError`), polls the list endpoint (X7), and has no timeout.
- **G5. Credentials.** Regional Overview `main.py:37-38` takes `username` and `password` as literals in source and caches the token as `bearer.jwt`; GAMS reads `.env` through an `AuthHelper` copy. Standardize on the `.env` approach.
- **G6. Auth path** differs between the two (X3).
- **G7. Region type filter** is sent as `region_type.name` (`COUNTY`, `MSA`). Works because enum binding is case-insensitive, but it is not the documented value; use the API's names (X9).
- **G8. Readmes.** GAMS lists `openpyxl`, which it does not use; Regional Overview has two empty bullets; both link to the legacy readme (X10) and hardcode 14/98.
- **G9. Model duplication.** `ModelBuildStatus` (`NOTBUILT = 1` ...) is unused and does not match the API's string statuses; `RegionType` and `CombineRegionRequest` are duplicated with different casing conventions from `Python - General` (X11). `CombineRegionRequest.hashIds` is typed `list[int]` but holds strings.

---

## 8. `R - Object Oriented`

All findings [static]. This folder has never been run according to Timothy; the code is consistent with that.

### Likely blockers

- **R1. Unset S4 slots are serialized as `[]` and `{}`.** `convert_slots_into_list` emits every slot; `convert_na_to_null` turns length-1 `NA` into `NULL`; `httr::POST(encode = "json")` calls `jsonlite::toJSON(auto_unbox = TRUE)`, which renders `NULL` as `{}` and zero-length vectors as `[]`. So `ProjectEndpoints::Create` sends `"Id": []`, `"IsMrio": []`, `"FolderId": []`, `"LastImpactRunId": []`; `IndustryOutputEvent` sends `"Employment": {}` and friends from its `NA_real_` prototypes; `Group` sends `"Urid": []`, `"UserModelId": []`, `"ModelId": []`. Newtonsoft cannot bind `[]` to `Guid`, `bool`, or `long?`, and `{}` to `double?`, so these calls should come back 400 [inferred from jsonlite and Newtonsoft behavior; close by running `Create` once and reading the problem details]. Fix: filter out `NULL`, `NA`, and zero-length slots before serializing, and pass `null = "null"`.
- **R2. Class-name collision on `Event`.** `Endpoints/GroupEndpoints.R:27` defines `setClass("Event", slots = list(eventId, scalingFactor))` while `Endpoints/Events/Event.R` defines `Event` with `ImpactEventType`, `Title`, `Id`, `ProjectId`, `Tags`. `CreateProjectWorkflow.R` sources both; the last definition wins, `Group` inherits `eventId` and `scalingFactor` and serializes them into the group body (see R1), and the event subclasses now point at a redefined superclass. Rename the group-side class (for example `GroupEventRef`).
- **R3. Side effects at `source()` time.** `Endpoints/SpecificationEndpoints.R:53` calls the API with a fake GUID; `CombinedRegionWorkflow.R:141` runs the whole combine example; `RegionalWorkflow.R:108` runs the regional example and is itself sourced from `CombinedRegionWorkflow.R:71`. `MultiEventToMultiGroupWorkflow.R` sources `SpecificationEndpoints.R`, so the fake-GUID call fires there too. Move all executable lines under `program.R`.
- **R4. Pre-reorganization paths.** `auth_variables.R:29` and `program.R:24` hardcode `C:\git\api\sampleCode\R`. Since PR #39 the files live under `sampleCode\R\R - Object Oriented`, so nothing resolves until both lines are edited. The README says to edit them; better to derive the path from the script location.

### Major

- **R5. `%>%` without magrittr.** `Services/Rest.R:133-139` and `Services/Logging.R` use `%>%`. `LoadPackages.R` attaches `httr`, `httr2`, `jsonlite`, `scales`, `methods`, and `knitr`; none exports `%>%`. The `GET_BODY` path used by `GetEstimatedGrowthPercentage` fails with "could not find function `%>%`". Use the native `|>`.
- **R6. Bearer token printed on every call.** `Services/Rest.R` prints `validated_token` in both `GetResponseContent` and `GetResponseData` (`print(validated_token)`), so the full JWT lands in the console and in every RStudio history. Remove.
- **R7. PascalCase auth body.** `Endpoints/Authentication.R:55-56` sends `Username` and `Password` (X3, question Q3).
- **R8. Industry-set text match** at `CreateProjectWorkflow.R:87` yields `NA` (X2); `as.integer(implan546AggScheme$householdSetIds)` is applied to a list column and only works by accident.
- **R9. `SpendingPatternCommodity.R:33`** sets `LocalPurchasePercentage` to `label_percent()(1)`, the string `"100%"`, for a numeric field.
- **R10. Status polling** without timeout or terminal states (X4); `ThrowIfNull` only warns and returns `NULL`, so a failed call flows into `tolower(NULL)` and similar errors far from the cause (X13).
- **R11. `CombineRegions`** converts the parsed response back to a JSON string with `toJSON`, tests `length(regions) != 1` on a length-1 string (always passes), and makes the caller `fromJSON` it again.
- **R12. `GetAggregationSchemes`** always appends `?industrySetId=` and has no default for the argument; the `industrySetId <- NA` dance is a no-op.
- **R13. Combined-region polling** through the list endpoint (X7). `RegionalWorkflow.R:54` already notes "user region url is throwing 503 response", which matches what I observed [live].
- **R14. Stale ids.** Scheme 8, dataset 96, spending-pattern dataset 87 (X1).

### Minor

- **R15.** `IndustryImpactAnalysisEvent.R:44` has a stray `,` between `slots` and `prototype`; R treats it as a missing argument, so it is cosmetic.
- **R16.** `MarginType` factor includes `NA` as a level; `Region` class and most model classes are never used for parsing (responses are `fromJSON` data frames), so they are decorative.
- **R17.** `auth_env$logDir` points at `Final_Code\Logs`, a leftover from an earlier layout.
- **R18.** `Logging.R` branches on `class(response) == "httr2_response"` and calls `status_code()` on a plain list in the error path, which itself errors.

---

## 9. `R - Procedural`

All findings [static]. This is the only R code I would expect to get through a full run with modest fixes.

- **RP1. No HTTP error handling on writes.** `createProject`, `addIndustryOutputEvent`, `addCommodityOutput`, `addGroup`, and `runProject` never check the status code. `createProject` discards the POST response and re-finds the project by scanning all projects for the title, so a 409 (duplicate title) or 400 surfaces later as "subscript out of bounds" when `project["id"][[1]]` is read. The Updated helper fixed this with `http_error` checks; port that.
- **RP2. Run status loop ignores failure.** `waitForProjectRunToComplete` polls 90 times, matches only `"Complete"`, then returns silently. The script then downloads results for a run that may have failed and writes the problem-details JSON into `.csv` files (X4).
- **RP3. Build wait fails silently.** `waitForModelToBuild` returns `FALSE` after 15 minutes and the caller proceeds to `getUserModel` and `addGroup` with an unbuilt region. Also `region_card["modelBuildStatus"] == "Complete"` on a zero-row frame gives `logical(0)` and `if` errors.
- **RP4. Stale ids.** `aggregation_scheme_id = 14` with comment "aggregation scheme 8 is 546", `data_set_id = 98`, `group_dollar_year <- 2021` (X1). Dollar year 2021 on 2023 data is odd for a demo.
- **RP5. Credentials file is gitignored.** `private/creds.json` is excluded by `.gitignore`, so a fresh clone has no such file and the README ("needs to be entered into private/creds.json") reads as if it exists. Ship `private/creds.example.json` and say "copy and rename".
- **RP6. Region lookup works.** `getRegionCardByFipsCode` compares state `fipsCode` to the two-digit prefix; live state cards carry two-digit FIPS (for example `"51"` for Virginia) [live], so this is correct. The caches are keyed by scheme and dataset and never expire, which is fine for reference data.
- **RP7. Token refresh at 479 minutes** while the documented lifetime is 24 hours. Harmless, but the comment claims 480 minutes.
- **RP8. Cosmetics.** Function name `getSummaryEconomicIndiciators`, README "ad folder name", `demo_events.csv` and the region CSVs pad descriptions with 100 spaces and a tab, `implan_main_demo_script.R` attaches `httr2` while the helper uses `httr`, mixed `EventId` and `scalingFactor` casing in `addGroup`.

---

## 10. `R - Updated`

All findings [static]. This folder was copied in by PR #39 and contains only the five OO workflow files, `auth_variables.R`, `program.R`, a reworked procedural helper, and a reworked demo script. It has no `Endpoints/`, `Services/`, `IWorkflow.R`, `LoadPackages.R`, or `RegionalWorkflow.R`.

### Blockers

- **U1. `program.R` cannot start.** Line 25 is `source(file.path(path, "LoadPackages.R"))` but nothing in this file defines `path` any more (the OO `program.R:24` did); `auth_variables.R` defines it but is only sourced on line 28. R stops with "object 'path' not found". Even with `path` fixed, `auth_variables.R:28` points at the pre-reorg folder, and every `auth_env$...` entry resolves to the `R - Object Oriented` copies of the workflow files, so this `program.R` would execute the OLD workflows, not the updated ones sitting next to it.
- **U2. Demo script sources a missing file.** `implan_demo_script.R:23` is `source("new_implan_api_helper.R")`; the file in the folder is `implan_api_helper.R` (question Q11).
- **U3. Undefined configuration constants.** `CreateProjectWorkflow.R` reads `INDUSTRY_SET_ID`, `TARGET_SCHEME_DESCRIPTION`, `TARGET_INDUSTRY`, `TARGET_DATASET_DESCRIPTION`, `TARGET_STATE`, and `DOLLAR_YEAR`; `CombinedRegionWorkflow.R` reads `COUNTIES_TO_COMBINE`, `AGGREGATION_SCHEME_ID`, and `DATA_SET_ID`. Neither file defines them, and only `MultiEventToMultiGroupWorkflow.R:53-56` defines a subset (`AGGREGATION_SCHEME_ID`, `INDUSTRY_SET_ID`, `DATA_SET_ID`, `DOLLAR_YEAR`). Both workflows stop with "object not found". The configuration block that the comments describe was never added.
- **U4. URID list is serialized as an object.** `implan_demo_script.R:80` builds `urids <- c(urids, getRegionCardByFipsCode(fips)["urid"])`. Combining a list with a one-column data frame yields a named list (`urid = ...`), which `toJSON` renders as a JSON object rather than an array, so `buildCombinedRegion` posts `"urids": {"urid": ..., "urid": ...}` and the API should reject it. The Procedural original's `urids[length(urids) + 1] <- ...` produces a proper unnamed list [inferred from R and jsonlite semantics; close by printing `toJSON(list(urids = urids))` once].

### Major

- **U5. Credential guidance contradicts itself.** `program.R:11-14` says to set `IMPLAN_USERNAME` and `IMPLAN_PASSWORD` environment variables, then lines 21-22 define `username <- ""` and `password <- ""` literals that `AuthenticationWorkflow.R` actually uses. The env vars are never read.
- **U6. Inherits R1, R2, R5, R6, R7, R9, and R13** because it reuses the OO `Endpoints/` and `Services/` unchanged.
- **U7. Stale ids** as in R OO (8 / 96 / 87) and in the helper (14 / 98 / 2021) (X1).
- **U8. Worth keeping.** Timeouts with `MAX_WAIT_SECONDS`, terminal-status handling, `http_error` checks after every request, the `saveResult` helper, `PROJECT_GUID` from an environment variable, and the input-file existence check are all improvements over the other two R folders. Port them into whichever R folder survives.

---

## 11. Workflow docs (`impact/workflows`)

- **D1. `CombineRegions.md:29-36`** shows `"hashids": [ { "W1aQl9wzxj", "Rgxp4eA3xK" } ]`, which is not valid JSON (object braces inside the array). Key should be `hashIds`; the doc should also mention `urids` as the alternative, and the response `modelBuildStatus: "New"`.
- **D2. `CreateProject.md`.** Line 205 names the field `intermediateOutputs`; the DTO is `IntermediateInputs` [backend]. JSON blocks at lines 71-79 and 179-187 have trailing commas. Line 125 links `[Impact Readme - Event Types](TODO)`. Line 58 "A code to describe" is an unfinished sentence. The event-type list omits `CustomSpendingPattern`, `HouseholdSpendingPattern`, and the international and custom Industry Impact Analysis types. The project-create example includes `id` and `lastImpactRunId`, which the API tells callers to leave out.
- **D3. `RunImpactAnalysis.md:170-176`** shows the Estimated Growth Percentage body with `[{"a", "b"}]` style arrays, again not valid JSON, and does not say all five arrays are required.
- **D4. `Regions.md:138-139`** lists region types with wrong casing and a space (X9); the dataset example marks 96 (2022) as default, which is now true only for scheme 8.
- **D5. `CanadaDataWorkflowConsiderations.md`.** "HosueholdSetId" typo; `"Scaling Factor": 1` is not a valid key; scheme 12 (235) is superseded by 17 (236); the dataset list is stale; "only one Household Set available to Canadian data" is per scheme (4 for 235, 7 for 236).
- **D6. Broken anchors in every doc** (X10). At minimum `#authentication---retrieving-bearer-access-token` does not exist; the others were not individually verified.
- **D7.** `MultiEventToMultiGroup.md` is accurate; consider linking the wiki specification page rather than the readme.

---

## 12. Out-of-scope observations

- `IMPLAN-API.postman_collection.json:6468` has a double slash: `api/v1//impact/results/ExportDetailEconomicIndicators/...`.
- `AggregationSchemeController.GetAggregationSchemesAsync` XML doc says omitting `industrysetId` returns the default US set's schemes; the code returns every scheme and only filters when the parameter is present [backend]. The samples' behavior (list everything, then pick) is correct; the spec text is not.
- `GET /api/v1/region/{agg}/{ds}/user` returned 503 for scheme 14 / dataset 124 during this review. That is one observation, not a pattern.
- The Google Sheets pages and `batch/` docs were not reviewed.

---

## 13. Recommended plan

Superseded by section 15, which records Timothy's answers and the plan as adjusted on 2026-09-14. Kept for the record.

Ordered so each step is independently reviewable.

1. **Decide the folder set** (Q1). My recommendation: keep `CSharp`, `Python - General`, and one `R` folder based on the Procedural helper plus the Updated folder's error handling; move the GAMS and Regional Overview scripts into `Python - General/workflow_examples` sharing its auth, REST, and models; delete `R - Object Oriented` and `R - Updated` after porting their scenarios. Update the wiki Code Examples note accordingly.
2. **Fix the blockers** in the surviving folders: C1-C3, P1-P3, and whichever of R1-R4, U1-U4 apply to the surviving R code.
3. **Replace hardcoded ids** (X1, X2) with runtime discovery in the identifiers example and a dated constants block elsewhere, using scheme 14, dataset 124, industry set 12, and current dollar year; verify each industry by code and description together.
4. **Apply the shared conventions**: `/api/auth` (X3), status polling with timeout and terminal states (X4), drop the ignored `industrySetId` (X5) and the unexposed `GetIndustrySet` (X6), poll `region/user/{hashId}` (X7), comment the GET-with-body (X8), fix region-type text (X9), surface problem details (X13).
5. **Docs**: fix D1-D6 and repoint every link to the wiki (X10); add `requirements.txt` and a Python minimum version; add `creds.example.json` for R (X11).
6. **Run each surviving folder end to end** against production with a test account, or against INT if a token is available, and record the run in the folder README. R needs a machine with R installed; this one has none.
7. **Housekeeping**: retarget C# to `net10.0` and current RestSharp (C13), remove the license header duplication in favor of the root `LICENSE`, and remove `Local`/`LOCAL` build leftovers (C15).

---

## 14. Questions for Timothy

All thirteen were answered on 2026-09-14; see section 15.

- **Q1. Folder set.** Do you agree with keeping C#, `Python - General`, and one R implementation, and deleting `R - Object Oriented` and `R - Updated` after porting? If you want to keep an object-oriented R sample, R1-R4 need to be fixed first and it will still be untested until someone runs it.
- **Q2. Canonical auth path.** Standardize every sample on `/api/auth` as the wiki documents? Is `/auth` going to stay on the gateway indefinitely, or should the samples treat it as legacy?
- **Q3. Auth body casing.** Does the auth service accept `Username`/`Password` in PascalCase (R OO sends that)? I could not test it without raw credentials.
- **Q4. Example identifiers.** Should the samples show the current family (scheme 14, dataset 124, industry set 12) as literals, or resolve them at runtime? Should the Canada and International examples move to schemes 17 and 18?
- **Q5. Throttles.** Are the rates in `impact/readme.md` (Region Models 5/min, Industry Codes 10/min, Data Sets 10/min) still accurate? That decides whether the GAMS and Regional Overview per-region checks are viable or must be redesigned.
- **Q6. GET with body.** Is the gateway confirmed to forward a request body on `GET .../EstimatedGrowthPercentage`? Is there any plan to change that endpoint to POST? The samples should follow whatever the answer is.
- **Q7. Targets.** Retarget C# to `net10.0` and bump RestSharp? State Python 3.12 as the minimum? Any R version floor?
- **Q8. Test access.** Can I get a test account, or an INT token, to run the samples end to end after fixing them? Otherwise I will make the fixes and hand you a one-step-at-a-time run script.
- **Q9. Workflow markdown.** Keep `impact/workflows/*.md` and fix them, or delete them in favor of the wiki pages they duplicate?
- **Q10. Dollar year.** What dollar year should examples use in 2026 (the code says 2024 everywhere, the Procedural helper says 2021)?
- **Q11. `new_implan_api_helper.R`.** The Updated demo script sources a file by that name. Was a newer helper meant to be copied into the repo, or is this a leftover rename?
- **Q12. Backend intent.** Is `GET /IndustryCodes/{aggregationSchemeId}` ignoring `industrySetId` intentional? If yes, the samples and docs should stop passing it; if no, that is a backend ticket.
- **Q13. `GetIndustrySet(id)`.** Expose it at the gateway, or delete the helpers in all three languages?

---

## 15. Decisions and revised plan (2026-09-14)

### 15.1 Decisions

| # | Decision |
| --- | --- |
| Q1 | Consolidate to exactly three folders named for the language: `sampleCode/CSharp`, `sampleCode/Python`, and `sampleCode/R`. No sub-project or variant folders; the entry point sits at each folder root. C# `ConsoleApp/` is flattened up one level; `Python - General` becomes `Python` and absorbs GAMS and Regional Overview as workflow examples; the three R folders become one `R`. |
| Q2 | Every sample authenticates at `POST /api/auth`. `/auth` is not mentioned. |
| Q3 | Login body is lowercase `username` and `password` everywhere. No live test of PascalCase needed. |
| Q4 | Identifiers are resolved at runtime: scheme by `mapCode` plus description, dataset by `isDefault`, industry by code plus description. |
| Q5 | The readme throttles are accurate. The GAMS and Regional Overview logic is redesigned to avoid one status GET per region (use the built-regions endpoint, or export first and build only on a 400). |
| Q6 | Not fixed in `ui_api` `main`: still GET with an implicit JSON body; both related branches are merged without changing it; every gateway export shows GET only; the published 2026-09-09 spec documents the required body; PHX-16692 lists "GET-with-body" as out of scope pending its own ticket. Timothy confirms API Gateway forwards GET bodies. Samples keep GET with body and comment why. |
| Q7 | Every language, runtime, and package moves to its current release when the samples are updated (net10.0 and current RestSharp for C#, current Python, current R). Exact versions are checked at implementation time. |
| Q8 | Credentials come from a gitignored `.env` (`IMPLAN_USERNAME`, `IMPLAN_PASSWORD`) read by all three languages and never printed. Objects created during verification runs carry a recognizable title prefix and are deleted afterward. |
| Q9 | The six workflow docs are fixed in place and relinked to the wiki. |
| Q10 | Dollar year is the current calendar year, computed at runtime. |
| Q11 | The single R folder is built from the `R - Updated` files as the newer base, merging in the `R - Object Oriented` Endpoints and Services they reference and the Procedural helper. The `new_implan_api_helper.R` reference is pointed at the merged helper. |
| Q12 | Ignoring `industrySetId` on `GET /IndustryCodes/{aggregationSchemeId}` is intentional. Samples and docs stop passing it on that route. |
| Q13 | `GetIndustrySet(id)` helpers are deleted in all three languages; callers filter the list. |
| Q14 | Three workflows added to the extended set after a survey of IMPLAN Support and the spec: 10 ImportEvents (Event Template upload), 11 MrioProject (`isMrio` project with spillover into a second region), and 12 AdvancedEvents (Industry Contribution Analysis and Industry Spending Pattern events, tags, tag-filtered results). Canada and International are folded into Identifiers and a map-code option on CreateProject; RegionalExports takes the export name as a parameter instead of growing new workflows. |
| Q15 | Samples target production (`api.implan.com`). The contract to write against is the INT-generated spec, because the error-code corrections now on INT will be in production before the updated samples are published; that is the source of the disconnects between the INT observations in this review and today's production behavior. |
| Q16 | The R folder is rebuilt on `httr2` with the native pipe and `jsonlite` as plain functions, the way the IMPLAN Support article "How to Use the IMPLAN API with R: Obtaining Your API Token" does it, not on the S4 classes and superseded `httr` of the existing folders. `req_auth_bearer_token()` for redaction, `req_error()` for problem details, `req_retry()` for the auth service's transient 503, `req_throttle()` in bulk workflows. The support article's "Procedural versus Object-Oriented" section will need updating once R is one folder. |

### 15.2 Revised plan

Each step is one reviewable unit. Timothy reviews the pattern on the first folder before it is applied to the others.

1. **Python first.** Move `Python - General` up to `sampleCode/Python` (entry point at the root). Fix P1 through P20 and apply every shared convention (X1 through X13 as decided above): `/api/auth`, one base URL, the token cache kept and made the reference pattern, tolerant models, status polling with timeout and terminal states, region readiness via `GET /region/user/{hashId}`, no `industrySetId` on the scheme route, no `get_industry_set`, runtime id resolution, current-year dollar year, `requirements.txt`, README with the current Python version. Rename workflow files to the CLAUDE.md names. Verify: compile, pyflakes, then a live run of identifiers, create project, impact, and reports using `.env`.
2. **Extended set in Python.** Absorb GAMS and Regional Overview into `sampleCode/Python/workflows` as the BulkFromCsv and RegionalExports workflows on the shared client, with the redesigned readiness check, then add ImportEvents, MrioProject, and AdvancedEvents. Delete the two Python download folders. Verify: live run of each; BulkFromCsv and RegionalExports against a small region set.
3. **C#.** Flatten `ConsoleApp/` up into `sampleCode/CSharp` so the `.csproj` sits at the folder root. Retarget to net10.0 and current RestSharp; remove the `DEBUG` and `LOCAL` blocks; read credentials from `.env`; add the token cache (C# has none today); re-enable error surfacing with problem details; fix C2 and C3; apply the shared conventions; delete `GetIndustrySet`; fix region-type comments; rename `RegionalWorkflow` and `CombinedRegionWorkflow` to the CLAUDE.md names; add `IdentifiersWorkflow`. Verify: build, then live run of the workflows in sequence.
4. **R.** Create `sampleCode/R` from the Updated base plus the referenced OO Endpoints and Services and the Procedural helper (which already caches the token); fix U1 through U5 and R1 through R13; `.env` credentials; snake_case file and function names; current R. Verify: needs an R installation (none on this machine); either install R here or Timothy runs the steps.
5. **Docs.** Fix D1 through D6 in place and relink to the wiki; update the three sample READMEs; update the wiki Code Examples note about which folders exist.
6. **Cleanup.** Delete `R - Object Oriented`, `R - Updated`, `R - Procedural`, `Python - GAMS Download`, `Python - Regional Overview Download`, and the emptied `CSharp/ConsoleApp` and `Python/Python - General` shells so only `CSharp`, `Python`, and `R` remain under `sampleCode/` (plus `googleSheets`, which is out of scope); delete verification projects and regions from the account; hand over the list of paths and a suggested commit message per step.

### 15.3 Specification written

The workflow specification lives in the repo as `CLAUDE.md` (rules, commenting standard, README standard, layout, naming, per-workflow specs) with a short reader-facing `sampleCode/README.md` pointing at it. Both written 2026-09-14 and committed as `2fc3eca` and `2264a88`.

Status moved to section 16.3.

---

## 16. Build state (2026-09-16, last updated 2026-09-21)

### 16.1 What was done

All three folders were rebuilt against the section 6 specifications. `sampleCode/` now holds exactly `CSharp`, `Python`, `R`, and the unrelated `googleSheets`. The seven old folders are gone.

**Python** (`sampleCode/Python`, 40 modules). Written first and used as the reference for the other two. Entry point `main.py` with an argparse CLI. Layers: `utilities/`, `models/`, `endpoints/`, `workflows/`. The `humps` dependency was removed by hand-writing the two case conversions, so the manifest is `requests` and `python-dotenv` and nothing else.

**C#** (`sampleCode/CSharp`). `ConsoleApp/` was flattened so the `.csproj` sits at the folder root, retargeted to `net10.0`, and moved to RestSharp 114.0.0, which has no advisories. Entry point `Program.cs` with a hand-written argument parser, no argument package. The `.env` reader is hand-written for the same reason.

**R** (`sampleCode/R`, 37 R files). Rebuilt from nothing on `httr2` and `jsonlite`, replacing all three old folders. Entry point `main.R`, which works under `Rscript` and under `source()` from RStudio. Plain functions, snake_case, S3 only for the `describe()` one-liners; environments in the two places state has to be mutable, the client and the region cache.

### 16.2 Findings from the build, worth keeping

- **There is no `/built` endpoint.** The section 6 spec for RegionalExports named `GET /api/v1/region/{aggregationSchemeId}/{datasetId}/built`. It is absent from the generated v1 spec and from every gateway export. The children listing already returns `modelBuildStatus` for every region it lists, so one call gives both the list and the build state. `CLAUDE.md` has been corrected and now says not to reintroduce it.
- **Query parameters cannot be a dictionary.** Several filters are repeated parameters (`regions=Oregon&regions=Wisconsin`), and a map keyed by name silently keeps only the last value. C# got a `Query` list type; R uses `req_url_query(.multi = "explode")`; Python relies on `requests` handling a list value.
- **Three `.gitignore` rules were dead.** `private/`, `.env`, and `results/` in the R block carried trailing comments. A `#` only starts a comment at the start of a line, so each pattern included its own comment text and matched nothing. `.env` was ignored only by an unrelated line in the Python block. Fixed, and the block now keeps every note on its own line.
- **`docs/` was ignored repository-wide.** It came in with the boilerplate R `.gitignore` as the pkgdown output folder, and it is unanchored, so any folder of prose named `docs` anywhere in this repository would have been invisible to git. Removed.
- **Folder ids change type.** A folder reports its own id as a string while a project's `folderId` and a folder's `parentId` are integers. Each language has one helper that converts, rather than a cast at each call site.

### 16.3 Status by language

Written means the file exists under the name `CLAUDE.md` gives it and follows the rules there. Built means the language's own compiler or interpreter accepts it. Run means it has been executed end to end against production, which has not happened for anything yet, because that needs credentials and creates real objects in an IMPLAN account.

| # | Workflow | C# written | Python written | R written |
| --- | --- | --- | --- | --- |
| 1 | Authentication | yes | yes | yes |
| 2 | Identifiers | yes | yes | yes |
| 3 | Regions | yes | yes | yes |
| 4 | CombineRegions | yes | yes | yes |
| 5 | CreateProject | yes | yes | yes |
| 6 | MultiEventToMultiGroup | yes | yes | yes |
| 7 | RunImpactAnalysis | yes | yes | yes |
| 8 | BulkFromCsv | yes | yes | yes |
| 9 | RegionalExports | yes | yes | yes |
| 10 | ImportEvents | yes | yes | yes |
| 11 | MrioProject | yes | yes | yes |
| 12 | AdvancedEvents | yes | yes | yes |

| Language | Static check | Result |
| --- | --- | --- |
| C# | `dotnet build` (SDK 10.0.400, net10.0) | Succeeded, 0 warnings, 0 errors. `dotnet run -- --list` prints all twelve. |
| Python | Import of all 40 modules, plus pyflakes (3.14.3) | All import, pyflakes silent. `python main.py --list` prints all twelve. |
| R | `Rscript main.R --list` on R 4.6.1, which sources all 37 files, plus a 44-check behavior script | All parse and load, all 44 checks pass. Exit codes are 0 for the list and 4 for an unknown workflow. |

R was installed on 2026-09-21 (R 4.6.1, via `winget install --id RProject.R`), which closed the gap this section previously described. httr2 resolved to 1.3.0 and jsonlite to 2.0.0, both above the floors in `packages.R`.

The behavior script exercised the parts most likely to be wrong and could not be reasoned about safely: that a filter with several values becomes a repeated query parameter rather than one comma-separated value, that a single tag serializes as `["tag"]` rather than `"tag"`, that all five growth-report arrays survive as `[]`, that a GET carrying a JSON body stays a GET after `req_body_json()` would otherwise turn it into a POST, that the `Authorization` header reads `<REDACTED>` when a request is inspected, and that an event carrying a field the sample has never heard of still reads. All of those hold.

### 16.3.1 Three defects the first R run found

Writing R without running it cost three bugs, all of them in the two files a reader touches first.

- **`packages.R` could not install anything on a fresh Windows machine.** The default library lives inside the R installation, under Program Files, and a standard user cannot write there. An interactive session offers to create a personal library instead; `Rscript` is never asked, so `install.packages()` failed with "unable to install packages" on the very first documented command. `user_library()` now creates the folder R already names in `R_LIBS_USER`, puts it on `.libPaths()`, and installs there.
- **`find_sample_root()` checked the command line before the sourced-file path.** When one script sources `main.R`, `--file=` names the outer script, so the sample root resolved to the caller's folder and every `source()` after it failed. The `ofile` check now runs first, because it is the more specific answer.
- **`main.R` ran the command line and quit whenever the session was non-interactive.** Sourcing it from another script is non-interactive too, so `source("main.R")` printed the workflow list and then killed the caller's session. The guard now keys off whether `--file=` names `main.R`, which is the question actually being asked.

None of these would have shown up in a review of the code. All three needed an interpreter.

### 16.4 Workflow docs, done 2026-09-17

D1 through D7 are fixed in place in `impact/workflows/*.md`, and the shared notes block in every page now points at the wiki first, at the readme second, and at `sampleCode/` for a runnable version. The claim in an earlier draft of this section, that those pages describe the old folder layout, was wrong: they never named a sample folder except one mention of `MultiEventToMultiGroupWorkflow.cs`, which now lists all three languages.

Three things turned up that the original review did not have:

- **The JSON blocks were worse than D1 and D3 suggested.** Validating every fenced `json` block found 15 that do not parse across the repository, not the two the review named. Eight were in `impact/workflows` and are fixed. Two more are the deliberate placeholders in `Workflow Template.md` and were left alone.
- **`Regions.md` had non-breaking spaces inside a JSON block**, so copying the region-type list out of the page produced something that would not parse. Replaced with ordinary spaces.
- **`CanadaDataWorkflowConsiderations.md` had an unterminated code fence** around the Create Group body, so everything after it rendered as code.

Two broken links were also fixed: `#authentication---retrieving-bearer-access-token`, which appeared in all six pages and has never existed in `impact/readme.md`, and `#summary-taxes-export-get`, where the heading carries no `(Get)`. Two `[Implan Support](support.implan.com)` links lacked a scheme and so resolved as relative paths. A link and anchor sweep now reports zero problems across `impact/workflows`.

**Not fixed, because `impact/readme.md` was out of scope for this pass.** Five JSON blocks in it do not parse, at lines 492, 919, 2210, 2320, and 2355. Line 492 and line 2320 are the more serious: 492 contains non-breaking spaces, and 2320 opens a fence on a fragment rather than an object. The others are trailing commas and one missing comma.

### 16.5 ImportEvents now explains all three outcomes, done 2026-09-21

An import can land in three states, and until now the workflow only spoke about one of them. It explained a group that came back with no events attached, said nothing when the import produced no groups at all, and in that second case printed a bare "Groups: 0" and stopped.

That second case is the common one, not an edge case. Timothy's own filled template, `Event Template V25.3_US 528_UR Visitor and Student Spending.xlsx`, is exactly it: 16 Industry events, and blank Groups and Group Events sheets. Plenty of analysts keep their events in the workbook and choose the regions afterwards, so a run that produces events and no groups is a normal outcome that needs a next step, not a silent one.

All three languages now branch three ways: no groups at all names the blank Groups sheet and points at the Create Group endpoint, groups with nothing attached names the blank Group Events sheet as before, and only the third prints the "ready to run" command. The first two now say plainly that the Project cannot be run yet.

### 16.6 Still to do

1. **Live verification.** The only real gap left. Needs a `.env` in each folder. Workflows 1 through 3 only read; 4 onwards create real objects in the account and each prints what it made so it can be deleted. Workflow 10 is no longer blocked on an input: pass `--workbook` and the path to the filled template named above, which lives outside this repository.
2. **`impact/readme.md` JSON blocks.** The five above. Re-checked 2026-09-21, still five, at those exact lines.
3. **The wiki's Code Examples page**, in the separate `api.wiki` repository. An earlier draft of this list said it points at the seven old folders. It does not: it links to `sampleCode` generically, and that link is still correct. What is stale is the note under it, which is dated 2025/08, calls C# and Python the primarily supported languages, calls R limited, and lists Java. R is now a full peer of the other two, and there is no Java sample in this repository.
4. **Delete `sampleCode/R/creds.json`.** Checked 2026-09-21: both fields hold empty strings, so it is an empty stub and nothing is lost. It is gitignored either way.

### 16.7 Open questions

- **Rate limits.** The wiki says Region Models is 5 per minute. Does that count region *reads* (children, user regions) or only *builds*? The bulk workflows currently throttle every request in the run to 5 per minute, which is safe and may be much slower than it needs to be.
- **ImportEvents needs a workbook.** Workflow 10 uploads a filled IMPLAN Event Template. A valid one has to be made in Excel from IMPLAN's official blank template rather than generated, so the sample ships without one and explains where to get it. Should a filled `event_template.xlsx` be committed instead?
- **The root Postman collection.** `IMPLAN-API.postman_collection.json` is hand-maintained and has 196 requests. Re-checked 2026-09-21: exactly one request carries a double-slash path, `Detail Economic Indicators Export`, whose URL reads `api/v1//impact/results/...`. Replacing it means choosing which generated collection, because `ui_api` holds several: the prod one has 149 requests, the INT one 161, and `External.Api/OpenApi` carries another at 181. Which, if any?

- **A filled Event Template for the repository.** Timothy has four US 528 templates in `Documents\IMPLAN`; three are blank and one, `Event Template V25.3_US 528_UR Visitor and Student Spending.xlsx`, holds 16 Industry events with Event Name, Specification, and Output, and empty Groups and Group Events sheets. It is good enough to verify workflow 10 locally by passing `--workbook`, but it is named for a specific engagement and carries real event rows, so it should not be committed. Shipping one means making a small neutral workbook for the purpose.
- **A leftover credentials file.** `sampleCode/R/creds.json` came from the old procedural R helper and was moved there when its folder was deleted. It is gitignored. Convert it to `.env` or delete it.

## Appendix A. Verification log

| Check | Command or tool | Result |
| --- | --- | --- |
| C# build | `dotnet build -c Debug` on a copy of `ConsoleApp` (SDK 10.0.400, target net8.0) | Build succeeded, 0 errors, 23 warnings (CS8618 x18, CS8602, CS8603, CS0162, CS0169, NU1902 RestSharp 111.4.1) |
| Python syntax | `python -m py_compile` on every `.py` under `sampleCode/Python` (Python 3.14.3) | All compile |
| Python lint | pyflakes in a scratch venv | Only unused imports/variables and placeholder-less f-strings |
| Python imports | Imported all 23 modules of `Python - General` with dummy credentials | All import |
| Python behaviors | `str(b'...')` and `raise 'text'` demonstrations | Byte-literal string; `TypeError: exceptions must derive from BaseException` |
| Route mapping | `External.Api/OpenApi/route-map.json`, gateway export `OAS30_pvvfv64frh_green_with_apig_ext.json` | Every sample URL maps; `/auth` and `/api/auth` both present; `industry-sets/{id}` absent |
| Live ids | MCP `get_agg_schemes`, `get_datasets_for_scheme` (8, 14, 12, 13), `get_ind_sets`, `get_ind_codes_by_agg_scheme` (8, 14), `get_region_types`, `get_top_level_region_children` (14, 124, State) | Section 3 |
| Live user regions | MCP `get_user_regions_for_scheme` (14, 124) | HTTP 503 Service Unavailable |
| Spec details | MCP `describe_api_endpoint` for `GetEstimatedGrowthPercentage` and `GetImpactStatus` | Required JSON body on GET; status 200 offers `text/plain` and `application/json` |
| R | none | Not installed on this machine |
| Working tree | `git status --short` in `github_api` | Clean |

Scratch artifacts (C# build copy, Python venv) are in this session's scratchpad directory, not in the repo or `C:\temp`.

## Appendix B. File age

| Path | Last substantive commit |
| --- | --- |
| `sampleCode/CSharp` | 2024-12-19 (`4098a5f`) |
| `sampleCode/Python/*`, `sampleCode/R/*` | Moved by PR #39 on 2026-07-13 (`bf1aa80`); content predates the move |
| `impact/workflows` | 2025-09-30 (`96fe484`) |
| `IMPLAN-API.postman_collection.json` | 2026-08-12 (`025be18`) |
