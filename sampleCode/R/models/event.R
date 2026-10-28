# Events: the economic changes being analyzed.
#
# An Event says what happened, a Group says where and when, and an Impact Run
# combines them. Every event carries `impact_event_type`, and that value decides
# which other fields the API expects, so the constructors here are one per type
# rather than one with every field on it.
#
# Only the types the workflows use are modeled. Adding another is a matter of
# copying the nearest constructor, changing the type and the fields, and
# registering it in `EVENT_BUILDERS` at the bottom so responses come back as it.
#
# Wiki: Events - https://github.com/Implan-Group/api/wiki/Events
# Support: Quick Start Guide 4: Impacts
# https://support.implan.com/hc/en-us/articles/360051087394


# The event types the API accepts.
#
# Not every type is valid in every Project: the international types are only
# valid in an international Aggregation Scheme, and IndustryImpactAnalysis and
# IndustryProprietorIncome are not valid in one. Ask the Project which types it
# accepts with `get_event_types()` rather than assuming.
EVENT_TYPES <- c(
  INDUSTRY_OUTPUT = "IndustryOutput",
  INDUSTRY_EMPLOYMENT = "IndustryEmployment",
  INDUSTRY_EMPLOYEE_COMPENSATION = "IndustryEmployeeCompensation",
  INDUSTRY_PROPRIETOR_INCOME = "IndustryProprietorIncome",
  COMMODITY_OUTPUT = "CommodityOutput",
  LABOR_INCOME = "LaborIncome",
  HOUSEHOLD_INCOME = "HouseholdIncome",
  INDUSTRY_CONTRIBUTION_ANALYSIS = "IndustryContributionAnalysis",
  INDUSTRY_IMPACT_ANALYSIS = "IndustryImpactAnalysis",
  CUSTOM_INDUSTRY_IMPACT_ANALYSIS = "CustomIndustryImpactAnalysis",
  INTERNATIONAL_INDUSTRY_IMPACT_ANALYSIS = "InternationalIndustryImpactAnalysis",
  INDUSTRY_SPENDING_PATTERN = "IndustrySpendingPattern",
  INSTITUTIONAL_SPENDING_PATTERN = "InstitutionalSpendingPattern",
  HOUSEHOLD_SPENDING_PATTERN = "HouseholdSpendingPattern",
  CUSTOM_SPENDING_PATTERN = "CustomSpendingPattern"
)


# Whether a value is the price the producer received or the buyer paid.
#
# Only retail and wholesale industries, and commodities sold through them, can be
# margined. Setting "PurchaserPrice" on anything else is reverted to
# "ProducerPrice" before the impact runs.
#
# Support: Margins - https://support.implan.com/hc/en-us/articles/115009506007
MARGIN_TYPES <- c(PRODUCER_PRICE = "ProducerPrice", PURCHASER_PRICE = "PurchaserPrice")


# How a spending-pattern event's value should be read.
#
# "IntermediateExpenditure" spends the whole value across the pattern's
# commodities. "Output" multiplies it by the industry's gross absorption first,
# so only the portion actually spent on intermediate inputs flows through.
SPENDING_PATTERN_VALUE_TYPES <- c(
  INTERMEDIATE_EXPENDITURE = "IntermediateExpenditure",
  OUTPUT = "Output"
)


# Fields shared by every event type.
#
# Leave `id` unset when creating: the API generates it and returns it. `title`
# must be unique among the Project's events and must avoid an ampersand and the
# characters | ; % * ? ! = ' " ^ #.
#
# `tags` are free text and are how results get filtered later; see the
# AdvancedEvents workflow. Note that updating an event merges tags rather than
# replacing them, so a tag can be added but not removed through an update.
new_event <- function(impact_event_type, title, tags = NULL, ...) {
  event <- list(impact_event_type = impact_event_type, title = title)
  if (!is.null(tags)) {
    event$tags <- as.character(tags)
  }
  event <- c(event, list(...))
  structure(event, class = c("implan_event", "implan_model", "list"))
}


# One line naming the event, for the console.
describe.implan_event <- function(x, ...) {
  sprintf("%s  [%s]  id=%s", x$title, x$impact_event_type, field_or(x, "id", "(none)"))
}


