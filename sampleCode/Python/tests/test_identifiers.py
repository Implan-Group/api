"""Resolving identifiers from an existing Project rather than from today's defaults."""

import json
import unittest

from endpoints import identifiers
from models.project import Project
from models.reference import MapCode
from tests.support import client_answering, reply

# A Project on an older Industry Set: scheme 8 is not the current default.
OLDER_SCHEME = {
    "id": 8,
    "description": "546 Unaggregated",
    "industrySetId": 8,
    "householdSetIds": [1],
    "mapCode": "US",
    "status": "Complete",
}
INDUSTRY_SETS = [
    {"id": 8, "description": "546 Industries", "isDefault": False, "activeStatus": True, "defaultAggregationSchemeId": 8},
    {"id": 12, "description": "528 Industries", "isDefault": True, "activeStatus": True, "defaultAggregationSchemeId": 14},
]
SCHEME_DATASETS = [
    {"id": 86, "description": "2021", "isDefault": False},
    {"id": 87, "description": "2022", "isDefault": True},
]


class ResolveForProjectTests(unittest.TestCase):
    def test_identifiers_come_from_the_projects_own_scheme(self) -> None:
        client, adapter = client_answering(
            reply(200, json.dumps(OLDER_SCHEME)),
            reply(200, json.dumps(INDUSTRY_SETS)),
            reply(200, json.dumps(SCHEME_DATASETS)),
        )
        project = Project(title="Older", aggregation_scheme_id=8, household_set_id=3)

        ids = identifiers.resolve_for_project(client, project)

        self.assertEqual(ids.aggregation_scheme_id, 8)
        self.assertEqual(ids.industry_set.id, 8)
        self.assertEqual(ids.dataset_id, 87)
        self.assertEqual(ids.household_set_id, 3)
        self.assertIs(ids.map_code, MapCode.US)
        self.assertTrue(adapter.sent[0].url.endswith("/api/v1/aggregationSchemes/8"))
        self.assertTrue(adapter.sent[2].url.endswith("/api/v1/datasets/8"))

    def test_the_map_code_comes_from_the_scheme(self) -> None:
        canadian = {**OLDER_SCHEME, "id": 9, "industrySetId": 8, "mapCode": "CAN"}
        client, _ = client_answering(
            reply(200, json.dumps(canadian)),
            reply(200, json.dumps(INDUSTRY_SETS)),
            reply(200, json.dumps(SCHEME_DATASETS)),
        )
        project = Project(title="Canadian", aggregation_scheme_id=9, household_set_id=1)

        ids = identifiers.resolve_for_project(client, project)

        self.assertIs(ids.map_code, MapCode.CANADA)


if __name__ == "__main__":
    unittest.main()
