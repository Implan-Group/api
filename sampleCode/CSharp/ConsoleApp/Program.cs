using ConsoleApp.Workflows;

/*
# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
*/

/* IMPLAN ImpactAPI Workflow Examples - C#
 
 Please see the Services folder for all the utilities used to define and send REST requests,
 control JSON serialization, and log to Console
 
 Please see the Endpoints folder for collections of Endpoints grouped together by functionality
 
 Please see the Workflows folder for collections of various Workflows
 
 */

// Before any workflow, you must Authenticate to IMPLAN's ImpactAPI
AuthenticationWorkflow.Examples();

// Workflow for Creating a Project and filling it
//CreateProjectWorkflow.Examples();
MultiEventToMultiGroupWorkflow.Examples();

// Workflow for Combining two or more Regions
//CombinedRegionWorkflow.Examples();

// Workflow for Running an Impact Analysis and retrieving the Results
//RunImpactAnalysisWorkflow.Examples();


// These lines keep the Console Window open until manually closed
Console.WriteLine("Press Enter to close this window");
Console.ReadLine();
