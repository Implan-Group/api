"""Dataset endpoints.

A Dataset is one data year within one Aggregation Scheme. IMPLAN publishes data
annually and flags the newest complete year as the default.

Dataset ids are scheme-specific and are not ordered by year, so never carry an id
from one scheme to another and never assume the newest is last in the list. Read
the list for your scheme and take the entry flagged `is_default`.

Wiki: Datasets - https://github.com/Implan-Group/api/wiki/Datasets
"""

from models.reference import Dataset
from utilities.rest import ApiClient


def get_datasets_for_scheme(
    client: ApiClient, aggregation_scheme_id: int
) -> list[Dataset]:
    """List the data years available for one Aggregation Scheme.

    GET /api/v1/datasets/{aggregationSchemeId}
    (wiki: Dataset by Aggregation Scheme)
    """
    payload = client.get_json(f"/api/v1/datasets/{aggregation_scheme_id}")
    return Dataset.list_from_api(payload)


def get_datasets(client: ApiClient) -> list[Dataset]:
    """List the data years for the current default Aggregation Scheme.

    GET /api/v1/datasets  (wiki: Datasets)

    The scheme-scoped call above is almost always the one you want, because it
    makes the scheme the ids belong to explicit.
    """
    payload = client.get_json("/api/v1/datasets")
    return Dataset.list_from_api(payload)


def default_dataset(datasets: list[Dataset]) -> Dataset:
    """Pick the default data year out of a list.

    The default is flagged rather than ordered: it is often the last entry, so
    taking the first would quietly select 2001. Exactly one entry carries the flag.
    """
    for dataset in datasets:
        if dataset.is_default:
            return dataset
    raise LookupError(
        "No Dataset in this Aggregation Scheme is flagged as the default. "
        "Choose one explicitly by description."
    )
