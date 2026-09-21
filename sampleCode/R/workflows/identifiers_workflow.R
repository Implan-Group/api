# Workflow 2: Identifiers.
#
# Goal: discover every id the other workflows need, instead of hardcoding it.
#
# This is the workflow to read first if you are new to the API, because the ids
# it resolves are the ones that trip people up. They are not stable across time
# and not portable across schemes:
#
#   - Industry Set ids change when IMPLAN publishes a new industry vintage.
#   - Dataset ids are specific to an Aggregation Scheme and are not ordered by
#     year.
#   - Industry codes mean different industries in different Industry Sets. Code
#     509 is Full-service restaurants in the 546 set and Federal electric
#     utilities in the 528 set, so a code copied from an old example silently
#     analyzes the wrong industry.
#
# Nothing here is expensive, and the resolution is four GETs. Do it at the start
# of a run and pass the result around.
#
# Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started


identifiers_workflow <- function() {
  client <- create_client()

  # Step 1. Resolve the United States identifiers. This is the chain every
  # workflow starts with: default Industry Set, its Aggregation Scheme, that
  # scheme's default Dataset, and the scheme's first Household Set.
  log_heading("Step 1: resolve the current United States identifiers")
  us <- resolve_identifiers(client, MAP_CODES[["US"]])

  # Step 2. Show the pieces the resolution walked through, so the chain is
  # visible rather than implied.
  log_heading("Step 2: the lists those came from")

  # GET /api/v1/industry-sets  (wiki: Get Industry Sets)
  all_sets <- get_industry_sets(client)
  log_info(
    "  Industry Sets (%d). The one flagged default is the current US list:",
    length(all_sets)
  )
  for (industry_set in all_sets) {
    marker <- if (isTRUE(industry_set$is_default)) " <- default" else ""
    active <- if (isTRUE(industry_set$active_status)) "" else "  (retired)"
    log_info("    %3s  %-40s%s%s", industry_set$id, industry_set$description, active, marker)
  }

  # GET /api/v1/datasets/{aggregationSchemeId}
  # (wiki: Dataset by Aggregation Scheme)
  scheme_datasets <- get_datasets_for_scheme(client, us$aggregation_scheme_id)
  log_info("")
  log_info(
    "  Datasets in Aggregation Scheme %s (%d). Note that the default is last,",
    us$aggregation_scheme_id, length(scheme_datasets)
  )
  log_info("  not first, and that these ids are meaningless in another scheme:")
  for (dataset in scheme_datasets) {
    marker <- if (isTRUE(dataset$is_default)) " <- default" else ""
    log_info("    %3s  %s%s", dataset$id, dataset$description, marker)
  }

  # Step 3. Look an industry up properly. Checking the description alongside the
  # code is what catches a code that has moved between industry vintages.
  log_heading("Step 3: look up an industry by code, and verify it")

  # GET /api/v1/IndustryCodes/{aggregationSchemeId}
  # (wiki: Industry Codes by Aggregation Scheme)
  # This route takes no query string: the scheme already implies its Industry
  # Set.
  codes <- get_industry_codes_for_scheme(client, us$aggregation_scheme_id)
  log_info("  %d industries in this Aggregation Scheme", length(codes))

  oilseed <- find_industry(codes, 1, "Oilseed farming")
  log_info("  code %s is '%s', as expected", oilseed$code, oilseed$description)

  # The portable way round: ask for the industry by name and accept whatever code
  # it has in this scheme. This is what the other workflows do for restaurants.
  restaurants <- find_industry_by_description(codes, "Full-service restaurants")
  log_info("  'Full-service restaurants' is code %s in this Industry Set", restaurants$code)
  log_info("  (it is a different code in other sets, which is why the samples look it")
  log_info("   up by name rather than hardcoding a number)")

  # Step 4. Region types, which are the values the region filters accept.
  log_heading("Step 4: region types")

  # GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
  region_types <- get_region_types(client)
  log_info("  %s", paste(region_types, collapse = ", "))
  log_info("  For Canadian data, State filters to Provinces and County to")
  log_info("  Economic Regions.")

  # Step 5. The same resolution for Canada and International. Only the US set
  # carries the default flag, so for these two the newest set in use is found
  # through the Aggregation Schemes instead.
  log_heading("Step 5: the same resolution for Canada and International")
  for (map_code in c(MAP_CODES[["CANADA"]], MAP_CODES[["INTERNATIONAL"]])) {
    tryCatch(
      {
        # `resolve_identifiers()` prints what it found, so there is nothing to do
        # with the return value here.
        resolve_identifiers(client, map_code)
        log_info("")
      },
      error = function(condition) {
        # An account whose subscription does not include Canadian or
        # international data is a normal situation, not a failure.
        log_info(
          "  %s is not available on this subscription: %s",
          map_code, conditionMessage(condition)
        )
      }
    )
  }

  log_heading("Done")
  log_info("Use these ids for the rest of this session. Resolve them again next")
  log_info("run rather than writing them down: IMPLAN publishes new data every")
  log_info("year, and the defaults move.")

  invisible(NULL)
}
