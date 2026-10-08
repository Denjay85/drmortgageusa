import json
import os
import unittest
from unittest.mock import Mock, patch

os.environ['ENABLE_RATE_UPDATER'] = '0'
import app as production_app


class LeadAttributionTests(unittest.TestCase):
    def setUp(self):
        self.client = production_app.app.test_client()
        self.connection = Mock()
        self.cursor = self.connection.cursor.return_value
        self.cursor.fetchone.return_value = (42,)
        self.payload = {'firstName': 'Local test', 'email': 'local@example.test',
                        'source': 'redesign-contact', 'eventId': 'local-test-id',
                        'emailConsent': True, 'smsConsent': False, 'callConsent': False}

    def post(self, **payload):
        return self.client.post('/api/quiz-submit', json={**self.payload, **payload})

    def test_attribution_reaches_saved_payload_and_crm_after_commit(self):
        events = []
        self.connection.commit.side_effect = lambda: events.append('commit')
        def zapier(payload):
            events.append('zapier')
            return {'sent': True}
        def meta(*args, **kwargs):
            events.append('meta')
            return {'sent': True}
        touch = json.dumps({'utm_source': 'google', 'gclid': 'test-click', 'landing_path': '/blog/guide',
                            'referrer_origin': 'https://www.google.com/search?q=private',
                            'timestamp': 1791477000000, 'email': 'discard@example.test'})
        with patch.object(production_app, 'PREVIEW_MODE', False), \
             patch.object(production_app, 'get_db_connection', return_value=self.connection), \
             patch.object(production_app, 'forward_to_zapier', side_effect=zapier) as forward, \
             patch.object(production_app, 'track_meta_server_event', side_effect=meta):
            response = self.post(utm_source='google', utm_medium='cpc', gclid='test-click',
                                 firstTouch=touch, lastTouch=touch,
                                 pageUrl='https://drmortgageusa.com/contact?email=private#fragment',
                                 referrer='https://example.test/search?q=private')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(events, ['commit', 'zapier', 'meta', 'commit'])
        saved = json.loads(self.cursor.execute.call_args_list[0].args[1][-1])
        self.assertEqual(saved, forward.call_args.args[0])
        self.assertEqual(saved['gclid'], 'test-click')
        self.assertEqual(saved['utm_source'], 'google')
        self.assertEqual(saved['pageUrl'], 'https://drmortgageusa.com/contact')
        self.assertEqual(saved['referrer'], 'https://example.test')
        first = json.loads(saved['firstTouch'])
        self.assertEqual(first['landing_path'], '/blog/guide')
        self.assertEqual(first['referrer_origin'], 'https://www.google.com')
        self.assertNotIn('email', first)
        self.assertEqual(saved['emailConsent'], True)
        self.connection.close.assert_called_once()
        self.cursor.close.assert_called_once()

    def test_malformed_or_sensitive_attribution_is_removed(self):
        data = {'utm_source': 'person@example.test', 'utm_medium': ['bad'], 'gclid': 'x' * 513,
                'utm_campaign': '<script>', 'utm_term': 'normal term', 'firstTouch': '{broken',
                'lastTouch': json.dumps({'landing_path': '/contact?email=private', 'email': 'private',
                                         'referrer_origin': 'javascript:alert(1)', 'timestamp': float('inf')}),
                'pageUrl': 'https://user:secret@example.test/private?q=secret'}
        production_app.sanitize_lead_attribution(data)
        self.assertEqual(data, {'utm_term': 'normal term', 'pageUrl': ''})

    def test_database_commit_failure_never_forwards_or_reports_a_lead(self):
        self.connection.commit.side_effect = RuntimeError('private database detail')
        with patch.object(production_app, 'PREVIEW_MODE', False), \
             patch.object(production_app, 'get_db_connection', return_value=self.connection), \
             patch.object(production_app, 'forward_to_zapier') as forward, \
             patch.object(production_app, 'track_meta_server_event') as meta:
            response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()['success'])
        self.assertNotIn('private database detail', response.get_data(as_text=True))
        forward.assert_not_called()
        meta.assert_not_called()
        self.connection.rollback.assert_called_once()
        self.connection.close.assert_called_once()

    def test_status_update_failure_keeps_saved_lead_successful(self):
        self.connection.commit.side_effect = [None, RuntimeError('status unavailable')]
        with patch.object(production_app, 'PREVIEW_MODE', False), \
             patch.object(production_app, 'get_db_connection', return_value=self.connection), \
             patch.object(production_app, 'forward_to_zapier', return_value={'sent': True}), \
             patch.object(production_app, 'track_meta_server_event', return_value={'sent': True}):
            response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        self.assertEqual(response.get_json()['lead_id'], 42)
        self.connection.rollback.assert_called_once()
        self.connection.close.assert_called_once()

    def test_optional_integrations_cannot_turn_saved_lead_into_failure(self):
        with patch.object(production_app, 'PREVIEW_MODE', False), \
             patch.object(production_app, 'get_db_connection', return_value=self.connection), \
             patch.object(production_app, 'forward_to_zapier', side_effect=RuntimeError('offline')), \
             patch.object(production_app, 'track_meta_server_event', side_effect=RuntimeError('offline')):
            response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        self.assertFalse(self.cursor.execute.call_args_list[1].args[1][0])

    def test_non_object_json_is_rejected_without_integrations(self):
        with patch.object(production_app, 'get_db_connection') as database:
            response = self.client.post('/api/quiz-submit', json=['invalid'])
        self.assertEqual(response.status_code, 400)
        database.assert_not_called()

    def test_privacy_page_describes_the_actual_measurement_features(self):
        with self.client.get('/privacy') as response:
            page = response.get_data(as_text=True)
        for phrase in ('Google Ads', 'UTM parameters', '30-minute', 'Global Privacy Control', 'Do Not Track'):
            self.assertIn(phrase, page)

    def test_current_main_site_forms_require_real_email_permission(self):
        for source in ('redesign-contact', 'redesign-dpa-review', 'redesign-build-my-plan',
                       'redesign-rate-watch', 'redesign-calculator-save'):
            with self.subTest(source=source), patch.object(production_app, 'get_db_connection') as database:
                response = self.post(source=source, emailConsent=False)
                self.assertEqual(response.status_code, 400)
                database.assert_not_called()

    def test_calls_or_texts_require_a_phone_number(self):
        with patch.object(production_app, 'get_db_connection') as database:
            response = self.post(smsConsent=True, phone='')
        self.assertEqual(response.status_code, 400)
        database.assert_not_called()


if __name__ == '__main__':
    unittest.main()
