# Impact API  Workflow - R Examples
---

## Installation
- In order to open and run the R workflow examples, you can use the following:
  - First, download and install R from https://cran.rstudio.com/
  - Then, download and install RStudio from https://posit.co/download/rstudio-desktop/ 

## Use
- At the top of `implan_api_helper.R` you can the Aggregation Scheme Id, Dataset Id, dollar year, ad folder name.
- Your IMPLAN Username and Password needs to be entered into `private/creds.json`

## Description

- This project will authenticate with the Implan API and cache the token until it expires where it will auto renew.
- Read combined model information from state_based.csv and county_based.csv then based on the grouping in the model_name column the program will to trigger the combined model.
- The program will wait until each model build is complete before proceeding to the next step.
- The program will then create a project for each combined model specified in state_based.csv and county_based.csv and add the events specified in demo_events.csv
- For each project the program will wait until the Impact has completed.  Then download the results to the Results folder inside the project.
- The program will then create a project with all of the combined models and events.  Wait for the project to complete, and download the results into the Results folder.
- All of the projects will be located in the folder specified in the folder name variable at the top of `implan_api_helper.R` 
