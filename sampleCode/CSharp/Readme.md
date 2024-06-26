# Impact API  Workflow - C# Examples
---

## Installation + Use
- In order to open, compile, and run the C# workflow examples, you will need the following:
  - Visual Studio 2022 (or newer) (required for .net 8.0)
    - https://visualstudio.microsoft.com/vs/ - You can use the free Community Edition
  - .Net 8.0 Runtime
    - https://dotnet.microsoft.com/en-us/download/dotnet/8.0 - You need just the `.Net Runtime 8.06` (or newer)
    - [Windows x64 Installer](https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-8.0.6-windows-x64-installer)

## Solution Folders
- `Endpoints` - Contains classes separated by logical functionality that contain the C# code to create, validate, and send Rest Requests
- `Services` - Contains C#-specific code to manage common functionality
  - `Json` - Contains all the configuration information for the standard `json` formatting
  - `Rest` - Contains all the boilerplate to send Rest Requests, handle errors, log, and return Responses
  - `Logging` - All the code that logs Requests/Responses to the `Console`
  - `Extension` - C#-specific helpers to clean up the code
- `Workflows`
  - Each file in this folder contains an example workflow, demonstrating the minimum steps necessary to accomplish a particular task