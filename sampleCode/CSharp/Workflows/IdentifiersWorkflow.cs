using Implan.ApiSamples.Endpoints;

namespace Implan.ApiSamples.Workflows;

/// <summary>
/// Workflow 2: Identifiers.
/// </summary>
/// <remarks>
/// Goal: discover every id the other workflows need, instead of hardcoding it.
///
/// This is the workflow to read first if you are new to the API, because the ids it
/// resolves are the ones that trip people up. They are not stable across time and
/// not portable across schemes:
///
///   - Industry Set ids change when IMPLAN publishes a new industry vintage.
///   - Dataset ids are specific to an Aggregation Scheme and are not ordered by year.
///   - Industry codes mean different industries in different Industry Sets. Code 509
///     is Full-service restaurants in the 546 set and Federal electric utilities in
///     the 528 set, so a code copied from an old example silently analyzes the wrong
///     industry.
///
/// Nothing here is expensive, and the resolution is four GETs. Do it at the start of
/// a run and pass the result around.
///
/// Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started
/// </remarks>
public static class IdentifiersWorkflow
{
    public static void Run()
    {
        var client = Auth.CreateClient();

        // Step 1. Resolve the United States identifiers. This is the chain every
        // workflow starts with: default Industry Set, its Aggregation Scheme, that
        // scheme's default Dataset, and the scheme's first Household Set.
        ConsoleLog.Heading("Step 1: resolve the current United States identifiers");
        var us = Endpoints.Identifiers.Resolve(client, MapCode.US);

        // Step 2. Show the pieces the resolution walked through, so the chain is
        // visible rather than implied.
        ConsoleLog.Heading("Step 2: the lists those came from");

        // GET /api/v1/industry-sets  (wiki: Get Industry Sets)
        var allSets = Industries.GetIndustrySets(client);
        ConsoleLog.Info("  Industry Sets ({0}). The one flagged default is the current US list:", allSets.Count);
        foreach (var set in allSets)
        {
            var marker = set.IsDefault == true ? " <- default" : string.Empty;
            var active = set.ActiveStatus == true ? string.Empty : "  (retired)";
            ConsoleLog.Info("    {0,3}  {1,-40}{2}{3}", set.Id, set.Description, active, marker);
        }

        // GET /api/v1/datasets/{aggregationSchemeId}  (wiki: Dataset by Aggregation Scheme)
        var schemeDatasets = Datasets.GetDatasetsForScheme(client, us.AggregationSchemeId);
        ConsoleLog.Info();
        ConsoleLog.Info("  Datasets in Aggregation Scheme {0} ({1}). Note that the default is last,",
            us.AggregationSchemeId, schemeDatasets.Count);
        ConsoleLog.Info("  not first, and that these ids are meaningless in another scheme:");
        foreach (var dataset in schemeDatasets)
        {
            var marker = dataset.IsDefault ? " <- default" : string.Empty;
            ConsoleLog.Info("    {0,3}  {1}{2}", dataset.Id, dataset.Description, marker);
        }

        // Step 3. Look an industry up properly. Checking the description alongside
        // the code is what catches a code that has moved between industry vintages.
        ConsoleLog.Heading("Step 3: look up an industry by code, and verify it");

        // GET /api/v1/IndustryCodes/{aggregationSchemeId}
        // (wiki: Industry Codes by Aggregation Scheme)
        // This route takes no query string: the scheme already implies its Industry Set.
        var codes = Industries.GetIndustryCodesForScheme(client, us.AggregationSchemeId);
        ConsoleLog.Info("  {0} industries in this Aggregation Scheme", codes.Count);

        var oilseed = Industries.FindIndustry(codes, 1, "Oilseed farming");
        ConsoleLog.Info("  code {0} is '{1}', as expected", oilseed.Code, oilseed.Description);

        // The portable way round: ask for the industry by name and accept whatever
        // code it has in this scheme. This is what the other workflows do.
        var restaurants = Industries.FindIndustryByDescription(codes, "Full-service restaurants");
        ConsoleLog.Info("  'Full-service restaurants' is code {0} in this Industry Set", restaurants.Code);
        ConsoleLog.Info("  (it is a different code in other sets, which is why the samples look it");
        ConsoleLog.Info("   up by name rather than hardcoding a number)");

        // Step 4. Region types, which are the values the region filters accept.
        ConsoleLog.Heading("Step 4: region types");

        // GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
        var regionTypes = Regions.GetRegionTypes(client);
        ConsoleLog.Info("  {0}", string.Join(", ", regionTypes));
        ConsoleLog.Info("  For Canadian data, State filters to Provinces and County to");
        ConsoleLog.Info("  Economic Regions.");

        // Step 5. The same resolution for Canada and International. Only the US set
        // carries the default flag, so for these two the newest set in use is found
        // through the Aggregation Schemes instead.
        ConsoleLog.Heading("Step 5: the same resolution for Canada and International");
        foreach (var mapCode in new[] { MapCode.CAN, MapCode.INTL })
        {
            try
            {
                // Resolve prints what it found, so there is nothing to do with the
                // return value here.
                Endpoints.Identifiers.Resolve(client, mapCode);
                ConsoleLog.Info();
            }
            catch (KeyNotFoundException error)
            {
                // An account whose subscription does not include Canadian or
                // international data is a normal situation, not a failure.
                ConsoleLog.Info("  {0} is not available on this subscription: {1}", mapCode, error.Message);
            }
        }

        ConsoleLog.Heading("Done");
        ConsoleLog.Info("Use these ids for the rest of this session. Resolve them again next");
        ConsoleLog.Info("run rather than writing them down: IMPLAN publishes new data every");
        ConsoleLog.Info("year, and the defaults move.");
    }
}
