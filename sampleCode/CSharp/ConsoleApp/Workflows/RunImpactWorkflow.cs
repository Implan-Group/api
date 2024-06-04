namespace ConsoleApp.Workflows;

public class RunImpactWorkflow : IWorkflow
{
    public static void Examples()
    {
        // In order to run an Impact, you first need to find the Project
        
        // You can get a list of all of your Projects
        Project[] projects = Projects.GetProjects();
        
        // You can also get a list of all Projects that have been shared with you
        Project[] shared = Projects.GetSharedProjects();
        
        // Once you have selected the Project you want to run, you can call the endpoint
        Guid projectId = Guid.Parse("795317c0-99ef-414c-942a-4f2525cc18a6");
        
        long impactRunId = Impacts.RunImpact(projectId);

        // The impact can take a while to run depending on the number of regions, number of events,
        // and whether it is MRIO
        // there are many ways to gather results,
        // see the workflow below for many examples
        ImpactResultsWorkflow.Examples();
        
        
        // Also, if you already know that you've Run an Impact and all you have is the ProjectId,
        // You can query for the Project (as above) and then use the
        // `LastImpactRunId` property to retrieve the Impact Run Id from the last time an Impact was run
        //impactRunId = projects[0].LastImpactRunId;
    }
}