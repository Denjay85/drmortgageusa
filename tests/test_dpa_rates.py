import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock, patch

import requests
import dpa_rates as dpa

FIXTURE = (Path(__file__).parent / 'fixtures/dpa-2026-11-03.html').read_text()


class DpaRateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.cache = dpa.DpaRateCache(Path(self.temp.name) / 'sheet.json')
        self.response = Mock(text=FIXTURE)

    def tearDown(self):
        self.temp.cleanup()

    def test_official_sheet_all_eighteen_rates_and_funding(self):
        snapshot = dpa.parse_snapshot(FIXTURE)
        self.assertEqual(snapshot['asOf'], 'November 3, 2026')
        self.assertEqual(snapshot['heroesFunding'], 'Over $20 Million Available in Hometown Heroes DPA')
        actual = {g['id']: [e['rate'] for e in g['entries']] for g in snapshot['groups']}
        self.assertEqual(actual, {
            'heroes-bond': ['7.000%', '7.500%', '7.000%'],
            'heroes-tba': ['7.125%', '7.250%', '7.375%'],
            'standard-bond': ['8.000%', '8.250%', '7.750%'],
            'standard-tba': ['8.250%', '7.875%', '8.000%'],
            'plus-tba': ['7.750%', '8.000%', '8.375%', '7.875%', '8.250%', '8.500%'],
        })

    def test_timeout_retries_then_persists_complete_source_sheet(self):
        with patch.object(dpa.requests, 'get', side_effect=[requests.Timeout(), self.response]) as get, \
                patch.object(dpa.time, 'sleep'):
            self.cache.refresh()
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args.kwargs['timeout'], (8, 45))
        self.assertTrue(self.cache.payload()['live'])
        restored = dpa.DpaRateCache(self.cache.path)
        self.assertEqual(restored.record, self.cache.record)

    def test_exhausted_timeouts_preserve_last_good_and_back_off(self):
        before = copy.deepcopy(self.cache.record)
        with patch.object(dpa.requests, 'get', side_effect=requests.Timeout('slow')), patch.object(dpa.time, 'sleep'):
            self.cache.refresh()
        with patch.object(dpa.threading, 'Thread') as thread:
            payload = self.cache.payload(force=True)
        self.assertFalse(payload['live'])
        self.assertFalse(payload['refreshing'])
        thread.assert_not_called()
        self.assertEqual(self.cache.record, before)
        self.assertGreater(self.cache.next_attempt, time.monotonic())

    def test_partial_sheet_never_overwrites_cache(self):
        before = copy.deepcopy(self.cache.record)
        broken = FIXTURE.replace('8.500%', 'missing').replace('8.000%', '9.000%')
        with patch.object(dpa.requests, 'get', return_value=Mock(text=broken)):
            self.cache.refresh()
        self.assertEqual(self.cache.record, before)
        self.assertFalse(self.cache.payload()['live'])
        self.assertFalse(self.cache.path.exists())

    def test_missing_funding_future_date_and_date_regression_rejected(self):
        for html in [FIXTURE.replace('Over $20 Million Available in Hometown Heroes DPA', ''),
                     FIXTURE.replace('November 3, 2026', 'November 3, 2099'),
                     FIXTURE.replace('November 3, 2026', 'July 15, 2026')]:
            before = copy.deepcopy(self.cache.record)
            with patch.object(dpa.requests, 'get', return_value=Mock(text=html)):
                self.cache.refresh()
            self.assertEqual(self.cache.record, before)
            self.assertFalse(self.cache.payload()['live'])

    def test_requests_return_immediately_and_launch_only_one_refresh(self):
        with patch.object(dpa.threading, 'Thread') as thread:
            first = self.cache.payload()
            second = self.cache.payload(force=True)
        thread.assert_called_once()
        self.assertTrue(first['refreshing'])
        self.assertTrue(second['refreshing'])
        self.assertFalse(first['live'])

    def test_force_refresh_throttled_and_old_sheet_not_live(self):
        self.cache.next_attempt = time.monotonic() + 300
        self.cache.last_success = time.monotonic()
        with patch.object(dpa.threading, 'Thread') as thread:
            self.cache.payload(force=True)
            thread.assert_not_called()
            self.cache.last_success -= 61
            self.cache.payload(force=True)
            thread.assert_called_once()
        self.cache.record['snapshot']['asOf'] = 'July 15, 2026'
        self.assertTrue(self.cache.payload()['stale'])
        self.assertFalse(self.cache.payload()['live'])

    def test_corrupt_disk_cache_falls_back_to_verified_seed(self):
        self.cache.path.write_text('{broken')
        self.assertEqual(dpa.DpaRateCache(self.cache.path).record['snapshot'], self.cache.record['snapshot'])


if __name__ == '__main__':
    unittest.main()
