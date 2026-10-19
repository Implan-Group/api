# IMPLAN Impact API: C# samples

Twelve runnable workflows against the IMPLAN Impact API, written as an ordinary
.NET console application with one dependency. The same workflows exist in Python
and R; see [sampleCode/README.md](../README.md) for the full set and what each one
does.

The API itself is documented in the [wiki](https://github.com/Implan-Group/api/wiki).
These samples show how the endpoints fit together; the wiki is the contract.

## Prerequisites

- **The .NET 10 SDK.** Verified on 10.0.402, 2026-10-16.
  Download it from [dotnet.microsoft.com/download](https://dotnet.microsoft.com/download).
  Check what you have:

      dotnet --version

  Anything starting with `10.` works. The SDK includes everything needed to build
  and run from the command line, with no editor required.

- **An IMPLAN subscription with API access.** The samples sign in with your normal
  IMPLAN credentials, but API access is a separate entitlement. If a login that
  works at app.implan.com is refused here, contact support@implan.com or your
  Customer Success Manager.

- **An editor**, optional but recommended.
  [Visual Studio 2026 Community](https://visualstudio.microsoft.com/vs/community/),
  [JetBrains Rider](https://www.jetbrains.com/rider/), or
  [Visual Studio Code](https://code.visualstudio.com/) with the
  [C# Dev Kit](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csdevkit).
  Open `ImplanApiSamples.sln`.

## Install dependencies

From this folder. There is nothing to install by hand: `dotnet build` restores the
one package the samples use.

    dotnet build

[RestSharp](https://restsharp.dev/) 114.0.0 is the only third-party dependency.
Everything else, including reading the `.env` file and parsing the command line,
comes from the base class library, so there is less to read that is not about the
API.

## Configure

Copy the example file and fill in your IMPLAN username and password.

    copy .env.example .env        # Windows
    cp .env.example .env          # macOS, Linux

Keep the double quotes around each value. Unquoted, the Python sample cuts a value
short at a space followed by `#`, which would break a password containing one.

`.env` is gitignored. It holds a working login, so treat it the way you would treat
the password itself. A real environment variable of the same name wins over the
file, which is how to supply credentials in CI without writing them to disk.

Three things get written next to the project file as you run the samples, all
gitignored:

| Path | What it is |
| --- | --- |
| `implan_auth.jwt` | The cached bearer token. Valid 24 hours and reused automatically. Delete it to force a fresh sign-in. |
| `logs/` | One file per day, with every request and response. The `Authorization` header is redacted. |
| `reports/` | Exported CSV reports and regional data downloads. |

Those paths are found by walking up from the running assembly to the folder holding
the `.csproj`, so they land in the same place whether you run with `dotnet run` or
start the built executable out of `bin/`.

## Run

One workflow at a time, in this order the first time through. Everything after
`--` is passed to the sample rather than to the `dotnet` command.

    dotnet run -- --list                       # every workflow, with a description

    dotnet run -- authentication               # 1  start here
    dotnet run -- identifiers                  # 2
    dotnet run -- regions                      # 3
    dotnet run -- combine-regions              # 4  creates a region
    dotnet run -- create-project               # 5  creates a project
    dotnet run -- run-impact-analysis          # 7  runs your most recent project
    dotnet run -- multi-event-to-multi-group   # 6

Workflows 1 through 3 only read. Everything from 4 on creates real objects in your
IMPLAN account, and each prints what it made so you can delete it afterwards.

`run-impact-analysis` uses your most recent project when you do not name one. To
run a specific project, pass its id, which `create-project` prints when it finishes:

    dotnet run -- run-impact-analysis --project-id 00000000-0000-0000-0000-000000000000

The extended workflows:

    dotnet run -- bulk-from-csv                # 8  builds from data/*.csv
    dotnet run -- regional-exports             # 9  ten MSAs by default
    dotnet run -- import-events                # 10 uploads data/event_template.xlsx
    dotnet run -- mrio-project                 # 11
    dotnet run -- advanced-events              # 12

Useful options:

| Option | Applies to | What it does |
| --- | --- | --- |
| `--project-id` | 6, 7 | Work in an existing project instead of creating one |
| `--map-code US\|CAN\|INTL` | 5 | Build a Canadian or international project |
| `--region-type` | 9 | `Msa`, `County`, `State`, and so on |
| `--export-name` | 9 | Any report from the wiki's Regional Data Exports section |
| `--limit 0` | 9 | Process every region rather than the first ten |
| `--workbook <path>` | 10 | Upload your own filled Event Template instead of the example |

The process returns an exit code, so a scheduled job can tell what went wrong:
0 success, 2 authentication, 3 the API refused the request, 4 a problem with the
input or the account, 5 the API could not be reached, 130 interrupted. Only 5 is
worth retrying unattended; it means nothing answered, usually the network, a VPN,
or a wrong `IMPLAN_API_URL`, rather than anything wrong with the request.

## Run the tests

From this folder:

    dotnet test --project Tests

The tests are an xUnit v3 project in `Tests/`, part of `ImplanApiSamples.sln`, so
Visual Studio and Rider list them in their test explorers too. xUnit v3 runs on
Microsoft.Testing.Platform, and `global.json` in this folder switches `dotnet test`
over to it, which the .NET 10 SDK requires.

They need no network and no credentials: every request goes to a scripted
`HttpMessageHandler`, which `ApiClient` accepts in place of the real one, so the
client runs its own retries, token refresh, logging, and error handling against
answers that never leave the machine.

They cover the places where C#, System.Text.Json, RestSharp, or the sample's own
plumbing could quietly do something other than what this API needs: a filter that
has to repeat rather than join with commas, a one-element array that must stay an
array, the growth report's five arrays surviving as `[]`, a GET that keeps its body,
the bearer token staying out of the log, a response field the sample has never seen
still being read, an error arriving with its problem details, a 401 refreshing the
token once, a token that arrives as a quoted JSON string, and the plain-text impact
status. They also cover the trap that matters most with RestSharp: it marks every
status other than 2xx and 404 as a failed request, so a 409 must still arrive as an
API error and not as "could not reach the API". Run them after changing anything
under `Services/` or `Models/`.

## What you should see

Each workflow narrates itself as numbered steps:

    IMPLAN Impact API sample: create-project
    API: https://api.implan.com

    Step 1: resolve the identifiers
    -------------------------------
    Resolved identifiers from the API:
      Map code:          US
      Industry Set:      12 - 528 Industries (latest US)
      Aggregation Scheme:14 - 528 Unaggregated
      Dataset:           124 - 2024
      Household Set:     1

    Step 2: create the Project
    --------------------------
      ImpactApi Sample - Create Project - 20260916-104233  id=...

    ...

    Done
    ----
    Project id:  8f1c...
    Group id:    2b77...

Reports land in `reports/<project title>/` as `.csv` files that open in Excel or
Sheets. A run takes a few minutes: the analysis itself is the slow part, and the
workflow polls every 15 seconds until it finishes.

## Run your own numbers

The workflows ship with example regions and events. To analyze your own, change the
inputs rather than the code: two workflows read everything they build from files you
can fill in yourself.

### Your events, from the Event Template (workflow 10)

The closest match to working in IMPLAN Cloud. Fill in IMPLAN's Event Template
workbook as you would for the Upload Template button, then upload it:

    dotnet run -- import-events --workbook "C:\path\to\your template.xlsx"

The workflow creates a project on the current default US Aggregation Scheme, uploads
the workbook, lists the Events and Groups it created, and, when the groups have
events attached, prints the command that runs the project. Without `--workbook` it
uploads the example in `data/event_template.xlsx`, a fictional timber panel plant in
Douglas County, Oregon.

The template is strict:

- Use the template for the project's Industry Set, which the workflow prints in
  Step 2. The US 528, US 546, Canada, and International templates are not
  interchangeable.
- Put each event type on its own sheet.
- Keep the formats the blank template shows: a `100%` cell means 100%, not 100.
- Give every event a value, and leave no formulas in the cells.
- On the Groups sheet, a state's FIPS code is five digits: `41000` for Oregon.
- Fill in the Group Events sheet. The import does not pair Events with Groups on
  its own, and a Group with no Events cannot be run.
- Keep one upload to about 500 events.

If the upload is refused, the error message names what to fix.

### The same events across many regions, from CSV files (workflow 8)

Edit the three files in `data/`, keeping their header rows:

| File | Columns | Each row is |
| --- | --- | --- |
| `state_based.csv` | `fips`, `region_description`, `model_name` | A state, by its five-digit FIPS code: `41000` for Oregon |
| `county_based.csv` | `fips`, `region_description`, `model_name` | A county, by its five-digit FIPS code: `41019` for Douglas County, Oregon |
| `demo_events.csv` | `Name`, `Code`, `Type`, `Value` | An event. `Type` is `Industry Output` or `Commodity Output`, `Code` is the industry or commodity code, and `Value` is the output in dollars |

- Rows that share a `model_name` are combined into one region. A `model_name` on
  only one row uses that state or county as it is.
- The region is found by `fips`. `region_description` is a label for you.
- Take codes from the current default Industry Set, which workflow 2 prints. The
  same code is a different industry in another set.
- Every event is applied to every region.
- A file you do not need can be left with only its header row.
- Excel drops leading zeros, so Alabama's `01000` becomes `1000`, which is not a
  place. Type such a code with an apostrophe in front, `'01000`, or edit the file in
  a text editor.

Then run:

    dotnet run -- bulk-from-csv

It builds the combined regions, reusing any it built on an earlier run, creates one
project per region and one holding them all, runs each, and saves four reports per
run under `reports/ImpactApi Sample - Bulk From CSV/`. The projects are filed in an
IMPLAN Cloud folder of the same name.

### Workflow 5 with your own industry, state, and amount

If you are comfortable changing a line of code, `Workflows/CreateProjectWorkflow.cs`
names its example near the top: `IndustryName` is the industry, spelled as IMPLAN
lists it, and `DefaultRegion` is the state for each map code. The amount is `Output
= 1_000_000.00` on the Industry Output event in Step 5. Change them, save, and run
`dotnet run -- create-project` again. The Industry Impact Analysis event beside it
keeps its example operating figures, so check those before relying on its results.

## Troubleshooting

Every failure from this API carries a `title`, a `detail`, and a `traceId`. The
samples print all three. Quote the `traceId` when you contact support: it
identifies the exact request in IMPLAN's logs.

| Status | What it means here | What to do |
| --- | --- | --- |
| **401** | The token is missing or expired. | The client refreshes once and retries by itself. If it repeats, delete `implan_auth.jwt` and run `authentication`. |
| **403** | Your subscription does not include the thing you asked for, or you do not have access to that project or region. | Check the `detail`. If it names Impact API, the entitlement is missing. |
| **404** | The thing does not exist. From the impact status endpoint it is expected for the first few seconds of a run, while the run's analyses are still being created, and the samples wait through it. A 404 that lasts more than a minute means the run never attached to a project, often because a Group was saved without a dollar year; that is terminal, so fix the Group and run again. | Check the id. Right after starting a run, poll again; past a minute, stop. |
| **409** | A name is already taken, an impact run has not finished, or a region's model is not built yet ("Model not built"). | The samples put a timestamp in every title to avoid the first. For the last, build the region, wait for it, and ask again. |
| **422** | The request is well formed but cannot be applied, for example an event type that is not valid in the project's Aggregation Scheme, or regions that nest inside one another. | Read the `detail`; it names the conflict. |
| **429** | You have exceeded a rate limit. | The client honors `Retry-After` and backs off. The bulk workflows also throttle themselves. If you hit this repeatedly, slow down rather than retrying harder: sustained overuse can get an account temporarily banned. |
| **503** from `POST /api/auth` | Either the authentication service is briefly unavailable, or API access has not been enabled on your account. | Wait a minute and try again. Repeat 503s point to the entitlement; ask your Customer Success Manager. |
| **503** from `GET /api/v1/region/user` | The region cache is being rebuilt, which happens on accounts with many custom schemes. | Use the scheme-scoped call instead, which the samples already do, or wait a few minutes. |

Rate limits, from the [wiki home page](https://github.com/Implan-Group/api/wiki):

| Endpoints | Limit |
| --- | --- |
| Industry Codes | 10 per minute |
| Datasets | 10 per minute |
| Region Models | 5 per minute |

The Region Models limit counts model builds, such as combining regions or building
an IMPLAN region's model. Reading regions and downloading exports do not count
against it. The two bulk workflows, `bulk-from-csv` and `regional-exports`, hold
every request to five a minute anyway. That is slower than the limit requires,
which is why a run over thousands of regions takes hours, but it keeps them simple
and safely inside the limit.

A report whose first line looks like JSON rather than a header row means the run
was not finished when it was read. `run-impact-analysis` checks for this in its
last step.

If `dotnet build` fails with a message about the target framework, the installed
SDK is older than .NET 10. `dotnet --list-sdks` shows what you have.

## Folder layout

| Folder | What is in it |
| --- | --- |
| `Workflows/` | One file per workflow. Start here; they read top to bottom. |
| `Endpoints/` | One static class per section of the wiki, wrapping the API calls. |
| `Models/` | The request and response shapes. |
| `Services/` | Configuration, authentication, the HTTP client, logging, JSON. |
| `data/` | Input files: the CSVs the bulk workflow reads, copied next to the executable on build, and the example Event Template. |
| `Tests/` | The xUnit tests, run with `dotnet test --project Tests`. No network, no credentials. |

`Services/ApiClient.cs` is the piece worth reading if you are writing your own
client: it holds the bearer token, the problem-details handling, the retry and
backoff, and the rate limiter, which are the parts that are the same for every
call.

Two details in there are worth calling out, because both are easy to get wrong:

- **`Query` is a list, not a dictionary.** Several filters are repeated parameters
  rather than one comma-separated value, so filtering on two regions means
  `regions=Oregon&regions=Wisconsin`. A dictionary keyed by name would silently
  keep only the last one.
- **`GetJson` and `GetText` accept a body.** That sounds wrong, and for most of the
  API it is, but the Estimated Growth Percentage report requires a JSON body on a
  GET. See `Endpoints/ImpactResults.cs`.

## Links

- [Impact API wiki](https://github.com/Implan-Group/api/wiki)
- [Authentication](https://github.com/Implan-Group/api/wiki/Authentication)
- [Getting Started](https://github.com/Implan-Group/api/wiki/Getting-Started)
- [All sample workflows](../README.md)
- [IMPLAN Support](https://support.implan.com)
- [Getting Started with the IMPLAN API](https://support.implan.com/hc/en-us/articles/47795231373595-Getting-Started-with-the-IMPLAN-API)

Licensed under the MIT License; see [LICENSE](../../LICENSE) at the repository root.
