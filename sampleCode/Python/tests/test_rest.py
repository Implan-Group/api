"""The HTTP client: bodies, logging, errors, token refresh, retries, and transport."""

import json
import tempfile
import unittest
from pathlib import Path

import requests

from models.results import ImpactResultsExportRequest
from tests.support import FAKE_TOKEN, client_answering, reply
from utilities.rest import ImplanApiError, TransportError


class RequestTests(unittest.TestCase):
    def test_a_get_carrying_a_body_stays_a_get(self) -> None:
        client, adapter = client_answering(reply(200, "Display Code\r\n1", "text/csv"))
        body = ImpactResultsExportRequest(dollar_year=2026).to_api()

        text = client.get_text("/api/v1/impact/results/EstimatedGrowthPercentage/1", json_body=body)

        sent = adapter.sent[0]
        self.assertEqual(sent.method, "GET")
        self.assertEqual(sent.headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(sent.body)["eventTags"], [])
        self.assertEqual(text, "Display Code\r\n1")

    def test_the_token_never_reaches_the_log(self) -> None:
        client, _ = client_answering(reply(200, "[]"))

        with self.assertLogs("implan", level="DEBUG") as captured:
            client.get_json("/api/v1/region/RegionTypes")

        log = "\n".join(captured.output)
        self.assertIn("RegionTypes", log)
        self.assertIn("Authorization: <redacted>", log)
        self.assertNotIn(FAKE_TOKEN.removeprefix("Bearer "), log)


class ErrorTests(unittest.TestCase):
    def test_an_error_carries_its_problem_details(self) -> None:
        problem = {"title": "Project not found", "detail": "No Project was found.", "traceId": "00-abc-01"}
        client, _ = client_answering(reply(404, json.dumps(problem), "application/problem+json"))

        with self.assertRaises(ImplanApiError) as caught:
            client.get_json("/api/v1/impact/project/x")

        self.assertEqual(caught.exception.status_code, 404)
        self.assertEqual(caught.exception.problem.title, "Project not found")
        self.assertEqual(caught.exception.problem.trace_id, "00-abc-01")

    def test_a_request_that_reaches_nothing_is_a_transport_error(self) -> None:
        client, _ = client_answering(requests.ConnectionError("connection refused"))

        with self.assertRaises(TransportError):
            client.get_json("/x")

    def test_a_transport_error_is_not_an_api_error(self) -> None:
        self.assertFalse(issubclass(TransportError, ImplanApiError))


class TokenRefreshTests(unittest.TestCase):
    def test_a_401_refreshes_the_token_once_and_retries(self) -> None:
        refreshes: list[int] = []
        client, _ = client_answering(
            reply(401),
            reply(200, '{"ok": true}'),
            token_refresher=lambda: refreshes.append(1) or FAKE_TOKEN,
        )

        self.assertEqual(client.get_json("/x"), {"ok": True})
        self.assertEqual(len(refreshes), 1)

    def test_a_second_401_is_raised_without_refreshing_again(self) -> None:
        refreshes: list[int] = []
        client, _ = client_answering(
            reply(401),
            reply(401),
            token_refresher=lambda: refreshes.append(1) or FAKE_TOKEN,
        )

        with self.assertRaises(ImplanApiError) as caught:
            client.get_json("/x")

        self.assertEqual(caught.exception.status_code, 401)
        self.assertEqual(len(refreshes), 1)

    def test_an_upload_retried_after_a_401_sends_the_whole_file_again(self) -> None:
        workbook = b"stand-in workbook bytes"
        client, adapter = client_answering(
            reply(401),
            reply(200, '{"ok": true}'),
            token_refresher=lambda: FAKE_TOKEN,
        )

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "template.xlsx"
            path.write_bytes(workbook)
            client.post_file("/x", field_name="excelFile", file_path=path)

        self.assertEqual(len(adapter.sent), 2)
        for request in adapter.sent:
            self.assertIn(workbook, request.body)


class RetryTests(unittest.TestCase):
    def test_a_503_is_retried_when_the_api_says_when(self) -> None:
        client, adapter = client_answering(
            reply(503, headers={"Retry-After": "0"}),
            reply(200, "[]"),
        )

        self.assertEqual(client.get_json("/x"), [])
        self.assertEqual(len(adapter.sent), 2)

    def test_a_get_is_retried_after_a_gateway_timeout(self) -> None:
        client, adapter = client_answering(
            reply(504, headers={"Retry-After": "0"}),
            reply(200, "[]"),
        )

        self.assertEqual(client.get_json("/x"), [])
        self.assertEqual(len(adapter.sent), 2)

    def test_a_post_is_not_retried_after_a_gateway_timeout(self) -> None:
        # The API behind the gateway may already have acted, so a second POST could
        # start a second run.
        client, adapter = client_answering(
            reply(504, headers={"Retry-After": "0"}),
            reply(200, "1"),
        )

        with self.assertRaises(ImplanApiError) as caught:
            client.post_json("/x", json_body={})

        self.assertEqual(caught.exception.status_code, 504)
        self.assertEqual(len(adapter.sent), 1)

    def test_a_post_is_retried_after_a_503(self) -> None:
        client, adapter = client_answering(
            reply(503, headers={"Retry-After": "0"}),
            reply(200, "1"),
        )

        self.assertEqual(client.post_json("/x", json_body={}), 1)
        self.assertEqual(len(adapter.sent), 2)


class BodyTests(unittest.TestCase):
    def test_an_empty_json_body_reads_as_none(self) -> None:
        client, _ = client_answering(reply(200, ""))

        self.assertIsNone(client.get_json("/x"))

    def test_csv_with_no_charset_is_read_as_utf8(self) -> None:
        client, _ = client_answering(reply(200, "Region\r\nQuébec", "text/csv"))

        self.assertEqual(client.get_text("/x"), "Region\r\nQuébec")

    def test_a_charset_the_api_names_is_honored(self) -> None:
        client, _ = client_answering(reply(200, "Region\r\nQuébec", "text/csv; charset=utf-8"))

        self.assertEqual(client.get_text("/x"), "Region\r\nQuébec")


if __name__ == "__main__":
    unittest.main()
