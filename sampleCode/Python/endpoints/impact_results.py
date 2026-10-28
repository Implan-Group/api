"""Reading the results of a completed impact run.

Every endpoint here returns CSV as text. Save it with a `.csv` extension and it
opens in Excel or Sheets. All of them take the same optional filters, so the same
run can be read whole or sliced by region, impact type, group, event, or tag.

Only read these once the run reports `Complete`.

Wiki: Impact Results - https://github.com/Implan-Group/api/wiki/Impact-Results
"""

from pathlib import Path

from models.results import ImpactResultsExportRequest, ResultFilters
from utilities import logging_setup
from utilities.rest import ApiClient

_RESULTS = "/api/v1/impact/results"


def get_summary_economic_indicators(
    client: ApiClient, run_id: int, filters: ResultFilters | None = None
) -> str:
    """Employment, Labor Income, Value Added, and Output by impact type.

    GET /api/v1/impact/results/SummaryEconomicIndicators/{runId}
    (wiki: Results - Summary Economic Indicators)

    The headline report, and the one to start with. Rows are split Direct,
    Indirect, and Induced for each Group, Event, and Region.
    """
    params = (filters or ResultFilters()).to_query()
    return client.get_text(f"{_RESULTS}/SummaryEconomicIndicators/{run_id}", params=params)


def get_detailed_economic_indicators(
    client: ApiClient, run_id: int, filters: ResultFilters | None = None
) -> str:
    """The same indicators, broken out by industry.

    GET /api/v1/impact/results/ExportDetailEconomicIndicators/{runId}
    (wiki: Results - Detailed Economic Indicators)

    Note the year in parentheses after a Group or Model name in this report: that
    is the Data Year of the underlying dataset, not the Dollar Year the figures are
    expressed in. They differ whenever you analyze an older data year in today's
    dollars.
    """
    params = (filters or ResultFilters()).to_query()
    return client.get_text(
        f"{_RESULTS}/ExportDetailEconomicIndicators/{run_id}", params=params
    )


def get_summary_taxes(
    client: ApiClient, run_id: int, filters: ResultFilters | None = None
) -> str:
    """Tax revenue by level of government.

    GET /api/v1/impact/results/SummaryTaxes/{runId}
    (wiki: Results - Summary Taxes)
    """
    params = (filters or ResultFilters()).to_query()
    return client.get_text(f"{_RESULTS}/SummaryTaxes/{run_id}", params=params)


def get_detailed_taxes(
    client: ApiClient, run_id: int, filters: ResultFilters | None = None
) -> str:
    """Tax revenue by tax type and level of government.

    GET /api/v1/impact/results/DetailedTaxes/{runId}
    (wiki: Results - Detailed Taxes)
    """
    params = (filters or ResultFilters()).to_query()
    return client.get_text(f"{_RESULTS}/DetailedTaxes/{run_id}", params=params)


def get_estimated_growth_percentage(
    client: ApiClient, run_id: int, request: ImpactResultsExportRequest
) -> str:
    """How large the impact is relative to each industry already in the region.

    GET /api/v1/impact/results/EstimatedGrowthPercentage/{runId}
    (wiki: Results - Estimated Growth Percentage)

    This one is different from its neighbours in two ways, and both matter.

    First, it takes its filters as a JSON body rather than as query parameters, on
    a GET. That is unusual, it is what the endpoint requires, and IMPLAN's API
    Gateway passes the body through, so do not rewrite it as a POST or move the
    filters to the query string.

    Second, all five filter lists have to be present even when empty. Send `[]` for
    any dimension you are not filtering on; omitting one is an error rather than a
    default. `ImpactResultsExportRequest` defaults them to empty lists for exactly
    this reason.

    A 409 means the run has not finished, or that its project has no completed run
    to compare against.
    """
    return client.get_text(
        f"{_RESULTS}/EstimatedGrowthPercentage/{run_id}",
        json_body=request.to_api(),
    )


def save_csv(csv_text: str, destination: Path) -> Path:
    """Write a CSV report to disk, creating the folder if it is not there.

    Written as UTF-8 with `newline=""` so the line endings the API sent survive
    intact instead of being doubled on Windows.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8", newline="") as handle:
        handle.write(csv_text)
    logging_setup.get_logger().info("  saved %s", destination)
    return destination
