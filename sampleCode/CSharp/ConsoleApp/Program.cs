using ConsoleApp.Workflows;

/* IMPLAN ImpactAPI Workflow Examples - C#
 
 Please see the Services folder for all the utilities used to define and send REST requests,
 control JSON serialization, and log to Console
 
 Please see the Endpoints folder for collections of Endpoints grouped together by functionality
 
 Please see the Workflows folder for collections of various Workflows
 
 */

// Before any workflow, you must Authenticate to IMPLAN's ImpactAPI
AuthenticationWorkflow.Examples();

// Workflow for Creating a Project and filling it
CreateProjectWorkflow.Examples();

// Workflow for Combining two or more Regions
//CombinedRegionWorkflow.Examples();

// Workflow for Running an Impact Analysis and retrieving the Results
//RunImpactAnalysisWorkflow.Examples();


// These lines keep the Console Window open until manually closed
Console.WriteLine("Press Enter to close this window");
Console.ReadLine();