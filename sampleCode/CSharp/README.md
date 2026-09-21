# IMPLAN Impact API: C# samples

Twelve runnable workflows against the IMPLAN Impact API, written as an ordinary
.NET console application with one dependency. The same workflows exist in Python
and R; see [sampleCode/README.md](../README.md) for the full set and what each one
does.

The API itself is documented in the [wiki](https://github.com/Implan-Group/api/wiki).
These samples show how the endpoints fit together; the wiki is the contract.

## Prerequisites

- **The .NET 10 SDK.** Verified on 10.0.400, 2026-09-16.
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
    dotnet run -- run-impact-analysis          # 6  runs your most recent project
    dotnet run -- multi-event-to-multi-group   # 7

Workflows 1 through 3 only read. Everything from 4 on creates real objects in your
IMPLAN account, and each prints what it made so you can delete it afterwards.

`run-impact-analysis` uses your most recent project when you do not name one. To
run a specific project, pass its id, which `create-project` prints when it finishes:

    dotnet run -- run-impact-analysis --project-id 00000000-0000-0000-0000-000000000000

The extended workflows:

    dotnet run -- bulk-from-csv                # 8  builds from data/*.csv
    dotnet run -- regional-exports             # 9  ten MSAs by default
    dotnet run -- import-events                # 10 needs a filled Event Template
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
| `--workbook <path>` | 10 | Point at your filled Event Template |

The process returns an exit code, so a scheduled job can tell what went wrong: 0
success, 2 authentication, 3 the API refused the request, 4 a problem with the
input or the account, 130 interrupted.

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

## Troubleshooting

Every failure from this API carries a `title`, a `detail`, and a `traceId`. The
samples print all three. Quote the `traceId` when you contact support: it
identifies the exact request in IMPLAN's logs.

| Status | What it means here | What to do |
| --- | --- | --- |
| **401** | The token is missing or expired. | The client refreshes once and retries by itself. If it repeats, delete `implan_auth.jwt` and run `authentication`. |
| **403** | Your subscription does not include the thing you asked for, or you do not have access to that project or region. | Check the `detail`. If it names Impact API, the entitlement is missing. |
| **404** | The thing does not exist. From the impact status endpoint it means something more specific: the run never attached to a project, usually because a Group was saved without a dollar year. That is terminal; fix the Group and run again. | Check the id. Do not retry a 404 from status. |
| **409** | A name is already taken, or an impact run has not finished. | The samples put a timestamp in every title to avoid the first. |
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
| `data/` | Input files the bulk workflow reads, copied next to the executable on build. |

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
