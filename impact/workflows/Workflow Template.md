# ImpactApi - {NAME} Workflow
- {Insert a high-level description of what this Workflow Template specifically covers}
- [Impact Readme](LINK TO THE RELEVANT SECTION HERE)

### 🗈 Notes
- The document is a supplement to the [Main Impact Readme](https://github.com/Implan-Group/api/blob/main/impact/readme.md)
- Additional workflows can be found in the [Workflows Directory](https://github.com/Implan-Group/api/tree/main/impact/workflows)
- All API Endpoints require a valid JWT Bearer Token to be passed with each requrest ([JWT.IO](https://jwt.io/))
	- Please see the [authentication](https://github.com/Implan-Group/api/blob/main/impact/readme.md#authentication---retrieving-bearer-access-token) section in the Readme to review authentication steps
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
