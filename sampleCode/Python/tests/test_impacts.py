"""Starting an impact run and reading its status, both of which answer in plain text."""

import unittest

from endpoints import impacts
from models.results import ImpactStatus
from tests.support import client_answering, reply


class ImpactStatusTests(unittest.TestCase):
    def test_status_is_read_as_text_with_or_without_quotes(self) -> None:
        for body, content_type in (("Complete", "text/plain"), ('"Complete"', "application/json")):
            with self.subTest(body=body):
                client, _ = client_answering(reply(200, body, content_type))
                self.assertEqual(impacts.get_impact_status(client, 1), ImpactStatus.COMPLETE)

    def test_an_unknown_status_is_reported_not_guessed(self) -> None:
        client, _ = client_answering(reply(200, "SomethingNew", "text/plain"))
        self.assertEqual(impacts.get_impact_status(client, 1), ImpactStatus.UNKNOWN)

    def test_a_run_id_is_a_bare_number(self) -> None:
        client, _ = client_answering(reply(200, "30542"))
        self.assertEqual(impacts.run_impact(client, "project"), 30542)


if __name__ == "__main__":
    unittest.main()
