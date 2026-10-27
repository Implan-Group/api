"""The command line: what it accepts, and the exit code each kind of failure gets."""

import contextlib
import io
import sys
import unittest
from unittest import mock

import requests

import main
from utilities import config
from utilities.auth import AuthenticationError
from utilities.rest import ImplanApiError, ProblemDetails, TransportError


class ExitCodeTests(unittest.TestCase):
    def exit_code_for(self, error: Exception) -> int:
        """What `python main.py identifiers` returns when the workflow raises `error`."""
        with (
            mock.patch.object(main, "_dispatch", side_effect=error),
            mock.patch.object(sys, "argv", ["main.py", "identifiers"]),
        ):
            return main.main()

    def test_each_failure_gets_its_own_exit_code(self) -> None:
        cases = {
            2: AuthenticationError("refused"),
            3: ImplanApiError("GET", "u", ProblemDetails(status=404, title="Not Found", detail="")),
            4: FileNotFoundError("no workbook"),
            5: TransportError("https://example.invalid", requests.ConnectionError("refused")),
        }
        for code, error in cases.items():
            with self.subTest(error=type(error).__name__):
                self.assertEqual(self.exit_code_for(error), code)


class CommandLineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = main._build_parser()

    def test_regional_exports_options(self) -> None:
        args = self.parser.parse_args(["regional-exports", "--region-type", "County", "--limit", "0"])
        self.assertEqual(args.workflow, "regional-exports")
        self.assertEqual(args.region_type, "County")
        # 0 means every region; the entry point passes `args.limit or None`.
        self.assertEqual(args.limit, 0)

    def test_an_unknown_region_type_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.parser.parse_args(["regions", "--region-type", "Planet"])

    def test_project_id_and_the_default_map_code(self) -> None:
        args = self.parser.parse_args(["run-impact-analysis", "--project-id", "abc-123"])
        self.assertEqual(args.project_id, "abc-123")
        self.assertEqual(args.map_code, "US")


class TitleTests(unittest.TestCase):
    def test_unique_title_carries_the_prefix(self) -> None:
        self.assertTrue(config.unique_title("Label").startswith("ImpactApi Sample - Label - "))

    def test_unique_title_drops_characters_implan_rejects(self) -> None:
        self.assertTrue(config.unique_title("Prince George's County").startswith("ImpactApi Sample - Prince Georges County - "))


if __name__ == "__main__":
    unittest.main()
