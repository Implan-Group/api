# Canada Data Workflow Considerations
This document is a supplement to the [Batch ReadMe](https://github.com/Implan-Group/api/blob/main/batch/readme.md#overview) and contains workflow instructions and considerations for those seeking to work with Canadian data.
This document describes the basic batch IMPLAN workflow as it relates the IMPLAN's Batch API. More detail on additional IMPLAN workflow topics can be found on [support.implan.com](https://support.implan.com/hc/en-us).

## Overview
### Authorization
Please note that all API endpoint requests presented in this document require a bearer token. Please see the [authentication](https://github.com/Implan-Group/api/blob/main/batch/readme.md#general-authentication-architecture) section of the ReadMe to review authentication steps.

### Domain References
See the [Development Variables](https://github.com/Implan-Group/api/blob/main/batch/readme.md#development-variables) section of the ReadMe for information regarding the `{{api_domain}}` variables used in this document.

## Analysis Consideration
Batch Impact analyses utilize industry output methodology.

## Workflow
### Find a Region and Industry to Study
All region data in IMPLAN are unique based on the Aggregation Scheme, Dataset (data year), and geographic demarcation. 

### Aggregation Schemes Endpoint (Get)
This endpoint will return a list of aggregation schemes available for use. For Canadian Batch API analyses, only aggregation schemes with a `MapCode` of `CAN` and an `unaggregated` description are valid.
#### Parameters
* Bearer Token
* IndustrySetId (optional filter)
#### Response (List)
* Id (Aggregation Scheme Id)
* Description
* Industry Set Id
* Household Set Ids []
* Map Code
* Status
#### Sample Response
```
[   …
	{
		"id": 12,
		"description": "235 Unaggregated Canada",
		"industrySetId": 10,
		"householdSetIds": [
                    4
		],
		"mapCode": "CAN",
		"status": "Complete"
	},
    …
]
```
#### Endpoint
**GET {{api_domain}}/{{env}}/api/v1/aggregationschemes?industrySetId={{industrySetId}}**


### Dataset Endpoint (Get)
Use the desired Aggregation Scheme Id with this endpoint to pull a list of available datasets.
#### Parameters
* Bearer Token
* Aggregation Scheme Id (URL Parameter)
#### Response (List)
* Data Set ID (Number)
* Data Set Description (Text)
* Default Data Set (Boolean - only 1 record in the list should be true)
#### Sample Response
```
[
	{
		"id": 86,
		"description": "2017",
		"isDefault": false
	},
	{
		"id": 88,
		"description": "2018",
		"isDefault": false
	},
	{
		"id": 89,
		"description": "2019",
		"isDefault": false
	},
	{
		"id": 93,
		"description": "2020",
		"isDefault": true
	}
]
```
#### Endpoint
**GET {{api_domain}}/{{env}}/api/v1/datasets/{{aggregationSchemeId}}**

### Region Model Endpoint (Get)
This endpoint will return a list of models available for Batch Impact analysis. A `datasetId` from the previously mentioned endpoint is required. The endpoint response will include a list of Region Names, Types, and Model IDs. The response may be cached.
#### Parameters
* Bearer Token
* Data Set Id
### Response (List)
* Model Id
* Region Type Id
  * 2 = State (Province for Canada Data)
  * 3 = MSA (Unused for Canada Data)
  * 4 = County (Unused for Canada Data)
* Region Name
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/models/{{datasetId}}**
### Sample Response
```
[
    {
        "hashId": "EgxYRX6Xav",
        "urid": 1815849,
        "userModelId": null,
        "description": "Nunavut",
        "modelId": 13922,
        "modelBuildStatus": "Complete",
        "employment": 20457.515130996704,
        "output": 7718418875.19136,
        "valueAdded": 4065133039.2314124,
        "aggregationSchemeId": 12,
        "datasetId": 93,
        "datasetDescription": "2020",
        "fipsCode": "14",
        "provinceCode": "62",
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": false,
        "regionTypeDescription": "State",
        "geoId": "62",
        "isMrioAllowed": true
    },
    {
        "hashId": "k4bKl80LVO",
        "urid": 1815833,
        "userModelId": null,
        "description": "Newfoundland",
        "modelId": 13928,
        "modelBuildStatus": "Complete",
        "employment": 200865.97679519653,
        "output": 52765471380.91922,
        "valueAdded": 32176045083.19381,
        "aggregationSchemeId": 12,
        "datasetId": 93,
        "datasetDescription": "2020",
        "fipsCode": "05",
        "provinceCode": "10",
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": false,
        "regionTypeDescription": "State",
        "geoId": "10",
        "isMrioAllowed": true
    },
    {
        "hashId": "4Ba4N4AeVp",
        "urid": 1818171,
        "userModelId": null,
        "description": "British Columbia",
        "modelId": 14042,
        "modelBuildStatus": "Complete",
        "employment": 2450467.4931640625,
        "output": 533364910349.4883,
        "valueAdded": 307411073455.7796,
        "aggregationSchemeId": 12,
        "datasetId": 93,
        "datasetDescription": "2020",
        "fipsCode": "02",
        "provinceCode": "59",
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": false,
        "regionTypeDescription": "State",
        "geoId": "59",
        "isMrioAllowed": true
    },...
]
```
### Industry Codes (Get)
Use the following endpoint to pull a list of industries that can be utilized for your analysis. Batch Impact Requests created later will require reference to one or more of the industry codes (`code`) returned here.
#### Parameters
* Bearer Token
* Aggregation Scheme Id (URL Parameter)
#### Response (List)
* Industry Id
* Industry Code
* Industry Description
#### Sample Response
```
[
	{
		"id": 5221,
		"code": 1,
		"description": "Crop production (except cannabis, greenhouse, nursery and floriculture production)"
	},
	{
		"id": 5222,
		"code": 2,
	"description": "Greenhouse, nursery and floriculture production (except cannabis)"
	}, …
]
```
#### Endpoint
**GET {{api_domain}}/{{env}}/api/v1/IndustryCodes/{{aggregationSchemeId}}**


### Run an Impact and Get Results
With the data from the prior endpoints in hand, utilize one of the two endpoints below to run an impact analysis.

### Instant Impact (Get)
This endpoint generates an impact analysis for a single Canadian region and industry combination.
#### Required Parameters:
* Bearer Token
* Model Id (Returned in Region Model Endpoint)
* Industry Code (Returned in Industry Code Endpoint)
* Output Event Value
#### Response - The API response when the impact analysis is complete will provide Direct, Indirect, Induced, and Total estimates for the following outputs:
* Output
* Employment
* Employee Compensation
* Proprietor Income
* Other Property Income
* Other Taxes on Production
* Total Taxes
#### Sample Response
```
{
    "requestModelId": 14332,
    "requestIndustryCode": 1,
    "directOutput": 10000000.0,
    "indirectOutput": 4595783.390503161,
    "inducedOutput": 3538457.139683301,
    "totalOutput": 18134240.530186463,
    "directEmployeeCompensation": 1321413.9991816378,
    "indirectEmployeeCompensation": 1244419.638699429,
    "inducedEmployeeCompensation": 872226.9982893274,
    "totalEmployeeCompensation": 3438060.636170394,
    "directProprietorIncome": 1260509.9487290196,
    "indirectProprietorIncome": 279215.78169577895,
    "inducedProprietorIncome": 143025.49325627458,
    "totalProprietorIncome": 1682751.2236810732,
    "directOtherPropertyIncome": 2515626.304749686,
    "indirectOtherPropertyIncome": 809025.7069785306,
    "inducedOtherPropertyIncome": 794714.5706390596,
    "totalOtherPropertyIncome": 4119366.582367276,
    "directOtherTaxesOnProduction": -587875.7273735196,
    "indirectOtherTaxesOnProduction": -69630.40701408712,
    "inducedOtherTaxesOnProduction": 424911.2081212994,
    "totalOtherTaxesOnProduction": -232594.92626630724,
    "directEmployment": 37.956369228424386,
    "indirectEmployment": 20.783509884136247,
    "inducedEmployment": 17.652077462862138,
    "totalEmployment": 76.39195657542277,
    "totalDirectTaxes": 444156.09666210436,
    "totalIndirectTaxes": 447918.0835338043,
    "totalInducedTaxes": 804388.3285929796,
    "totalOfAllTaxes": 1696462.5087888883
}
```
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/can/{{modelId}}/{{industryCode}}/{{outputEventValue}}**


## Batch Impact (Post)
This endpoint generates an impact analysis for a collection of Canadian region and industry combinations. This will return a similar response to the Instant Impact, but will be formatted to return an array in the order of the events sent.
#### Required Parameters:
* Bearer Token
* In Body: List of the following combinations
  * Model Id (Returned in Region Model Endpoint)
  * Industry Code (Returned in Industry Code Endpoint)
  * Event Value (output)
#### Body Request Sample
```
[
    {"modelId":"14332", "industrycode" : 1, "eventvalue" : 10002.90},
    {"modelId":"14332", "industrycode" : 2, "eventvalue" : 30002.90}
]
```
#### Response - The API response when the impact analysis is complete will provide Direct, Indirect, Induced, and Total estimates for the following outputs:
* Output
* Employment
* Employee Compensation
* Proprietor Income
* Other Property Income
* Taxes on Production and Imports
* Total Taxes
#### Response Sample
```
[
  {
    "requestModelId": 14332,
    "requestIndustryCode": 1,
    "directOutput": 10000000.0,
    "indirectOutput": 4595783.390503161,
    "inducedOutput": 3538457.139683301,
    "totalOutput": 18134240.530186463,
    "directEmployeeCompensation": 1321413.9991816378,
    "indirectEmployeeCompensation": 1244419.638699429,
    "inducedEmployeeCompensation": 872226.9982893274,
    "totalEmployeeCompensation": 3438060.636170394,
    "directProprietorIncome": 1260509.9487290196,
    "indirectProprietorIncome": 279215.78169577895,
    "inducedProprietorIncome": 143025.49325627458,
    "totalProprietorIncome": 1682751.2236810732,
    "directOtherPropertyIncome": 2515626.304749686,
    "indirectOtherPropertyIncome": 809025.7069785306,
    "inducedOtherPropertyIncome": 794714.5706390596,
    "totalOtherPropertyIncome": 4119366.582367276,
    "directOtherTaxesOnProduction": -587875.7273735196,
    "indirectOtherTaxesOnProduction": -69630.40701408712,
    "inducedOtherTaxesOnProduction": 424911.2081212994,
    "totalOtherTaxesOnProduction": -232594.92626630724,
    "directEmployment": 37.956369228424386,
    "indirectEmployment": 20.783509884136247,
    "inducedEmployment": 17.652077462862138,
    "totalEmployment": 76.39195657542277,
    "totalDirectTaxes": 444156.09666210436,
    "totalIndirectTaxes": 447918.0835338043,
    "totalInducedTaxes": 804388.3285929796,
    "totalOfAllTaxes": 1696462.5087888883
  },
  {
    "requestModelId": 14332,
    "requestIndustryCode": 2,
    "directOutput": 10000000.0,
    "indirectOutput": 4595783.390503161,
    "inducedOutput": 3538457.139683301,
    "totalOutput": 18134240.530186463,
    "directEmployeeCompensation": 1321413.9991816378,
    "indirectEmployeeCompensation": 1244419.638699429,
    "inducedEmployeeCompensation": 872226.9982893274,
    "totalEmployeeCompensation": 3438060.636170394,
    "directProprietorIncome": 1260509.9487290196,
    "indirectProprietorIncome": 279215.78169577895,
    "inducedProprietorIncome": 143025.49325627458,
    "totalProprietorIncome": 1682751.2236810732,
    "directOtherPropertyIncome": 2515626.304749686,
    "indirectOtherPropertyIncome": 809025.7069785306,
    "inducedOtherPropertyIncome": 794714.5706390596,
    "totalOtherPropertyIncome": 4119366.582367276,
    "directOtherTaxesOnProduction": -587875.7273735196,
    "indirectOtherTaxesOnProduction": -69630.40701408712,
    "inducedOtherTaxesOnProduction": 424911.2081212994,
    "totalOtherTaxesOnProduction": -232594.92626630724,
    "directEmployment": 37.956369228424386,
    "indirectEmployment": 20.783509884136247,
    "inducedEmployment": 17.652077462862138,
    "totalEmployment": 76.39195657542277,
    "totalDirectTaxes": 444156.09666210436,
    "totalIndirectTaxes": 447918.0835338043,
    "totalInducedTaxes": 804388.3285929796,
    "totalOfAllTaxes": 1696462.5087888883
  }
]
```

**Post https://{{api_domain}}/{{env}}/api/v1/impact/batch/can**