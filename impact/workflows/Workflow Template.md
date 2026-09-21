# ImpactApi - {NAME} Workflow
- {Insert a high-level description of what this Workflow Template specifically covers}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)

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
## 🔽 {High-Level Workflow Step}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain more about this step}

---
### {Endpoint Reference}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain this Endpoint}

##### Request
- `METHOD {{api_domain}}api/v1/{ENDPOINT_PATH}`
- `METHOD {{api_domain}}api/v1/{ALT_ENDPOINT}?={OPTIONAL_VARIABLE}`
	- {Describe any JSON body that might need to be included}
```json
{
	SHOW AN EXAMPLE INPUT
}
```
	- `{VARIABLE_NAME}` ({VARTYPE}, {OPTIONAL?}): {Brief Description}
	- `{VARIABLE_NAME}` ({VARTYPE}, {OPTIONAL?}): {Brief Description}

##### Response
- Returns {description of return: single value, array, json, csv, text, etc...}
```json
{
	SHOW AN EXAMPLE OUTPUT
}
```
	- `{VARIABLE_NAME}` ({VARTYPE}, {OPTIONAL?}): {Brief Description}
	- `{VARIABLE_NAME}` ({VARTYPE}, {OPTIONAL?}): {Brief Description}


---
## 🔽 {High-Level Workflow Step}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain more about this step}

---
### {Step}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain this Step}

### {Step}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain this Step}

### {Step}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)
- {Explain this Step}
