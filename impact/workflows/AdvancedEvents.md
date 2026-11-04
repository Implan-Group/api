# ImpactApi - Advanced Events Workflow
- Adds the two event types analysts reach for after Industry Output, an Industry Contribution Analysis event and an Industry Spending Pattern event with an edited spending pattern, tags each one, and reads the results once per tag. One run answers two questions separately.
- [Events](https://github.com/Implan-Group/api/wiki/Events)
- Support: [ICA: Introduction to Industry Contribution Analysis](https://support.implan.com/hc/en-us/articles/360025854654), [Industry Spending Pattern Events](https://support.implan.com/hc/en-us/articles/360052212933), and [Event Tags](https://support.implan.com/hc/en-us/articles/4407853242139)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 Which event answers which question
- **Industry Output** asks what happens if new activity arrives: a new hotel, a new plant. The other workflows use it
- **Industry Contribution Analysis** (`IndustryContributionAnalysis`) asks how much of the economy already rests on an industry that is there now. It keeps the industry from buying from itself, so its own output is not counted twice. Use it for "the restaurant industry contributes this much to the state", never for a new restaurant
	- `output` is a dollar amount, and it must not exceed the industry's total output in the Region. Set `isOutputPercentage` to `true` to give a share from 0 to 1 instead, which avoids having to know that total
- **Industry Spending Pattern** (`IndustrySpendingPattern`) models a buyer rather than a producer. It spends the value through an industry's supply chain without adding any direct output of its own, which suits an organization whose own output is not what is being measured
	- `spendingPatternValueType` says how to read the value. `IntermediateExpenditure` spends the whole value across the pattern; `Output` treats it as the industry's total output and spends only the part that goes to intermediate inputs. This workflow uses `IntermediateExpenditure`
	- The pattern is a list of Commodities and the share of each dollar spent on them. Read the default pattern, change what you know better, and send the whole list back with the event
- [Event Types](https://github.com/Implan-Group/api/wiki/Event-Types) describes every type, and [Get Event Types](https://github.com/Implan-Group/api/wiki/Get-Event-Types) lists the ones a project accepts

---
## 🔽 Editing a spending pattern
- [Spending Pattern by Id](https://github.com/Implan-Group/api/wiki/Spending-Pattern-by-Id) returns an industry's default pattern for a Dataset
- This workflow raises the largest commodity's coefficient by 10% and marks it `isUserCoefficient`. That flag tells IMPLAN the number is yours rather than its own, so the change shows as yours in the project
- The rest of the list goes back unchanged. Send every commodity you want included, not only the ones you edited

---
## 🔽 Tags
- Each event takes a list of `tags`. Here the contribution event is tagged `contribution` and the spending event `spending`
- The results endpoints take an `eventTags` filter, so one run is read once per tag and each report holds only its own event
- Tag events by what they represent, such as construction against operations, and one project answers several questions

---
## 🔽 Run it
- Run the `advanced-events` workflow from the C#, Python, or R folder. Each folder's README gives the exact command
- It creates one project in your account and runs it. Delete the project in IMPLAN Cloud when you are done
- The reports are saved under `reports/Advanced Events-{runId}/`

---
## 🔽 What it does
1. Resolves the current default US Aggregation Scheme, Dataset, and Household Set
2. Creates the project, and stops unless the project accepts both event types ([Create Project](https://github.com/Implan-Group/api/wiki/Create-Project), [Get Event Types](https://github.com/Implan-Group/api/wiki/Get-Event-Types))
3. Adds an Industry Contribution Analysis event of $1,000,000 for Full-service restaurants, looked up by name, tagged `contribution` ([Create Event](https://github.com/Implan-Group/api/wiki/Create-Event))
4. Reads the default spending pattern for Oilseed farming in the resolved Dataset, and prints its five largest commodities ([Spending Pattern by Id](https://github.com/Implan-Group/api/wiki/Spending-Pattern-by-Id))
5. Raises the largest commodity's coefficient by 10% and marks it as yours
6. Adds an Industry Spending Pattern event of $1,000,000 that carries the edited pattern, tagged `spending` ([Create Event](https://github.com/Implan-Group/api/wiki/Create-Event))
7. Adds one Group for Oregon holding both events ([Regional Children](https://github.com/Implan-Group/api/wiki/Regional-Children), [Create Group](https://github.com/Implan-Group/api/wiki/Create-Group))
8. Runs the impact and waits for it to finish ([Run Impact Analysis](https://github.com/Implan-Group/api/wiki/Run-Impact-Analysis), [Get Impact Status](https://github.com/Implan-Group/api/wiki/Get-Impact-Status))
9. Reads the results by tag
	- Summary Economic Indicators once for each tag, with `eventTags` as a query filter ([Results - Summary Economic Indicators](https://github.com/Implan-Group/api/wiki/Results---Summary-Economic-Indicators))
	- Estimated Growth Percentage for the `spending` tag. This report is a GET that takes its filters as a JSON body, and every list in it must be present; send `[]` for a list you do not want to filter on ([Results - Estimated Growth Percentage](https://github.com/Implan-Group/api/wiki/Results---Estimated-Growth-Percentage))
