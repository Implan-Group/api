# Impact API - Workflow - C# Example

### Folders

- `Endpoints` - Contains classes separated by logical functionality that contain the C# code to create, validate, and send Rest Requests
- `Services` - Contains C#-specific code to manage common functionality
  - `Json` - Contains all the configuration information for the standard `json` formatting
  - `Rest` - Contains all the boilerplate to send Rest Requests, handle errors, log, and return Responses
  - `Logging` - All the code that logs Requests/Responses to the `Console`
  - `Extension` - C#-specific helpers to clean up the code
- `Workflows`
  - Each file in this folder contains an example workflow, demonstrating the minimum steps necessary to accomplish a particular task