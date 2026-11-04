"""BulkFromCsv's input files: read strictly, and checked before anything is created."""

import tempfile
import unittest
from pathlib import Path

from workflows import bulk_from_csv_workflow as bulk


def read(text: str, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Read `text` as an input file with the workflow's own reader."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "input.csv"
        path.write_text(text, encoding="utf-8")
        return bulk._read_csv(path, columns)


def region(fips: str, model_name: str, line: int = 2) -> dict[str, str]:
    return {"fips": fips, "region_description": "", "model_name": model_name, "line": str(line)}


def event(name: str, code: str = "1", kind: str = "Industry Output", value: str = "1000", line: int = 2) -> dict[str, str]:
    return {"Name": name, "Code": code, "Type": kind, "Value": value, "line": str(line)}


class ReadCsvTests(unittest.TestCase):
    def test_an_unquoted_comma_is_reported_with_its_line(self) -> None:
        text = "fips,region_description,model_name\n41019,Douglas County, OR,MyModel\n"
        with self.assertRaisesRegex(ValueError, "line 2 .*double quotes"):
            read(text, bulk.REGION_COLUMNS)

    def test_a_quoted_comma_is_one_value(self) -> None:
        text = 'fips,region_description,model_name\n41019,"Douglas County, OR",MyModel\n'
        self.assertEqual(read(text, bulk.REGION_COLUMNS)[0]["model_name"], "MyModel")

    def test_a_semicolon_file_is_reported_as_not_comma_separated(self) -> None:
        text = "fips;region_description;model_name\n41019;Douglas;MyModel\n"
        with self.assertRaisesRegex(ValueError, "comma-separated"):
            read(text, bulk.REGION_COLUMNS)

    def test_rows_of_bare_commas_are_skipped(self) -> None:
        text = "fips,region_description,model_name\n41019,Douglas,MyModel\n,,\n,,\n"
        self.assertEqual(len(read(text, bulk.REGION_COLUMNS)), 1)


class CheckInputsTests(unittest.TestCase):
    def test_good_rows_pass_and_are_normalized(self) -> None:
        states = [region("1000", "South"), region("1", "South", line=3)]
        events = [event("Output", value="$1,000,000")]

        bulk._check_inputs(states, [], events)

        self.assertEqual([row["fips"] for row in states], ["01000", "01"])
        self.assertEqual(events[0]["Value"], "1000000")

    def test_every_problem_is_reported_at_once(self) -> None:
        states = [region("ABC", "Lane & Douglas")]
        counties = [region("41019", "Lane & Douglas")]
        events = [
            event("Food", kind="Household Income"),
            event("Food", code="x", value="lots", line=3),
        ]

        with self.assertRaises(ValueError) as caught:
            bulk._check_inputs(states, counties, events)

        message = str(caught.exception)
        for expected in (
            "'ABC' is not a state or county FIPS code",
            "contains &",
            "is in both state_based.csv and county_based.csv",
            "is not Industry Output or Commodity Output",
            "'Food' is already used",
            "Code 'x' is not a whole number",
            "Value 'lots' is not an amount",
        ):
            self.assertIn(expected, message)

    def test_at_least_one_region_and_one_event_are_needed(self) -> None:
        with self.assertRaises(ValueError) as caught:
            bulk._check_inputs([], [], [])

        self.assertIn("both empty", str(caught.exception))
        self.assertIn("demo_events.csv is empty", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
