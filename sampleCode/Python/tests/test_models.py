"""The request and response models: what they send, and what they tolerate."""

import json
import unittest

import requests

from models.event import Event, EventType, IndustryOutputEvent, event_from_api
from models.group import Group, GroupEvent
from models.region import CombineRegionRequest, Region
from models.results import ImpactResultsExportRequest, ResultFilters


class GroupTests(unittest.TestCase):
    def test_sends_only_the_region_identifier_it_has(self) -> None:
        body = Group(
            title="g",
            hash_id="abc",
            dollar_year=2026,
            group_events=[GroupEvent(event_id="e1"), GroupEvent(event_id="e2")],
        ).to_api()

        self.assertEqual(body["hashId"], "abc")
        self.assertNotIn("urid", body)
        self.assertNotIn("userModelId", body)
        self.assertEqual(len(body["groupEvents"]), 2)

    def test_one_group_event_is_still_an_array(self) -> None:
        body = Group(title="g", hash_id="abc", group_events=[GroupEvent(event_id="e1")]).to_api()
        self.assertIn('"groupEvents": [{', json.dumps(body))

    def test_nested_group_events_read_as_models(self) -> None:
        group = Group.from_api(
            {"title": "g", "groupEvents": [{"eventId": "e", "scalingFactor": 0.5}]}
        )
        self.assertIsInstance(group.group_events[0], GroupEvent)
        self.assertEqual(group.group_events[0].scaling_factor, 0.5)


class EventTests(unittest.TestCase):
    def test_one_tag_is_still_an_array(self) -> None:
        body = IndustryOutputEvent(title="t", industry_code=1, output=1.0, tags=["spending"]).to_api()
        self.assertIn('"tags": ["spending"]', json.dumps(body))

    def test_unknown_fields_are_kept(self) -> None:
        event = event_from_api(
            {"impactEventType": EventType.INDUSTRY_OUTPUT.value, "industryCode": 1, "brandNewField": 42}
        )
        self.assertIsInstance(event, IndustryOutputEvent)
        self.assertEqual(event.industry_code, 1)
        self.assertEqual(event.extra["brandNewField"], 42)

    def test_unknown_event_type_is_read_as_a_plain_event(self) -> None:
        event = event_from_api({"impactEventType": "SomethingNew", "weird": True})
        self.assertIs(type(event), Event)
        self.assertEqual(event.impact_event_type, "SomethingNew")
        self.assertIs(event.extra["weird"], True)


class RegionTests(unittest.TestCase):
    def test_build_status_and_unknown_fields(self) -> None:
        region = Region.from_api(
            {"hashId": "x", "modelBuildStatus": "Complete", "somethingAddedLater": 1}
        )
        self.assertTrue(region.is_built)
        self.assertFalse(region.is_user_defined)
        self.assertEqual(region.extra["somethingAddedLater"], 1)

    def test_a_user_defined_region_says_it_is_yours(self) -> None:
        region = Region.from_api(
            {"hashId": "x", "description": "Two counties", "userModelId": 42}
        )
        self.assertTrue(region.is_user_defined)
        self.assertIn("yours, userModelId=42", region.describe())

    def test_combining_sends_hash_ids_as_an_array(self) -> None:
        body = CombineRegionRequest(description="d", hash_ids=["a", "b"]).to_api()
        self.assertEqual(body["hashIds"], ["a", "b"])


class ResultsTests(unittest.TestCase):
    def test_growth_request_keeps_all_five_arrays_even_empty(self) -> None:
        body = ImpactResultsExportRequest(dollar_year=2026).to_api()
        self.assertEqual(body["dollarYear"], 2026)
        for name in ("regions", "impacts", "groupNames", "eventNames", "eventTags"):
            with self.subTest(name=name):
                self.assertEqual(body[name], [])

    def test_filters_drop_empty_dimensions(self) -> None:
        query = ResultFilters(year=2026, regions=["Oregon (2024)", "Wisconsin (2024)"]).to_query()
        self.assertEqual(
            query,
            {"year": 2026, "regions": ["Oregon (2024)", "Wisconsin (2024)"]},
        )
        self.assertEqual(ResultFilters().to_query(), {})

    def test_a_repeated_filter_becomes_repeated_parameters(self) -> None:
        query = ResultFilters(regions=["Oregon (2024)", "Wisconsin (2024)"]).to_query()
        url = requests.Request("GET", "https://example.invalid/r", params=query).prepare().url
        self.assertIn("regions=Oregon+%282024%29&regions=Wisconsin+%282024%29", url)


if __name__ == "__main__":
    unittest.main()
