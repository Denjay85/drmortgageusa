import os
import re
import unittest
from unittest.mock import Mock, patch

os.environ['ENABLE_RATE_UPDATER'] = '0'

import app as production_app


class FakeCursor:
    def __init__(self):
        self.executions = []

    def execute(self, query, params=None):
        self.executions.append((query, params))

    def fetchone(self):
        return (101,)

    def close(self):
        return None


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        return None

    def close(self):
        return None


class RedesignIntegrationTests(unittest.TestCase):
    def setUp(self):
        production_app.app.config.update(TESTING=True)
        self.client = production_app.app.test_client()

    def test_redesign_and_legacy_seo_routes_are_available(self):
        sitemap_response = self.client.get('/sitemap.xml')
        sitemap = sitemap_response.get_data(as_text=True)
        sitemap_response.close()
        routes = [
            re.sub(r'^https://drmortgageusa\.com', '', value) or '/'
            for value in re.findall(r'<loc>(.*?)</loc>', sitemap)
        ]
        self.assertGreaterEqual(len(routes), 60)
        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, route)
            if response.content_type.startswith('text/html'):
                self.assertNotIn('—', response.get_data(as_text=True), route)
            response.close()

    def test_live_data_endpoints_feed_the_redesign(self):
        rates = self.client.get('/api/rates')
        self.assertEqual(rates.status_code, 200)
        self.assertIn('Conventional 30-year', rates.get_json()['rates'])

        blog = self.client.get('/api/blog')
        self.assertEqual(blog.status_code, 200)
        self.assertGreaterEqual(len(blog.get_json()['posts']), 40)

        with patch.object(production_app.requests, 'get', side_effect=RuntimeError('offline test')):
            dpa = self.client.get('/api/dpa-rates')
        self.assertEqual(dpa.status_code, 200)
        self.assertFalse(dpa.get_json()['live'])
        self.assertEqual(len(dpa.get_json()['snapshot']['groups']), 5)

    def test_lead_submission_preserves_consent_and_tracking_context(self):
        connection = FakeConnection()
        zapier_response = Mock(ok=True, status_code=200, text='ok')
        payload = {
            'firstName': 'Migration Test',
            'email': 'migration@example.com',
            'phone': '8503468514',
            'segment': 'Purchase mortgage plan',
            'timeline': 'Within 90 days',
            'source': 'redesign-build-my-plan',
            'eventId': 'lead_test_123',
            'emailConsent': True,
            'callConsent': False,
            'smsConsent': True,
            'pathAnswers': '{"goal":"purchase"}',
        }

        with patch.object(production_app, 'get_db_connection', return_value=connection), \
             patch.object(production_app, 'ZAPIER_WEBHOOK_URL', 'https://example.test/hook'), \
             patch.object(production_app.requests, 'post', return_value=zapier_response), \
             patch.object(production_app, 'track_meta_server_event', return_value={'sent': True}):
            response = self.client.post('/api/quiz-submit', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        insert_params = connection.cursor_instance.executions[0][1]
        self.assertEqual(insert_params[11], 'redesign-build-my-plan')
        self.assertEqual(insert_params[12], 'lead_test_123')
        self.assertEqual(insert_params[13:16], (True, False, True))
        self.assertIn('pathAnswers', insert_params[16])


if __name__ == '__main__':
    unittest.main()
