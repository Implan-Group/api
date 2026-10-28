# ImpactApi - Bulk From CSV Workflow
- Builds study regions from lists of states and counties, adds the same events to each one, runs them all, and saves the reports. Everything it builds comes from three CSV files, so you can analyze your own regions and events without changing any code.
- [Combine Regions](https://github.com/Implan-Group/api/wiki/Combine-Regions)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 Fill in the input files
- The three files are in the `data/` folder of each language's sample: `sampleCode/CSharp/data`, `sampleCode/Python/data`, and `sampleCode/R/data`. Each folder has its own copy, so edit the one for the language you run.

| File | Columns | Each row is |
| --- | --- | --- |
| `state_based.csv` | `fips`, `region_description`, `model_name` | A state, by its FIPS code: `41000` or `41` for Oregon |
| `county_based.csv` | `fips`, `region_description`, `model_name` | A county, by its five-digit FIPS code: `41019` for Douglas County, Oregon |
| `demo_events.csv` | `Name`, `Code`, `Type`, `Value` | An event. `Type` is `Industry Output` or `Commodity Output`, `Code` is the industry or commodity code, and `Value` is the output in dollars |

- Keep each file's header row, and save the files as comma-separated CSV. A file saved with semicolons between the values, as some regional settings do, is refused with a message saying so
- Put double quotes around any value that contains a comma: `41019,"Douglas County, OR",Southwest`
- Regions
	- Rows in the same file that share a `model_name` are combined into one region. A `model_name` on only one row uses that state or county as it is
	- A `model_name` can be used in one file only. Give the counties a different `model_name` from the states
	- The region is found by `fips`. `region_description` is a label for you
	- A FIPS code that has lost its leading zero, as Excel does to Alabama's `01000`, is padded back to `01000`
	- A rerun with the same rows reuses the regions it built before. To change which states or counties a `model_name` covers, give it a new `model_name`: the API refuses a name you already have when its regions differ
- Events
	- `Name` becomes the event's title, so each one must be different
	- Take each `Code` from the current default Industry Set, which the `identifiers` workflow prints. The same code is a different industry in another set
	- `Value` can be written `1000000`, `1,000,000`, or `$1,000,000`
	- Every event is applied to every region
- `model_name` and `Name` cannot contain any of `& | ; % * ? ! = ' " ^ #`, which IMPLAN does not allow in titles
- One of the two region files can be left with only its header row, as long as the other has at least one region. `demo_events.csv` needs at least one event
- Every row is checked before anything is created in your account. A problem stops the run with a list of each file and line to fix, and nothing is created

---
## 🔽 Run it
- Run the `bulk-from-csv` workflow from the C#, Python, or R folder. Each folder's README gives the exact command
- It creates one project per region plus one holding them all, files them in an IMPLAN Cloud folder named `ImpactApi Sample - Bulk From CSV`, runs each, and saves four reports per run under `reports/ImpactApi Sample - Bulk From CSV/`: Summary Economic Indicators, Detailed Economic Indicators, Summary Taxes, and Detailed Taxes
- It holds every request to five a minute, the published limit for region builds, so a run takes a while. Delete the folder and its projects in IMPLAN Cloud when you are done

---
## 🔽 What it does
1. Resolves the current default US Aggregation Scheme, Dataset, and Household Set
2. Reads and checks the three files
3. Looks up every FIPS code: the states once, then the counties of each state it needs ([Regional Children](https://github.com/Implan-Group/api/wiki/Regional-Children))
4. Combines each model's regions ([Combine Regions](https://github.com/Implan-Group/api/wiki/Combine-Regions)) and waits for each model to build ([Get User Region](https://github.com/Implan-Group/api/wiki/Get-User-Region))
5. Finds or creates the folder ([Get Folders](https://github.com/Implan-Group/api/wiki/Get-Folders), [Create Folder](https://github.com/Implan-Group/api/wiki/Create-Folder))
6. For each region, creates a project ([Create Project](https://github.com/Implan-Group/api/wiki/Create-Project)), adds the events ([Create Event](https://github.com/Implan-Group/api/wiki/Create-Event)) and one group ([Create Group](https://github.com/Implan-Group/api/wiki/Create-Group)), runs it ([Run Impact Analysis](https://github.com/Implan-Group/api/wiki/Run-Impact-Analysis), [Get Impact Status](https://github.com/Implan-Group/api/wiki/Get-Impact-Status)), and saves the reports ([Impact Results](https://github.com/Implan-Group/api/wiki/Impact-Results))
7. Creates one more project with a group for every region, and runs it the same way
