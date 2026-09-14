# Impact API sample code

Working examples of the IMPLAN Impact API in three languages. Every language folder contains the same set of workflows, written the way that language is normally written, using the same example data, so you can pick the language you know and compare results across them.

The API itself is documented in the [wiki](https://github.com/Implan-Group/api/wiki). These samples show how the endpoints fit together; the wiki is the contract.

## Pick a language

| Folder | Language | Start here |
| --- | --- | --- |
| [CSharp](CSharp/) | C# console application | [CSharp/README.md](CSharp/README.md) |
| [Python](Python/) | Python scripts | [Python/README.md](Python/README.md) |
| [R](R/) | R scripts | [R/README.md](R/README.md) |

Each README tells you what to install, how to configure your credentials, how to run each workflow, and what you should see.

## The workflows

The wiki's [Getting Started](https://github.com/Implan-Group/api/wiki/Getting-Started) page describes the Impact API as one ten-step process. Workflows 1 through 7 are that process cut into runnable pieces, in the order you would use them. Workflows 8 through 12 are larger or more specialized examples that build on them.

| # | Workflow | What it shows | Getting Started steps |
| --- | --- | --- | --- |
| 1 | Authentication | Obtain a bearer token, cache it, and verify it. | 1 |
| 2 | Identifiers | Discover the current default Aggregation Scheme, Dataset, Household Set, and Industry Codes from the API instead of hardcoding them. | 2, 4 |
| 3 | Regions | Walk the region hierarchy: top level, states, counties, a single region, and your own combined regions. | 3 |
| 4 | CombineRegions | Combine two counties into one region and wait for its model to build. | 3 |
| 5 | CreateProject | Create a project, add two events, add one group, the minimum runnable project. | 5, 6, 7 |
| 6 | MultiEventToMultiGroup | Apply the same events to several states, one group per state. | 6, 7 |
| 7 | RunImpactAnalysis | Run a project, wait for it correctly, and download the five standard CSV reports. | 8, 9, 10 |
| 8 | BulkFromCsv | Build regions, projects, events, and groups from CSV input files, run them all, and save the results. | all |
| 9 | RegionalExports | Download a regional data export for many regions at once without tripping the rate limits. | 3 |
| 10 | ImportEvents | Fill a project from the official IMPLAN Event Template workbook in one upload. | 6, 7 |
| 11 | MrioProject | Multi-regional input-output: an event in one state, effects reported in another. | 5 through 10 |
| 12 | AdvancedEvents | Industry Contribution Analysis and Industry Spending Pattern events, tagged, with results filtered by tag. | 6 through 10 |

Every workflow file is named for its row in this table, spelled in that language's style (`CreateProjectWorkflow.cs`, `create_project_workflow.py`, `create_project_workflow.R`), and every API call in the code names the wiki page it comes from.

## Before you run anything

- You need an IMPLAN subscription with API access. Contact <support@implan.com> to add it.
- Workflows 4 through 8 and 10 through 12 create real objects in your IMPLAN account (regions, projects, events, groups, impact runs). Each one prints what it created so you can find and delete it in IMPLAN Cloud.
- The API has rate limits, listed on the wiki [Home](https://github.com/Implan-Group/api/wiki) page. The samples respect them; if you adapt one to loop over many regions, keep the pauses.

## Contributing

The rules the samples follow, the commenting standard, the README template, and the full specification of each workflow are in [CLAUDE.md](../CLAUDE.md) at the repository root. Read it before changing or adding a sample, and add any new workflow to every language.
