using ConsoleApp.Workflows;

// How to authenticate to Implan's Impact + Batch Apis
AuthenticationWorkflow.Execute();

// Contains an explanation and sample workflow for creating a Project
CreateProjectWorkflow.Execute();
// Contains an explanation and sample workflow for examining a Project's Impact Results
ImpactResultsWorkflow.Execute();


Console.WriteLine("Press Enter to close this window");
Console.ReadLine();