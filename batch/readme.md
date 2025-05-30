# Overview

This document is intended to provide a developer guide for the API that IMPLAN has developed for generating simple and scalable Batch Industry Output impacts via API. 

## Postman Collection

We have created a Postman collection with reference calls per section in this document to help with implementation.  IMPLAN will provide a client ID and client secret in a separate correspondence as needed by client request.


## Development Variables
The following variables can be used while developing against the IMPLAN API. Following development, please transition to Production Variables below.  

<table>
  <tr>
   <td>Item
   </td>
   <td>Reference Value
   </td>
   <td>Development Value
   </td>
  </tr>
  <tr>
   <td>API Domain 
   </td>
   <td>{{api_domain}}
   </td>
   <td>api.implan.com/
   </td>
  </tr>
  <tr>
   <td>Environment
   </td>
   <td>{{env}}
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>User Email
   </td>
   <td>{{email}}
   </td>
   <td>
   </td>
  </tr>
  <tr>
   <td>User Password
   </td>
   <td>{{password}}
   </td>
   <td>
   </td>
  </tr>
</table>



## Production Variables

<table>
  <tr>
   <td>Item
   </td>
   <td>Reference Value
   </td>
   <td>Development Value
   </td>
  </tr>
  <tr>
   <td>API Domain 
   </td>
   <td>{{api_domain}}
   </td>
   <td>api.implan.com/
   </td>
  </tr>
  <tr>
   <td>Environment
   </td>
   <td>{{env}}
   </td>
   <td>n/a
   </td>
  </tr>
  <tr>
   <td>User Email
   </td>
   <td>{{email}}
   </td>
   <td>Same as app.implan.com
   </td>
  </tr>
  <tr>
   <td>User Password
   </td>
   <td>{{password}}
   </td>
   <td>Same as app.implan.com
   </td>
  </tr>
</table>



# Retrieving Bearer access token


## General Authentication Architecture

API client will implement a backend solution to communicate with the IMPLAN API service.  API Client will need to include a bearer token when sending requests to the IMPLAN API Service.  This bearer token will be valid for 24 hours and it is expected that API Client will cache this token while it’s valid. 


## Token Caching

The “access_token” is good for 24 hours.  It is required that you cache this token and use the token to make additional requests to Implan.  Requesting Excessive tokens  (eg. Getting a new token for every request) is not necessary and is not supported, and may incur additional cost if we exceed 1000 tokens per month.  Requesting additional tokens is supported for use cases such as system reboots.  Excessive access_token requests are not supported.


## Examples

