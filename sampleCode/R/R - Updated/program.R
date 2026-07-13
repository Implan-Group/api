# MIT License
# Copyright (c) 2023 IMPLAN
# (Full license text omitted for brevity — see original LICENSE file)

# ── Entry Point ────────────────────────────────────────────────────────────────
# This is the main entry point for the IMPLAN R SDK demo.
# Run this file first. It will:
#   1. Load all required packages
#   2. Set up file paths and shared configuration
#   3. Authenticate with the IMPLAN API
#   4. Run whichever workflow(s) you choose below
#
# BEFORE RUNNING: Set your credentials as environment variables.
# In your R console or .Renviron file, run:
#   Sys.setenv(IMPLAN_USERNAME = "your@email.com")
#   Sys.setenv(IMPLAN_PASSWORD = "yourpassword")
# ──────────────────────────────────────────────────────────────────────────────

# !! REQUIRED: Replace the empty strings below with your IMPLAN credentials !!
# Do this before running anything else.
username <- ""  # e.g. "your@email.com"
password <- ""  # e.g. "yourpassword"

# Load required packages 
source(file.path(path, "LoadPackages.R"))

#Load the required file Paths and base url
source(file.path(path, "auth_variables.R"))

# ── STEP 1: Authentication ─────────────────────────────────────────
source(auth_env$AuthenticationWorkflow)          # Load the workflow definition
auth_flow_instance <- new("AuthenticationWorkflow") # Create a workflow object
Examples(auth_flow_instance)                     # Run the authentication steps

# ── STEP 2: Create a New Project ────────────────────────────────────
# Uncomment this block to create a new IMPLAN project from scratch.
# You do NOT need to run this if you already have an existing project.
#
# source(auth_env$CreateProjectWorkflow)
# CreateProject_instance <- new("CreateProjectWorkflow")
# Examples(CreateProject_instance)

# ── STEP 3: Multi-Event to Multi-Group Workflow ─────────────────────
source(auth_env$MultiEventToMultiGroupWorkflow)          # Load the workflow definition
MultiEventToMultiGroupWorkflow_instance <- new("MultiEventToMultiGroupWorkflow") # Create a workflow object
Examples(MultiEventToMultiGroupWorkflow_instance)        # Run the workflow

# ── STEP 4: Combined Regions Workflow ───────────────────────────────
# Uncomment this block to combine two or more counties into a custom region,
# then build a model for that combined region.
#
# source(auth_env$CombinedRegionWorkflow)
# CombinedRegion_instance <- new("CombinedRegionWorkflow")
# Examples(CombinedRegion_instance)

# ── STEP 5: Run Impact Analysis on an Existing Project ──────────────
# Uncomment this block to run an impact analysis on a project you already created.
# Replace the project_id value below with your actual project GUID.
#
# project_id <- "your-project-guid-here"  # <-- replace this with your GUID
#
# source(auth_env$RunImpactAnalysisWorkflow)
# RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")
# Examples(RunImpactAnalysisWorkflow_instance, ProjectId = project_id)