# A change in what an industry produces, stated in dollars of output.
#
# The most common event type and the right default when you know a dollar figure
# and the industry that earned it. Supply any one of output, employment, employee
# compensation, or proprietor income; IMPLAN estimates the rest from the
# industry's averages for the region.
#
# Support: Industry Events
# https://support.implan.com/hc/en-us/articles/360051441834
industry_output_event <- function(title,
                                  industry_code,
                                  output = NULL,
                                  employment = NULL,
                                  employee_compensation = NULL,
                                  proprietor_income = NULL,
                                  margin_type = NULL,
                                  percentage = NULL,
                                  dataset_id = NULL,
                                  tags = NULL) {
  new_event(
    EVENT_TYPES[["INDUSTRY_OUTPUT"]], title, tags,
    industry_code = industry_code,
    output = output,
    employment = employment,
    employee_compensation = employee_compensation,
    proprietor_income = proprietor_income,
    # Margins apply to retail and wholesale industries only.
    margin_type = margin_type,
    percentage = percentage,
    # The data year the margins come from, when margins are applied.
    dataset_id = dataset_id
  )
}


# A change in demand for a commodity rather than for an industry's output.
#
# Use this when you know what was bought rather than who produced it. IMPLAN
# decides which industries supply the commodity locally.
commodity_output_event <- function(title,
                                   commodity_code,
                                   output = NULL,
                                   margin_type = NULL,
                                   tags = NULL) {
  new_event(
    EVENT_TYPES[["COMMODITY_OUTPUT"]], title, tags,
    commodity_code = commodity_code,
    output = output,
    margin_type = margin_type
  )
}


# A change in income for one household income bracket.
#
# `household_income_code` is a specification code, not an industry code. Read the
# valid ones from `get_event_specifications()`; they look like
# "10002 - Households 15-30k".
#
# Support: Household Income Events
# https://support.implan.com/hc/en-us/articles/360052212413
household_income_event <- function(title, household_income_code, value = NULL, tags = NULL) {
  new_event(
    EVENT_TYPES[["HOUSEHOLD_INCOME"]], title, tags,
    household_income_code = household_income_code,
    value = value
  )
}


# The contribution an existing industry already makes to a region.
#
# This is a different question from an impact. An impact asks what would change
# if new activity arrived; a contribution asks how much of the current economy
# rests on an industry that is already there. The analysis constrains the
# industry from buying from itself so its own output is not counted twice.
#
# Set `output` to a dollar figure, or set `is_output_percentage` and give
# `output` as a share of the industry's regional output from 0 to 1.
#
# Support: ICA: Introduction to Industry Contribution Analysis
# https://support.implan.com/hc/en-us/articles/360025854654
industry_contribution_analysis_event <- function(title,
                                                 industry_code,
                                                 output = NULL,
                                                 is_output_percentage = FALSE,
                                                 tags = NULL) {
  new_event(
    EVENT_TYPES[["INDUSTRY_CONTRIBUTION_ANALYSIS"]], title, tags,
    industry_code = industry_code,
    output = output,
    is_output_percentage = is_output_percentage
  )
}


# An industry event where you know the production function, not just a total.
#
# Where an Industry Output event gives IMPLAN one number and lets it estimate the
# rest, this type lets you state employment, compensation, proprietor income,
# taxes, and intermediate inputs yourself. Use it when you have the operating
# statement for the thing being modeled, such as a hospital or a university.
#
# Support: Industry Impact Analysis (Detailed) Events
# https://support.implan.com/hc/en-us/articles/4414451454491
industry_impact_analysis_event <- function(title,
                                           industry_code,
                                           intermediate_inputs = NULL,
                                           total_output = NULL,
                                           employee_compensation = NULL,
                                           proprietor_income = NULL,
                                           total_labor_income = NULL,
                                           other_property_income = NULL,
                                           tax_on_production_and_imports = NULL,
                                           wage_and_salary_employment = NULL,
                                           proprietor_employment = NULL,
                                           total_employment = NULL,
                                           local_purchase_percentage = 1.0,
                                           is_sam = FALSE,
                                           spending_pattern_dataset_id = NULL,
                                           spending_pattern_value_type =
                                             SPENDING_PATTERN_VALUE_TYPES[["INTERMEDIATE_EXPENDITURE"]],
                                           spending_pattern_commodities = NULL,
                                           tags = NULL) {
  new_event(
    EVENT_TYPES[["INDUSTRY_IMPACT_ANALYSIS"]], title, tags,
    industry_code = industry_code,
    intermediate_inputs = intermediate_inputs,
    total_output = total_output,
    employee_compensation = employee_compensation,
    proprietor_income = proprietor_income,
    total_labor_income = total_labor_income,
    other_property_income = other_property_income,
    tax_on_production_and_imports = tax_on_production_and_imports,
    wage_and_salary_employment = wage_and_salary_employment,
    proprietor_employment = proprietor_employment,
    total_employment = total_employment,
    # Share of intermediate inputs bought inside the region, 0 to 1. Leave at 1
    # when everything is local, or set `is_sam` to let IMPLAN use the region's
    # own trade data instead.
    local_purchase_percentage = local_purchase_percentage,
    is_sam = is_sam,
    # Which data year's spending pattern to spend the intermediate inputs
    # through.
    spending_pattern_dataset_id = spending_pattern_dataset_id,
    spending_pattern_value_type = spending_pattern_value_type,
    spending_pattern_commodities = spending_pattern_commodities
  )
}


