using ConsoleApp.Workflows;

/* Accessing Implan Impact + Batch API
 
The very first step to accessing Implan's ImpactApi is to authenticate to the service.
Your current Implan Username + Password need to be entered below so that the process completes.
See Rest.cs for details
*/

//Rest.SetAuthentication("", "");

//TODO: Try setting the auth timeout in Gateway higher? (1min?)

/* Here is an example of a complete walkthrough of creating + defining a Project */
//CreateProjectWorkflow.Execute();
ImpactResultsWorkflow.Execute();
//StartingWorkflow.Execute();

//RegionalWorkflow.Execute();


Console.WriteLine("Press Enter to close this window");
Console.ReadLine();