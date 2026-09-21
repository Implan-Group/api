# IMPLAN Impact API: Python samples

Twelve runnable workflows against the IMPLAN Impact API, written in ordinary Python
with two dependencies. The same workflows exist in C# and R; see
[sampleCode/README.md](../README.md) for the full set and what each one does.

The API itself is documented in the [wiki](https://github.com/Implan-Group/api/wiki).
These samples show how the endpoints fit together; the wiki is the contract.

## Prerequisites

- **Python 3.11 or newer.** Verified on 3.14.3, 2026-09-16.
  Download it from [python.org/downloads](https://www.python.org/downloads/).
  Check what you have:

      python --version

  On macOS and Linux that may be `python3`. If the command is missing on Windows,
  reinstall and tick "Add python.exe to PATH".

- **An IMPLAN subscription with API access.** The samples sign in with your normal
  IMPLAN credentials, but API access is a separate entitlement. If a login that
  works at app.implan.com is refused here, contact support@implan.com or your
  Customer Success Manager.

- **An editor**, optional but recommended.
  [PyCharm Community](https://www.jetbrains.com/pycharm/download/) or
  [Visual Studio Code](https://code.visualstudio.com/) with the
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python).

## Install dependencies

From this folder. A virtual environment keeps these packages out of your system
Python, which is worth the two extra lines.

    python -m venv .venv

    .venv\Scripts\activate        # Windows
    source .venv/bin/activate     # macOS, Linux

    pip install -r requirements.txt

`requirements.txt` lists exactly two packages: `requests` for HTTP and
`python-dotenv` for reading the credentials file.

## Configure

Copy the example file and fill in your IMPLAN username and password.

    copy .env.example .env        # Windows
    cp .env.example .env          # macOS, Linux

`.env` is gitignored. It holds a working login, so treat it the way you would
treat the password itself.

Three things get written next to `main.py` as you run the samples, all gitignored:

| Path | What it is |
| --- | --- |
| `implan_auth.jwt` | The cached bearer token. Valid 24 hours and reused automatically. Delete it to force a fresh sign-in. |
| `logs/` | One file per day, with every request and response. The `Authorization` header is redacted. |
| `reports/` | Exported CSV reports and regional data downloads. |

## Run

One workflow at a time, in this order the first time through.

    python main.py --list                      # every workflow, with a description

    python main.py authentication              # 1  start here
    python main.py identifiers                 # 2
    python main.py regions                     # 3
    python main.py combine-regions             # 4  creates a region
    python main.py create-project              # 5  creates a project
    python main.py run-impact-analysis         # 6  runs your most recent project
    python main.py multi-event-to-multi-group  # 7

Workflows 1 through 3 only read. Everything from 4 on creates real objects in your
IMPLAN account, and each prints what it made so you can delete it afterwards.

`run-impact-analysis` uses your most recent project when you do not name one. To
run a specific project, pass its id, which `create-project` prints when it finishes:

    python main.py run-impact-analysis --project-id 00000000-0000-0000-0000-000000000000

The extended workflows:

    python main.py bulk-from-csv               # 8  builds from data/*.csv
    python main.py regional-exports            # 9  ten MSAs by default
    python main.py import-events               # 10 needs a filled Event Template
    python main.py mrio-project                # 11
    python main.py advanced-events             # 12

Useful options:

| Option | Applies to | What it does |
| --- | --- | --- |
| `--project-id` | 6, 7 | Work in an existing project instead of creating one |
| `--map-code US\|CAN\|INTL` | 5 | Build a Canadian or international project |
| `--region-type` | 9 | `Msa`, `County`, `State`, and so on |
| `--export-name` | 9 | Any report from the wiki's Regional Data Exports section |
| `--limit 0` | 9 | Process every region rather than the first ten |
| `--workbook <path>` | 10 | Point at your filled Event Template |

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

## Folder layout

| Folder | What is in it |
| --- | --- |
| `workflows/` | One file per workflow. Start here; they read top to bottom. |
| `endpoints/` | One module per section of the wiki, wrapping the API calls. |
| `models/` | The request and response shapes, as dataclasses. |
| `utilities/` | Configuration, authentication, the HTTP client, logging, JSON. |
| `data/` | Input files the bulk workflow reads. |

`utilities/rest.py` is the piece worth reading if you are writing your own client:
it holds the bearer token, the problem-details handling, the retry and backoff, and
the rate limiter, which are the parts that are the same for every call.

## Links

- [Impact API wiki](https://github.com/Implan-Group/api/wiki)
- [Authentication](https://github.com/Implan-Group/api/wiki/Authentication)
- [Getting Started](https://github.com/Implan-Group/api/wiki/Getting-Started)
- [All sample workflows](../README.md)
- [IMPLAN Support](https://support.implan.com)
- [Getting Started with the IMPLAN API](https://support.implan.com/hc/en-us/articles/47795231373595-Getting-Started-with-the-IMPLAN-API)

Licensed under the MIT License; see [LICENSE](../../LICENSE) at the repository root.
