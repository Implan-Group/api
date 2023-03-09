<!-----

You have some errors, warnings, or alerts. If you are using reckless mode, turn it off to see inline alerts.
* ERRORs: 1
* WARNINGs: 0
* ALERTS: 4

Conversion time: 2.141 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β34
* Thu Mar 09 2023 11:12:00 GMT-0800 (PST)
* Source doc: IMPLAN - Batch API Developer Guide
* Tables are currently converted to HTML tables.

ERROR:
undefined internal link to this URL: "#heading=h.24vt0ete0h93".link text: Appendix
?Did you generate a TOC with blue links?

* This document has images: check for >>>>>  gd2md-html alert:  inline image link in generated source and store images to your server. NOTE: Images in exported zip file from Google Docs may not appear in  the same order as they do in your doc. Please check the images!


WARNING:
You have 7 H1 headings. You may want to use the "H1 -> H2" option to demote all headings by one level.

----->


<p style="color: red; font-weight: bold">>>>>>  gd2md-html alert:  ERRORs: 1; WARNINGs: 1; ALERTS: 4.</p>
<ul style="color: red; font-weight: bold"><li>See top comment block for details on ERRORs and WARNINGs. <li>In the converted Markdown or HTML, search for inline alerts that start with >>>>>  gd2md-html alert:  for specific instances that need correction.</ul>

<p style="color: red; font-weight: bold">Links to alert messages:</p><a href="#gdcalert1">alert1</a>
<a href="#gdcalert2">alert2</a>
<a href="#gdcalert3">alert3</a>
<a href="#gdcalert4">alert4</a>

<p style="color: red; font-weight: bold">>>>>> PLEASE check and correct alert issues and delete this message and the inline alerts.<hr></p>




<p id="gdcalert1" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image1.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert2">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image1.png "image_tooltip")



# Overview

This document is intended to provide a developer guide for the API that IMPLAN has developed for generating simple and scalable Batch Industry Output impacts via API. 

## Postman Collection

We have created a Postman collection with reference calls per section in this document to help with implementation.  IMPLAN will provide a client ID and client secret in a separate correspondence.


## Development Variables


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
   <td>api.implan.com
   </td>
  </tr>
  <tr>
   <td>Environment
   </td>
   <td>{{env}}
   </td>
   <td>beta
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



## Production Variables

Coming soon


# Retrieving Bearer access token


## General Authentication Architecture

API client will implement a backend solution to communicate with the IMPLAN API service.  API Client will need to include a bearer token when sending requests to the IMPLAN API Service.  This bearer token will be valid for 24 hours and it is expected that API Client will cache this token while it’s valid. 


## Token Caching

The “access_token” is good for 24 hours.  It is required that you cache this token and use the token to make additional requests to Implan.  Requesting Excessive tokens  (eg. Getting a new token for every request) is not necessary and is not supported, and may incur additional cost if we exceed 1000 tokens per month.  Requesting additional tokens is supported for use cases such as system reboots.  Excessive access_token requests are not supported.


## Examples

Some code examples for obtaining the authentication token are provided in the 

<p id="gdcalert2" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: undefined internal link (link text: "Appendix"). Did you generate a TOC with blue links? </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert3">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>

[Appendix](#Appendix).


## Expected Response

The expected response will be in this format:



<p id="gdcalert3" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image2.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert4">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image2.png "image_tooltip")



# Postman Collection

IMPLAN has provided a [Postman](https://www.postman.com/) collection to help provide examples while developing.  You may download this collection from this link below:



* IMPLAN [Batch API V1 Beta.postman_collection.json](https://drive.google.com/file/d/1ikNquclP88taDsj3oD5WZHcL_jKWJtSO/view?usp=share_link)
* [Postman Instructions for Importing a Collection](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman)

Once downloaded, you may enter your application credentials into the “auth” request body to obtain a bearer token.  Copy the results of the “auth” response into the Collection’s Pre-request script:



<p id="gdcalert4" ><span style="color: red; font-weight: bold">>>>>>  gd2md-html alert: inline image link here (to images/image3.png). Store image on your image server and adjust path/filename/extension if necessary. </span><br>(<a href="#">Back to top</a>)(<a href="#gdcalert5">Next alert</a>)<br><span style="color: red; font-weight: bold">>>>>> </span></p>


![alt_text](images/image3.png "image_tooltip")



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


## Region Model Endpoint (Get)

Since region model id’s and underlying data can change each year, Purchaser will need to provide a Data Set ID as an input.  The Endpoint response will include a list of Region Names, Types, and Model ID’s.   The response may be cached.

The Regions that will be accessible by this API endpoint will include the regions purchased in their data subscription.



1. Parameters
    1. Bearer Token
    2. Data Set Id 
2. Response (List)
    3. Model Id
    4. Region Type Id
        1. 2 = State
        2. 3 = MSA
        3. 4 = County
    5. Region Name

Take a dataset id from the dataset API request and use it for the model’s API request

**GET https://{{api_domain}}/{{env}}/api/v1/models?datasetId=77   **   	

Will return Models


    [


       {


            "id": 21350,


            "description": "Indiana",


            "regionType": "State"


        },


        {


            "id": 21349,


            "description": "Michigan",


            "regionType": "State"


        },


        {


            "id": 20766,


            "description": "Minnesota",


            "regionType": "State"


        }


    ]


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


<p id="Appendix" ># Appendix</p?


## Code Examples to retrieve tokens


### C# example

**var** client = **new** RestClient("https://{{api_domain}}/{{env}}/auth");

client.Timeout = -1;

**var** request = **new** RestRequest(Method.POST);

request.AddHeader("Content-Type", "text/plain");

**var** body = @"{  ""username"": ""{{email}}"",   ""password"": ""{{password}}"" }";

request.AddParameter("text/plain", body,  ParameterType.RequestBody);

IRestResponse response = client.Execute(request);

Console.WriteLine(response.Content);


### Java Example

HttpResponse&lt;String> response = Unirest.post("https://{{api_domain}}/{{env}}/auth")

  .header("Content-Type", "text/plain")

  .body("{  \"username\": \"{{email}}\",   \"password\": \"{{password}}\" }")

  .asString();


### 


### Node Example

var request **=** **require**('request');

var options **=** {

  'method': 'POST',

  'url': 'https://{{api_domain}}/{{env}}/auth',

  'headers': {

    'Content-Type': 'text/plain'

  },

  body: '{  "username": "{{email}}",   "password": "{{password}}" }'

};

request(options, **function** (error, response) {

  **if** (error) **throw** **new** Error(error);

  console.**log**(response.body);

});


###  Python Example

**import** http.client

conn = http.client.HTTPSConnection("{{api_domain}}")

payload = "{  \"username\": \"{{email}}\",   \"password\": \"{{password}}\" }"

headers = {

  'Content-Type': 'text/plain'

}

conn.request("POST", "/{{env}}/auth", payload, headers)

res = conn.getresponse()

data = res.read()

**print**(data.decode("utf-8"))
