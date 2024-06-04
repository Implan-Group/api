using ConsoleApp.Workflows;

// How to authenticate to Implan's Impact + Batch Apis
AuthenticationWorkflow.Examples();


// var temp = Regions.GetRegionChildren(8, 96, regionType: "County")
//     .Where(r => r.Description.Contains("Douglas") || r.Description.Contains("Lane"))
//     .ToList();
CombinedRegionWorkflow.Examples();

Debugger.Break();


// Contains an explanation and sample workflow for creating a Project
CreateProjectWorkflow.Examples();

// Contains an explanation and sample workflow for examining a Project's Impact Results
ImpactResultsWorkflow.Examples();


Console.WriteLine("Press Enter to close this window");
Console.ReadLine();