# An industry's purchases of goods and services, excluding labor.
#
# Use this to model a buyer rather than a producer: the event spends money
# through an industry's supply chain without adding any direct output of its own.
# The commodity list can be left empty to use IMPLAN's default pattern, or
# supplied with edited coefficients, which is what the AdvancedEvents workflow
# demonstrates.
#
# Support: Industry Spending Pattern Events
# https://support.implan.com/hc/en-us/articles/360052212933
industry_spending_pattern_event <- function(title,
                                            industry_code,
                                            output = NULL,
                                            local_purchase_percentage = 1.0,
                                            is_sam = FALSE,
                                            spending_pattern_dataset_id = NULL,
                                            spending_pattern_region_urid = NULL,
                                            spending_pattern_value_type =
                                              SPENDING_PATTERN_VALUE_TYPES[["OUTPUT"]],
                                            spending_pattern_commodities = NULL,
                                            tags = NULL) {
  new_event(
    EVENT_TYPES[["INDUSTRY_SPENDING_PATTERN"]], title, tags,
    industry_code = industry_code,
    output = output,
    local_purchase_percentage = local_purchase_percentage,
    is_sam = is_sam,
    spending_pattern_dataset_id = spending_pattern_dataset_id,
    spending_pattern_region_urid = spending_pattern_region_urid,
    spending_pattern_value_type = spending_pattern_value_type,
    spending_pattern_commodities = spending_pattern_commodities
  )
}


# The fields each event type declares, by `impactEventType`.
#
# Reading a response needs to know which fields the type owns so the rest can be
# kept aside rather than dropped. A type that is not listed falls back to the
# shared fields, which is why an event type this sample has never heard of still
# comes back readable instead of raising.
EVENT_FIELDS <- list(
  IndustryOutput = c(
    "industry_code", "output", "employment", "employee_compensation",
    "proprietor_income", "margin_type", "percentage", "dataset_id"
  ),
  CommodityOutput = c("commodity_code", "output", "margin_type"),
  HouseholdIncome = c("household_income_code", "value"),
  IndustryContributionAnalysis = c("industry_code", "output", "is_output_percentage"),
  IndustryImpactAnalysis = c(
    "industry_code", "intermediate_inputs", "total_output", "employee_compensation",
    "proprietor_income", "total_labor_income", "other_property_income",
    "tax_on_production_and_imports", "wage_and_salary_employment",
    "proprietor_employment", "total_employment", "local_purchase_percentage",
    "is_sam", "spending_pattern_dataset_id", "spending_pattern_value_type",
    "spending_pattern_commodities", "is_local_employee_compensation",
    "is_fte_employment", "is_wage_and_salary", "is_contribution_analysis"
  ),
  IndustrySpendingPattern = c(
    "industry_code", "output", "local_purchase_percentage", "is_sam",
    "spending_pattern_dataset_id", "spending_pattern_region_urid",
    "spending_pattern_value_type", "spending_pattern_commodities"
  )
)

# Fields every event carries, whatever its type.
EVENT_SHARED_FIELDS <- c("impact_event_type", "title", "id", "project_id", "tags")


# Builds an event from a response, whatever type it turns out to be.
#
# GET /api/v1/impact/project/{projectId}/event returns a mixed list, so the type
# has to be read from each item before the item can be read.
#
# This is where the old samples came apart. They declared a fixed set of fields
# and rejected anything else, so the day IMPLAN added `isContributionAnalysis` to
# Industry Impact Analysis events, reading one stopped working. Keeping the
# unknown fields instead means a new field is visible rather than fatal.
event_from_api <- function(payload) {
  event_type <- payload$impactEventType
  if (is.null(event_type)) {
    event_type <- ""
  }

  known <- EVENT_FIELDS[[event_type]]
  defaults <- as.list(rep(list(NULL), length(EVENT_SHARED_FIELDS) + length(known)))
  names(defaults) <- c(EVENT_SHARED_FIELDS, known)
  defaults$impact_event_type <- event_type
  defaults$title <- ""

  from_api(payload, defaults = defaults, class_name = "implan_event")
}


# Builds a list of events from a response array.
events_from_api <- function(payload) list_from_api(payload, event_from_api)
