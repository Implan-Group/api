# ImpactApi - Combined Region Workflow
- Not all economic models are built for Regions by default, or sometimes you may want to combine regions. Combining regions is used to create a custom group of counties, ZIP codes, MSAs, and/or states and treat them as one economic region that can be studied. The endpoints defined in this section may be used to build single or combined regions.
- [Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md#building-regions)

### 🗈 Notes
- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
	- Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
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
    "hashids": [
	    { 
	        "W1aQl9wzxj", 
	        "Rgxp4eA3xK"
	    }
	]
}
```
    - `description` (text): A unique-per-Project description for this Combined Region
    - `hashids` (array of text): An array of the HashIds for all the Regions to be combined

##### Response
- Returns a `json`-array of Regions (see Region Json above) that has a singular Region: The newly combined one