Some code examples for obtaining the authentication token are provided in the [Appendix](#Appendix).


## Expected Response

The expected response will be in this format:

![alt_text](/images/auth_response.png "auth response")

# Postman Collection

IMPLAN has provided a [Postman](https://www.postman.com/) collection to help provide examples while developing.  You may download this collection from this link below:



* IMPLAN [Batch API V1 postman_collection.json](/Implan%20API.postman_collection.json)
* [Postman Instructions for Importing a Collection](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman)

Once downloaded, you may enter your application credentials into the “auth” request body to obtain a bearer token.  Copy the results of the “auth” response into the Collection’s Pre-request script:

![alt_text](/images/auth_pre_request.png "auth pre request")

# Throttling Rates
The IMPLAN API will currently support the following requests per timeframe, to ensure a smooth operation for all customers.  When exceeding these rates, you will receiving a throttling error response.  
* Industry Codes
  * Requests per minute = 10
* Data Sets
  * Requests per minute = 10
* Region Models
  * Requests per minute = 5
* Instant 
  * Requests per second = 5
* Batch
  * Requests per minute = 6
  * 2500 events per request supported.

# Preliminary Requests to Running an Impact

Responses from the following endpoints are needed to provide information to run an impact analysis and receive results.  Once these are collected, you may proceed to run an impact and get results.  


## Dataset Endpoint (Get)

IMPLAN models vary based on annual data sets.  In order to provide the correct list of models and industries, this API endpoint will provide a list of available data sets.  This response may be cached.  As data is released, IMPLAN will update the Default Data Set returned so that the Purchaser application can update without maintenance.



1. Parameters
    1. Bearer Token
2. Response (List)
    2. Data Set ID (Number)
    3. Data Set Description (Text)
    4. Default Data Set (Boolean - only 1 record in the list should be true)

**GET https://{{api_domain}}/{{env}}/api/v1/datasets**

Will Return datasets

[   

	{

        "id": 59,

        "description": "2018",

        "isDefault": false

    },

    {

        "id": 77,

        "description": "2019",

        "isDefault": true

    }

]

**NOTE**: Batch API currently only supports processing for 2018, 2019, and 2020 state models and impacts.  


### Region Model Endpoint (Get)
This endpoint will return a list of models available for Batch Impact analysis. A `datasetId` from the previously mentioned endpoint is required. The response may be cached.
#### Parameters
* Bearer Token
* Data Set Id (in URL)
* Region Type Filer (query parameter; *optional)
  * State
  * County 
  * MSA
  * CongressionalDistrict
### Sample Response
```
[
    {
        "hashId": "5Oad92M9bZ",
        "urid": 1646939,
        "userModelId": null,
        "description": "Vermont",
        "modelId": 11597,
        "modelBuildStatus": "Complete",
        "employment": 410771.60344260157,
        "output": 71119723120.10498,
        "valueAdded": 38292831461.82147,
        "aggregationSchemeId": 8,
        "datasetId": 87,
        "datasetDescription": "2021",
        "fipsCode": "50",
        "provinceCode": null,
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": false,
        "regionTypeDescription": "State",
        "geoId": "50",
        "isMrioAllowed": true
    },
    ...
    {
        "hashId": "wlx62YXDxk",
        "urid": 1646952,
        "userModelId": null,
        "description": "Arkansas",
        "modelId": 11623,
        "modelBuildStatus": "Complete",
        "employment": 1639050.8514250224,
        "output": 308251018253.70966,
        "valueAdded": 150461125093.1109,
        "aggregationSchemeId": 8,
        "datasetId": 87,
        "datasetDescription": "2021",
        "fipsCode": "05",
        "provinceCode": null,
        "m49Code": null,
        "regionType": "State",
        "hasAccessibleChildren": false,
        "regionTypeDescription": "State",
        "geoId": "05",
        "isMrioAllowed": true
    }
]
```
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/models/{{datasetId}}**\
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/models/{{datasetId}}?regionTypeFilter={{regionTypeFilter}}**


## Industry Codes Endpoint (Get)

The Industries supported by this API will be the current standard IMPLAN 546 Industry scheme. This response may be cached.  A list of those industries can be found here: [https://support.implan.com/hc/en-us/articles/360034896614-546-Industries-Conversions-Bridges-Construction-2018-Data](https://support.implan.com/hc/en-us/articles/360034896614-546-Industries-Conversions-Bridges-Construction-2018-Data)

In 2023, the BEA will redefine the North American Industry Classifications System (NAICS) codes. This change will result in a change to the IMPLAN industry scheme for the 2023 IMPLAN data release. The API will then be updated to include these new industry designations when that data is added to the system.



1. Parameters
    1. Bearer Token
2. Response (List)
    2. Id - Unique identifier
    3. Code - Implan Code corresponding to BEA
        1. Use this when making an IMPACT request
    4. Description

**GET https://{{api_domain}}/{{env}}/api/v1/IndustryCodes**

Will return Industries

[

    {

        "id": 4638,

        "code": 1,

        "description": "Oilseed farming"

    },

    {

        "id": 4639,

        "code": 2,

        "description": "Grain farming"

    },

    {

        "id": 4640,

        "code": 3,

        "description": "Vegetable and melon farming"

    }

]


# Running an Impact and getting Results

After the authentication token, and responses have been collected from the API endpoints above, you may then proceed with running an impact analysis and retrieving results.  


## Instant Impact (Get)

The API method that will estimate economic impacts will be using the Industry Output methodology. This will allow for a single endpoint that can accommodate instant outputs for industry output based inputs. 



1. Required Parameters:
    1. Bearer Token
    2. Model Id (Returned in Region Model Endpoint)
    3. Industry Code (Returned in Industry Code Endpoint) 
    4. Output Event Value 
2. Response - The API response when the impact analysis is complete will provide Direct, Indirect, Induced, and Total estimates for the following outputs:
    5. Output
    6. Employment
    7. Employee Compensation
    8. Proprietor Income
    9. Other Property Income
    10. Taxes on Production and Imports
    11. Total Taxes

**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/{{modelId}}/{{industryCode}}/{{outputEventValue}}**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/{{industryCode}}/{{outputEventValue}}?urid={{urid}}**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/{{industryCode}}/{{outputEventValue}}?hashId={{hashId}}**  



Will return results:

{

    "requestModelId": 21350,

    "requestIndustryCode": 1,

    "directOutput": 1000000.0,

    "indirectOutput": 441450.9285317437,

    "inducedOutput": 319847.0603026519,

    "totalOutput": 1761297.9888343955,

    "directEmployeeCompensation": 2472.900136053837,

    "indirectEmployeeCompensation": 82254.23939162493,

    "inducedEmployeeCompensation": 88549.70207157897,

    "totalEmployeeCompensation": 173276.84159925772,

    "directProprietorIncome": 226931.1493427253,

    "indirectProprietorIncome": 75340.41642662129,

    "inducedProprietorIncome": 16336.698484485116,

    "totalProprietorIncome": 318608.26425383164,

    "directOtherPropertyIncome": 231299.71079943964,

    "indirectOtherPropertyIncome": 50187.716015487764,

    "inducedOtherPropertyIncome": 62506.37506839628,

    "totalOtherPropertyIncome": 343993.80188332364,

    "directTaxesOnProductionAndImports": 14094.89315942286,

    "indirectTaxesOnProductionAndImports": 14599.263637118289,

    "inducedTaxesOnProductionAndImports": 15784.781427157634,

    "totalTaxesOnProductionAndImports": 44478.93822369878,

    "directEmployment": 2.4027237817133655,

    "indirectEmployment": 2.6857916158570942,

    "inducedEmployment": 2.1816787685694536,

    "totalEmployment": 7.2701941661399125,

    "totalDirectTaxes": 59536.24791805996,

    "totalIndirectTaxes": 45952.24774663439,

    "totalInducedTaxes": 39488.143525720414,

    "totalOfAllTaxes": 144976.63919041475

}

### NOTE: Due to variances in the underlying model structure, Canada and International models require the use of specific endpoints. Data returned will be in the same scheme as domestic U.S. data but with some changes to terminology.

Canada:  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/can/{{modelId}}/{{industryCode}}/{{outputEventValue}} FOR CANADA MODELS**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/can/{{industryCode}}/{{outputEventValue}}?urid={{urid}} FOR CANADA MODELS**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/can/{{industryCode}}/{{outputEventValue}}?hashId={{hashId}} FOR CANADA MODELS**  

International:  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/intl/{{modelId}}/{{industryCode}}/{{outputEventValue}} FOR INTERNATIONAL MODELS**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/intl/{{industryCode}}/{{outputEventValue}}?urid={{urid}} FOR INTERNATIONAL MODELS**  
**GET https://{{api_domain}}/{{env}}/api/v1/impact/instant/intl/{{industryCode}}/{{outputEventValue}}?hashId={{hashId}} FOR INTERNATIONAL MODELS**  


## Batch Impact (Post)

The API method that will estimate economic impacts will be using the Industry Output methodology. This will allow for a single endpoint that can accommodate batch outputs for multiple industry output based inputs. For example, 1000 inputs can be sent at once.  



1. Required Parameters:
    1. Bearer Token
    2. Model Id (Returned in Region Model Endpoint)
    3. Industry Code (Returned in Industry Code Endpoint) 
    4. Output Event Value 
2. Response - The API response when the impact analysis is complete will provide Direct, Indirect, Induced, and Total estimates for the following outputs:
    5. Output
    6. Employment
    7. Employee Compensation
    8. Proprietor Income
    9. Other Property Income
    10. Taxes on Production and Imports
    11. Total Taxes

**Post https://{{api_domain}}/{{env}}/api/v1/impact/batch**

Also include this in the body of the request:

[

    {"modelId":"26899", "industrycode" : 1, "eventvalue" : 10002.90},

    {"modelId":"26899", "industrycode" : 2, "eventvalue" : 30002.90},

    {"modelId":"26899", "industrycode" : 1, "eventvalue" : 10002.90}

]

This will return a similar response to the Instant Impact, but will be formatted to return an array in the order of the events sent.


# 


# Appendix


## Code Examples to retrieve tokens


### C# example
```
var client = new RestClient("https://{{api_domain}}/{{env}}/auth");

client.Timeout = -1;

var request = new RestRequest(Method.POST);

request.AddHeader("Content-Type", "text/plain");

var body = @"{  ""username"": ""{{email}}"",   ""password"": ""{{password}}"" }";

request.AddParameter("text/plain", body,  ParameterType.RequestBody);

IRestResponse response = client.Execute(request);

Console.WriteLine(response.Content);
```

### Java Example
```
HttpResponse&lt;String> response = Unirest.post("https://{{api_domain}}/{{env}}/auth")

  .header("Content-Type", "text/plain")

  .body("{  \"username\": \"{{email}}\",   \"password\": \"{{password}}\" }")

  .asString();
```

### Node Example
```
var request = require('request');

var options = {

  'method': 'POST',

  'url': 'https://{{api_domain}}/{{env}}/auth',

  'headers': {

    'Content-Type': 'text/plain'

  },

  body: '{  "username": "{{email}}",   "password": "{{password}}" }'

};

request(options, function (error, response) {

  if (error) throw new Error(error);

  console.log(response.body);

});
```

###  Python Example
```
import http.client

conn = http.client.HTTPSConnection("{{api_domain}}")

payload = "{  \"username\": \"{{email}}\",   \"password\": \"{{password}}\" }"

headers = {

  'Content-Type': 'text/plain'

}

conn.request("POST", "/{{env}}/auth", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```