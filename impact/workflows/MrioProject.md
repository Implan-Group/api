# ImpactApi - MRIO Project Workflow
- Runs a multi-regional input-output (MRIO) analysis, where activity in one Region shows up as effects in another. It places $10,000,000 of Full-service restaurant output in Oregon, links Wisconsin into the same project, and reports each state separately.
- [Projects](https://github.com/Implan-Group/api/wiki/Projects)
- Support: [MRIO: Introduction to Multi-Regional Input-Output Analysis](https://support.implan.com/hc/en-us/articles/115009713448)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 What MRIO changes
- An ordinary project treats each Region on its own. A restaurant in Oregon that buys supplies from Wisconsin shows Oregon's supply chain, and the Wisconsin purchases leave the model and are never counted
- With `isMrio` set to `true` on the project, IMPLAN follows that demand into the other Regions in the same project, so Wisconsin shows indirect and induced effects from activity that happened only in Oregon
- `isMrio` is set when the project is created ([Create Project](https://github.com/Implan-Group/api/wiki/Create-Project))
- Not every Region can take part. Each Region carries `isMrioAllowed`; check it before building the project ([Regions](https://github.com/Implan-Group/api/wiki/Regions))
- Every Region you want results for needs a Group in the project, including a Region with no activity of its own. That Group is where its spillover is reported

---
## 🔽 Why Wisconsin carries a tiny copy of the event
- The cleaner illustration is a Wisconsin Group with no events, but the API requires every Group to carry at least one event
- So the Wisconsin Group carries the Oregon event with a `scalingFactor` of `0.01`. Its own direct effect is a hundredth of Oregon's, and nearly everything reported for Wisconsin is spillover from Oregon
- A scaling factor multiplies the event: `1` leaves it as entered, and `0.01` is one percent of it

---
## 🔽 Run it
- Run the `mrio-project` workflow from the C#, Python, or R folder. Each folder's README gives the exact command
- It creates one project in your account and runs it. Delete the project in IMPLAN Cloud when you are done
- The two reports are saved under `reports/MRIO-{runId}/`. Compare them: the Wisconsin report is the effect an ordinary project would have lost

---
## 🔽 What it does
1. Resolves the current default US Aggregation Scheme, Dataset, and Household Set
2. Finds Oregon and Wisconsin among the states, and stops if either does not allow MRIO ([Regional Children](https://github.com/Implan-Group/api/wiki/Regional-Children))
3. Creates the project with `isMrio` set to `true` ([Create Project](https://github.com/Implan-Group/api/wiki/Create-Project))
4. Looks up Full-service restaurants by name and adds one Industry Output event of $10,000,000 ([Industry Codes by Aggregation Scheme](https://github.com/Implan-Group/api/wiki/Industry-Codes-by-Aggregation-Scheme), [Create Event](https://github.com/Implan-Group/api/wiki/Create-Event))
5. Adds a Group for Oregon with the event, and a Group for Wisconsin with the event scaled to `0.01` ([Create Group](https://github.com/Implan-Group/api/wiki/Create-Group))
6. Runs the impact and waits for it to finish ([Run Impact Analysis](https://github.com/Implan-Group/api/wiki/Run-Impact-Analysis), [Get Impact Status](https://github.com/Implan-Group/api/wiki/Get-Impact-Status))
7. Downloads Summary Economic Indicators twice, filtered to each state ([Results - Summary Economic Indicators](https://github.com/Implan-Group/api/wiki/Results---Summary-Economic-Indicators))
	- The `regions` filter must include the data year, as the report writes it: `Oregon (2024)`, not `Oregon`. The bare name is refused with a `400 Bad Request`
