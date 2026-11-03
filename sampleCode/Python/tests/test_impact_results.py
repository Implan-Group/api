"""Reading a results report back: the effect totals the MRIO workflow prints."""

import unittest

from endpoints import impact_results
from models.results import EffectTotals

# A Summary Economic Indicators report as the API writes it: spaces after the
# header's commas, a Group name that needs quotes, and a closing "Totals" row.
REPORT = (
    "GroupName, EventName, ModelName, Impact, Employment, LaborIncome, ValueAdded, Output, TagName\r\n"
    '"Smith, Inc (2024)",Restaurants,Oregon (2024),1 - Direct,10.5,100,200,1000,\r\n'
    '"Smith, Inc (2024)",Restaurants,Oregon (2024),2 - Indirect,1.25,10,20,300,\r\n'
    '"Smith, Inc (2024)",Restaurants,Oregon (2024),3 - Induced,0.25,5,10,200,\r\n'
    "Totals,,,,12,115,230,1500,\r\n"
)


class EffectTotalsTests(unittest.TestCase):
    def test_direct_is_split_from_the_rest_and_the_totals_row_is_skipped(self) -> None:
        self.assertEqual(
            impact_results.effect_totals(REPORT),
            EffectTotals(direct_output=1000, indirect_and_induced_output=500, employment=12),
        )

    def test_a_report_without_an_impact_column_says_so(self) -> None:
        with self.assertRaisesRegex(ValueError, "Impact"):
            impact_results.effect_totals("GroupName,Output,Employment\r\nOregon (2024),1000,10\r\n")


if __name__ == "__main__":
    unittest.main()
