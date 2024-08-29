source(auth_env$Authentication)
source(auth_env$AggregationSchemeEndpoints)
source(auth_env$Rest)
source(auth_env$ProjectEndpoints)
source(auth_env$IndustrySetEndpoints)
source(auth_env$IndustryCodeEndpoints)
source(auth_env$EventEndpoints)
source(auth_env$DataSetEndpoints)
source(auth_env$RegionEndpoints)
source(auth_env$GroupEndpoints)
source(auth_env$Iworkflow)
source(auth_env$RunImpactAnalysisWorkflow)



# regions_instances <- new("Regions")
# 
# regions <- GetRegionTypes(regions_instances)
# 
# print(regions)

setClass("CreateProjectWorkflow",
         contains = "Iworkflow")

# Create a generic function for Create
#setGeneric("Examples", function(object) standardGeneric("Examples"))

# Define a method for the Create function with the CreateProjectWorkflow class
setMethod("Examples", signature = "CreateProjectWorkflow", function(object){
  
  AllSchemes <- new("AggregationSchemeEndpoints")
  aggregationSchemes <- GetAggregationSchemes(AllSchemes,IndustrySetId=8)
  
  print(aggregationSchemes)
  
  
  implan546AggScheme <- aggregationSchemes[aggregationSchemes$description=="546 Unaggregated",]
  
  aggregationSchemeId <- implan546AggScheme$id
  
  householdSetId <- as.integer(implan546AggScheme$householdSetIds)
  
  Title = paste0("ProjectWorkflow ",Sys.time())
  
  # Create an instance of `project_instance`
  project_instance <- new("ProjectEndpoints",
                          Title = paste0("ProjectWorkflow ",Sys.time()),
                          AggregationSchemeId = aggregationSchemeId,
                          HouseholdSetId = householdSetId[1]
  )
  
  print(project_instance)
  
  # Call the Create method
  project <- Create(project_instance)
  
  project
  
  industries <- new("IndustrySetEndpoints")
  
  industrySets <- GetIndustrySets(industries)
  
  industrySets
  
  implan546IndustriesSet <- industrySets[industrySets$description=="546 Industries",][1,] #[1,] accessing first row
  
  industryCodes <- new("IndustryCodeEndpoints")
  
  IndustryCodes <- GetIndustryCodes(industryCodes,aggregationSchemeId,implan546IndustriesSet$id)
  
  IndustryCodes
  
  IndustryCode <- IndustryCodes[IndustryCodes$description=="Oilseed farming",][1,] #[1,] accessing first row
  
  IndustryCode
  
  Event_class <- new("EventEndpoints")
  
  eventTypes <- GetEventsTypes(Event_class,project$id)
  
  eventTypes
  
  # Create an instance of `IndustryOutputEvent`
  industry_output_event <- new("IndustryOutputEvent",
                               Output = 100000,
                               IndustryCode = IndustryCode$code,
                               Title = "Industry Output Event"
  )
  
  print(industry_output_event)
  
  
  industryOutputEvent <- AddEvent(industry_output_event,
                                  projectGuid = project$id)
  
  industryOutputEvent
  
  
  industryImpactAnalysisEvent <- new("IndustryImpactAnalysisEvent",
                                     Title = "Industry Impact Analysis Event",
                                     IndustryCode = IndustryCode$code,
                                     IntermediateInputs = 500000,
                                     EmployeeCompensation = 250000,
                                     ProprietorIncome = 50000,
                                     WageAndSalaryEmployment = 4,
                                     ProprietorEmployment = 1,
                                     TotalEmployment = 5,
                                     TotalLaborIncome = 300000,
                                     OtherPropertyIncome = 100000,
                                     TaxOnProductionAndImports = 100000,
                                     SpendingPatternDatasetId = as.integer(87),
                                     SpendingPatternValueType = as.character(SpendingPatternValueType[SpendingPatternValueType == "IntermediateExpenditure"])
  )
  
  industryImpactAnalysisEvent <- AddEvent(industryImpactAnalysisEvent,
                                           projectGuid = project$id)
  
  industryImpactAnalysisEvent
  
  datasets_instance <- new("DataSetEndpoints")
  
  datasets <- GetDataSets(datasets_instance,aggregationSchemeId)
  
  datasets
  
  dataset <- datasets[datasets$description=="2022",][1,] #[1,] accessing first row
  
  dataset
  
  Regions_instance <- new("RegionEndpoints")
  
  stateRegions <- GetRegionChildren(Regions_instance, aggregationSchemeId = aggregationSchemeId ,
                                    dataSetId = dataset$id ,regionType = "State")
  stateRegions
  
  oregonStateRegion <- stateRegions[stateRegions$description == "Oregon",][1,] #[1,] accessing first row
  
  oregonStateHashId <- oregonStateRegion$hashId
  
  oregonStateHashId
  
  print(paste0(project$id," ", dataset$id," ", oregonStateHashId," ", industryOutputEvent$id," ", industryImpactAnalysisEvent$id))
  
  # Create an instance of `GroupEndpoints`
  group_instance <- new("GroupEndpoints",
                        ProjectId = project$id,
                        Title = "Sample Group",
                        DatasetId = dataset$id,
                        DollarYear = as.integer(2024),
                        # Must specify at least one regional identifier
                        HashId = oregonStateHashId,
                        
                        # Must add at least one Event
                        GroupEvents = list(GroupEvent(new("Event", eventId = industryOutputEvent$id)), 
                                           GroupEvent(new("Event", eventId = industryImpactAnalysisEvent$id)))
  )
  
  print(group_instance)
  
  
  group <- AddGroupToProject(projectGuid = project$id, group_instance)
  
  group
  
  RunImpactAnalysisWorkflow_instance <- new("RunImpactAnalysisWorkflow")
  
  print(Examples(RunImpactAnalysisWorkflow_instance,ProjectId = project$id))
})

