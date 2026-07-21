import unittest
from datetime import datetime, timezone

from update_rates import parse_mnd_snapshot, snapshot_is_fresh


MND_TABLE_FIXTURE = '''
<div class="historical-chart">30 Yr. Fixed 6.04%</div>
<div class="last-updated" style="font-weight: normal;">as of 7/20/26</div>
<a href="/mortgage-rates/mnd">Mortgage News Daily</a>
<table>
  <tr><td class="rate-product"><a href="/mortgage-rates/30-year-fixed">30 Yr. Fixed</a></td><td class="rate">6.71%</td></tr>
  <tr><td class="rate-product"><a href="/mortgage-rates/15-year-fixed">15 Yr. Fixed</a></td><td class="rate">6.18%</td></tr>
  <tr><td class="rate-product"><a href="/mortgage-rates/30-year-jumbo">30 Yr. Jumbo</a></td><td class="rate">6.84%</td></tr>
  <tr><td class="rate-product"><a href="/mortgage-rates/30-year-fha">30 Yr. FHA</a></td><td class="rate">6.30%</td></tr>
  <tr><td class="rate-product"><a href="/mortgage-rates/30-year-va">30 Yr. VA</a></td><td class="rate">6.32%</td></tr>
</table>
<div class="last-updated">as of 7/16/26</div>
<a href="/mortgage-rates/freddie-mac">Freddie Mac</a>
'''


class MortgageNewsDailyParserTests(unittest.TestCase):
    def test_parser_uses_current_daily_index_not_historical_page_data(self):
        snapshot = parse_mnd_snapshot(MND_TABLE_FIXTURE)

        self.assertEqual(snapshot['as_of'], '2026-07-20')
        self.assertEqual(snapshot['rates']['conv30'], '6.71')
        self.assertEqual(snapshot['rates']['conv15'], '6.18')
        self.assertEqual(snapshot['rates']['jumbo30'], '6.84')
        self.assertEqual(snapshot['rates']['fha30'], '6.30')
        self.assertEqual(snapshot['rates']['va30'], '6.32')
        self.assertNotIn('usda30', snapshot['rates'])

    def test_parser_rejects_an_incomplete_daily_index(self):
        incomplete = MND_TABLE_FIXTURE.replace(
            '<tr><td class="rate-product"><a href="/mortgage-rates/30-year-va">30 Yr. VA</a></td><td class="rate">6.32%</td></tr>',
            '',
        )

        with self.assertRaisesRegex(ValueError, '30 Yr. VA'):
            parse_mnd_snapshot(incomplete)

    def test_freshness_allows_a_long_weekend_but_rejects_old_data(self):
        snapshot = {'as_of': '2026-07-17'}
        monday = datetime(2026, 7, 20, tzinfo=timezone.utc)
        wednesday = datetime(2026, 7, 22, tzinfo=timezone.utc)

        self.assertTrue(snapshot_is_fresh(snapshot, now=monday))
        self.assertFalse(snapshot_is_fresh(snapshot, now=wednesday))


if __name__ == '__main__':
    unittest.main()
