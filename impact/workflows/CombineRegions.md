# ImpactApi - Combined Region Workflow
- Not all economic models are built for Regions by default, or sometimes you may want to combine regions. Combining regions is used to create a custom group of counties, ZIP codes, MSAs, and/or states and treat them as one economic region that can be studied. The endpoints defined in this section may be used to build single or combined regions.
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#building-regions)

### 🗈 Notes
- This document supplements the [Impact API wiki](https://github.com/Implan-Group/api/wiki), which is the current reference for every endpoint, and the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- Runnable versions of these workflows in C#, Python, and R are in [sampleCode](https://github.com/Implan-Group/api/tree/main/sampleCode)
- All API Endpoints require a valid JWT Bearer Token to be passed with each request ([JWT.IO](https://jwt.io/))
	- See the wiki's [Authentication](https://github.com/Implan-Group/api/wiki/Authentication) page, or the [Authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication) section of the Readme, to review authentication steps
	- A token is valid for 24 hours and must be cached and reused. Requesting a new one on every call is unsupported and repeated requests in a short period can earn a temporary ban on the account
- Variables required for Endpoint calls will appear inside of double-braces (`{{}}`) and they must be replaced with valid values before the Request is sent
	- _e.g._ `{{api_domain}}` should be replaced with `https://api.implan.com/` for Public Production requests
	- See the [Production Variables](https://github.com/Implan-Group/api/blob/main/impact/readme.md#production-variables) section of the Readme for more information

---
## 🔽 Locate Regions to Combine
- See the `Regions.md` Workflow document located in the same directory as this one for a complete overview on Regions and Searching for them


---
## 🔽 Combine the Regions
- Once you have found the `HashIds` of all of the regions you wish to combine (using the endpoints above), you can combine them together into a single Region

---
### Combine Regions
- Combines several regions into a singular one

##### Request
- `POST {{api_domain}}api/v1/region/build/combined/{{aggregationSchemeId}}`
	- A `json` body must be included that defines the combined region
```json
{
    "description": "Testing Combined Region",
    "hashIds": [
        "W1aQl9wzxj",
        "Rgxp4eA3xK"
    ]
}
```
    - `description` (text): A description for this Combined Region. It must be unique for your account, so a timestamp or a run identifier in the name avoids a collision on a second run. It must not contain an ampersand or any of the characters `| ; % * ? ! = ' " ^ #`
    - `hashIds` (array of text): The HashIds of the Regions to be combined
    - `urids` (array of numbers): The URIDs of the Regions to be combined, for callers still working in URIDs
    - Supply `hashIds`, `urids`, or both. Two or more Regions are required between them. HashId is the identifier IMPLAN is standardizing on, so prefer it for new work

- The Regions being combined must come from the same Dataset, must not overlap, and must not nest inside one another. A state and a county within that state cannot be combined

##### Response
- Returns a `json`-array of Regions (see Region Json above) that has a singular Region: The newly combined one
- The new Region comes back with `"modelBuildStatus": "New"`. The economic model is built in the background and the Region is not usable until that reads `"Complete"`
	- Poll `GET {{api_domain}}api/v1/region/user/{{hashId}}` for the change. That endpoint reads one Region rather than the whole list, so it stays fast
	- Do not poll a data export to find out whether the model is ready. Those answer with an error until it is, and the error reads like a different problem