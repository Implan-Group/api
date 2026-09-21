# IMPLAN Impact API: R samples

Twelve runnable workflows against the IMPLAN Impact API, written in ordinary R
with two packages. The same workflows exist in C# and Python; see
[sampleCode/README.md](../README.md) for the full set and what each one does.

The API itself is documented in the [wiki](https://github.com/Implan-Group/api/wiki).
These samples show how the endpoints fit together; the wiki is the contract.

## Prerequisites

- **R 4.1 or newer.** The samples use the native pipe `|>` and the `\(x)` lambda
  shorthand, both of which arrived in 4.1. Install it as described below.

- **An IMPLAN subscription with API access.** The samples sign in with your normal
  IMPLAN credentials, but API access is a separate entitlement. If a login that
  works at app.implan.com is refused here, contact support@implan.com or your
  Customer Success Manager.

- **An editor**, optional but recommended. [RStudio
  Desktop](https://posit.co/download/rstudio-desktop/) is the usual choice and is
  free. [Visual Studio Code](https://code.visualstudio.com/) with the [R
  extension](https://marketplace.visualstudio.com/items?itemName=REditorSupport.r)
  also works.

### Installing R on Windows

The quickest route is winget, which ships with Windows 11 and recent Windows 10.
From PowerShell:

```powershell
winget install --id RProject.R --source winget
```

RStudio, if you want the editor as well:

```powershell
winget install --id Posit.RStudio --source winget
```

You do **not** need Rtools for these samples. Rtools is the C and Fortran
toolchain used to build packages from source, and both packages the samples need
are published as Windows binaries. Install it only if you later want a package
that has no binary:

```powershell
winget install --id RProject.Rtools --source winget
```

**Put R on your PATH.** The R installer does not do this, so `Rscript` will not be
found in a new shell until you add it. Check what the installer put down, then add
that folder to your user PATH and open a new shell:

```powershell
(Get-ChildItem 'C:\Program Files\R' -Directory | Sort-Object Name -Descending | Select-Object -First 1).FullName
```

```powershell
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';C:\Program Files\R\R-4.6.1\bin\x64', 'User')
```

Change the version in that path to whatever the first command printed. Then open a
new PowerShell window and confirm:

```powershell
Rscript --version
```

RStudio finds R by itself and does not need the PATH entry. The PATH is only for
running `Rscript main.R` from a terminal.

### Installing R on macOS and Linux

macOS, with [Homebrew](https://brew.sh):

```bash
brew install --cask r
```

Debian and Ubuntu:

```bash
sudo apt-get update && sudo apt-get install -y r-base
```

The version in a distribution's own repository is often older than 4.1. If
`R --version` reports anything earlier, follow the CRAN instructions for your
distribution at [cran.r-project.org/bin/linux](https://cran.r-project.org/bin/linux/).
Any platform can also install from [cran.r-project.org](https://cran.r-project.org).

## Install dependencies

From this folder, once:

```bash
Rscript packages.R
```

That installs two packages from CRAN and nothing else:

| Package | What it does here |
| --- | --- |
| `httr2` | The HTTP client. The bearer token, the retries, the rate limiting, and the error handling all come from it. Version 1.2.0 or newer. |
| `jsonlite` | Reading and writing JSON. |

`curl` arrives with `httr2` and is used directly in one place, for the multipart
upload in the ImportEvents workflow.

Reading the `.env` file, parsing the command line, and reading the CSV inputs are
all done with base R, so there is less to install and less to read that is not
about the API.

## Configure

Copy the example file and fill in your IMPLAN username and password.

```powershell
copy .env.example .env
```

```bash
cp .env.example .env
```

`.env` is gitignored. It holds a working login, so treat it the way you would treat
the password itself. A real environment variable of the same name wins over the
file, which is how to supply credentials in CI without writing them to disk.

Three things get written next to `main.R` as you run the samples, all gitignored:

| Path | What it is |
| --- | --- |
| `implan_auth.jwt` | The cached bearer token. Valid 24 hours and reused automatically. Delete it to force a fresh sign-in. |
| `logs/` | One file per day, with every request and response. The `Authorization` header is redacted. |
| `reports/` | Exported CSV reports and regional data downloads. |

## Run

One workflow at a time, in this order the first time through.

```bash
Rscript main.R --list
```

```bash
Rscript main.R authentication
```

Then `identifiers`, `regions`, `combine-regions`, `create-project`,
`run-impact-analysis`, and `multi-event-to-multi-group`, in that order.

Workflows 1 through 3 only read. Everything from 4 on creates real objects in your
IMPLAN account, and each prints what it made so you can delete it afterwards.

`run-impact-analysis` uses your most recent project when you do not name one. To
run a specific project, pass its id, which `create-project` prints when it
finishes:

```bash
Rscript main.R run-impact-analysis --project-id 00000000-0000-0000-0000-000000000000
```

The extended workflows are `bulk-from-csv`, `regional-exports`, `import-events`,
`mrio-project`, and `advanced-events`.

Useful options:

| Option | Applies to | What it does |
| --- | --- | --- |
| `--project-id` | 6, 7 | Work in an existing project instead of creating one |
| `--map-code US\|CAN\|INTL` | 5 | Build a Canadian or international project |
| `--region-type` | 9 | `Msa`, `County`, `State`, and so on |
| `--export-name` | 9 | Any report from the wiki's Regional Data Exports section |
| `--limit 0` | 9 | Process every region rather than the first ten |
| `--workbook <path>` | 10 | Point at your filled Event Template |

From RStudio or an R console, source the entry point once and then call a workflow
by name. This is the better way to explore, because the objects stay in your
workspace afterwards:

```r
source("main.R")
run_workflow("regions")
run_workflow("run-impact-analysis", "--project-id", "00000000-0000-0000-0000-000000000000")
```

`Rscript main.R` returns an exit code, so a scheduled job can tell what went wrong:
0 success, 2 authentication, 3 the API refused the request, 4 a problem with the
input or the account.

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
| **429** | You have exceeded a rate limit. | `req_retry()` honors `Retry-After` and backs off. The bulk workflows also throttle themselves with `req_throttle()`. If you hit this repeatedly, slow down rather than retrying harder: sustained overuse can get an account temporarily banned. |
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

Two R-specific failures are worth naming:

- **`could not find function "request"`** means `httr2` is not installed or is too
  old. Run `Rscript packages.R`.
- **`Rscript` is not recognized** means R is installed but is not on your PATH. See
  the Windows section above.

## Folder layout

| Folder | What is in it |
| --- | --- |
| `workflows/` | One file per workflow. Start here; they read top to bottom. |
| `endpoints/` | One file per section of the wiki, wrapping the API calls. |
| `models/` | The request and response shapes, as constructor and reader functions. |
| `utilities/` | Configuration, authentication, the HTTP client, logging, JSON. |
| `data/` | Input files the bulk workflow reads. |

`utilities/rest.R` is the piece worth reading if you are writing your own client.
It holds the bearer token, the problem-details handling, the retry and backoff,
and the rate limiter, which are the parts that are the same for every call.

Three details in there are worth calling out, because each is easy to get wrong:

- **Repeated query parameters.** Several filters are repeated parameters rather
  than one comma-separated value, so filtering on two regions means
  `regions=Oregon&regions=Wisconsin`. That is `req_url_query(.multi = "explode")`.
- **A JSON body on a GET.** That sounds wrong, and for most of the API it is, but
  the Estimated Growth Percentage report requires it. `req_body_json()` switches
  the method to POST, so `req_method("GET")` has to come after it.
- **Arrays that must stay arrays.** The bodies are written with
  `auto_unbox = TRUE`, which turns a one-element vector into a JSON scalar. One
  tag has to go out as `["capital"]`, so `ARRAY_FIELDS` in
  `utilities/json_helper.R` names the fields that are forced back to arrays.

The code is plain functions, grouped by file, with S3 for the `describe()`
one-liners the workflows print. There are no S4 or R6 classes: an environment is
used in the two places something has to be mutable, the client and the region
cache, and everything else is a list.

## Links

- [Impact API wiki](https://github.com/Implan-Group/api/wiki)
- [Authentication](https://github.com/Implan-Group/api/wiki/Authentication)
- [Getting Started](https://github.com/Implan-Group/api/wiki/Getting-Started)
- [All sample workflows](../README.md)
- [IMPLAN Support](https://support.implan.com)
- [How to Use the IMPLAN API with R: Obtaining Your API Token](https://support.implan.com/hc/en-us/articles/48279952909467)
- [Getting Started with the IMPLAN API](https://support.implan.com/hc/en-us/articles/47795231373595-Getting-Started-with-the-IMPLAN-API)

Licensed under the MIT License; see [LICENSE](../../LICENSE) at the repository root.
