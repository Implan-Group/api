# ImpactApi - Identifiers Workflow
- Finds every id the other workflows need, an Aggregation Scheme, a Dataset, a Household Set, and Industry Codes, by asking the API rather than copying numbers from an example. It does this for the United States, Canada, and International data, and prints what it chose.
- [Getting Started](https://github.com/Implan-Group/api/wiki/Getting-Started)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account

---
## 🔽 Why resolve the ids every run
- The ids are not stable over time. IMPLAN publishes a new data year every year, and a new Industry Set when the industry classification changes, and the defaults move with them. An id written into a script keeps analyzing old data long after it should
- The ids are not portable between schemes
	- A Dataset id belongs to one Aggregation Scheme. The same number means nothing in another scheme
	- The Dataset list is not ordered by year, and the default is often last. Take the entry flagged `isDefault` rather than the first or the last
	- An Industry Code means a different industry in a different Industry Set. Full-service restaurants is 509 in the 546 set and 491 in the 528 set, so a code copied from an old example can analyze the wrong industry without any error
- Resolving them costs a handful of GET requests. Do it at the start of a run and pass the result along

---
## 🔽 The rules the samples follow
- United States
	- The Industry Set flagged `isDefault` in [Get Industry Sets](https://github.com/Implan-Group/api/wiki/Get-Industry-Sets) is the current one, and its `defaultAggregationSchemeId` is the Aggregation Scheme to use
	- The Dataset is the one flagged `isDefault` in [Dataset by Aggregation Scheme](https://github.com/Implan-Group/api/wiki/Dataset-by-Aggregation-Scheme) for that scheme
	- The Household Set is the first entry of the scheme's `householdSetIds`
- Canada and International
	- Only the United States Industry Set carries the `isDefault` flag. For these two, list the [Aggregation Schemes](https://github.com/Implan-Group/api/wiki/Aggregation-Schemes), keep the ones whose `mapCode` is `CAN` or `INTL` and whose description contains `Unaggregated`, and take the one with the highest `industrySetId`, which is the newest vintage. Then take that scheme's default Dataset and first Household Set, as for the United States
	- Each scheme lists its own Household Sets, so read the Household Set from the scheme you chose rather than carrying one between schemes
- Industries
	- Look an industry up by description as well as by code, and stop if the two disagree. A code that has moved between Industry Sets is caught here instead of in the results
	- [Industry Codes by Aggregation Scheme](https://github.com/Implan-Group/api/wiki/Industry-Codes-by-Aggregation-Scheme) lists the codes an Event in that scheme may use. An aggregated scheme has fewer codes than its Industry Set
- The Dollar Year is the current calendar year, computed when the workflow runs

---
## 🔽 Canadian and International data
- Two Canadian Industry Sets are in use, the 235-industry set and the newer 236-industry set. The rule above picks the newer one; pick the other by description if your work needs it
- Region types filter differently for Canadian data: `State` returns Provinces and `County` returns Economic Regions ([Get Region Types](https://github.com/Implan-Group/api/wiki/Get-Region-Types), [Regional Children](https://github.com/Implan-Group/api/wiki/Regional-Children))
- Not every data product is available outside the United States
	- Environmental data, for Regions and for impact results, is available only for United States data
	- Occupation data is available for United States and Canadian data, through separate Canadian routes such as `ImpactOccupationCanada` ([Results - Occupation](https://github.com/Implan-Group/api/wiki/Results---Occupation)). It is not available for International data
- If the Aggregation Schemes list has no Unaggregated scheme for a map code, as for an account without Canadian or International data, the workflow says so and carries on

---
## 🔽 Run it
- Run the `identifiers` workflow from the C#, Python, or R folder. Each folder's README gives the exact command
- It reads only. Nothing is created in your account

---
## 🔽 What it does
1. Resolves the current United States Industry Set, Aggregation Scheme, Dataset, and Household Set
2. Shows the lists those came from
	- Every Industry Set, with the default marked ([Get Industry Sets](https://github.com/Implan-Group/api/wiki/Get-Industry-Sets))
	- The chosen scheme, read back by id to show its Industry Set, map code, and status, which must be `Complete` before the scheme can be used ([Aggregation Scheme by Id](https://github.com/Implan-Group/api/wiki/Aggregation-Scheme-by-Id))
	- The scheme's Datasets, with the default marked ([Dataset by Aggregation Scheme](https://github.com/Implan-Group/api/wiki/Dataset-by-Aggregation-Scheme)), compared with the unscoped Datasets list, which answers for the default scheme without saying which ([Dataset by Id](https://github.com/Implan-Group/api/wiki/Dataset-by-Id))
3. Looks up industries: the codes in the scheme, the codes in its Industry Set, code 1 checked against `Oilseed farming`, and Full-service restaurants found by name ([Industry Codes by Aggregation Scheme](https://github.com/Implan-Group/api/wiki/Industry-Codes-by-Aggregation-Scheme), [Industry Codes by Industry Set](https://github.com/Implan-Group/api/wiki/Industry-Codes-by-Industry-Set))
4. Lists the Region Types the region filters accept ([Get Region Types](https://github.com/Implan-Group/api/wiki/Get-Region-Types))
5. Resolves the same identifiers for Canada and International, so the three sit side by side
