"""Case conversion between the API's camelCase and Python's snake_case."""

import unittest

from utilities.json_helper import camel_case, snake_case


class CaseConversionTests(unittest.TestCase):
    def test_snake_case(self) -> None:
        cases = {
            "hashId": "hash_id",
            "isMrioAllowed": "is_mrio_allowed",
            "m49Code": "m49_code",
        }
        for api_name, python_name in cases.items():
            with self.subTest(api_name=api_name):
                self.assertEqual(snake_case(api_name), python_name)

    def test_camel_case(self) -> None:
        cases = {
            "hash_ids": "hashIds",
            "dollar_year": "dollarYear",
        }
        for python_name, api_name in cases.items():
            with self.subTest(python_name=python_name):
                self.assertEqual(camel_case(python_name), api_name)

    def test_round_trip(self) -> None:
        name = "spendingPatternCommodities"
        self.assertEqual(camel_case(snake_case(name)), name)


if __name__ == "__main__":
    unittest.main()
