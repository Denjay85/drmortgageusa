import json
import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

os.environ['ENABLE_RATE_UPDATER'] = '0'
import app as backend


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.client = backend.app.test_client()

    def test_all_views_require_authorization_and_are_never_cached(self):
        for path in ('/admin/dashboard', '/admin/mission-control', '/api/mission-control/leads'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertIn(response.status_code, (302, 401))
                self.assertEqual(response.headers['Cache-Control'], 'private, no-store')

    def test_read_only_token_is_separate_from_admin_login(self):
        with patch.dict(os.environ, {'MISSION_CONTROL_LEADS_TOKEN': 'test-only'}), patch.object(backend, 'read_lead_dashboard', return_value={'leads': []}) as read:
            self.assertEqual(self.client.get('/api/mission-control/leads', headers={'Authorization': 'Bearer wrong'}).status_code, 401)
            read.assert_not_called()
            response = self.client.get('/api/mission-control/leads', headers={'Authorization': 'Bearer test-only'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Cache-Control'], 'private, no-store')
            self.assertEqual(self.client.get('/admin/dashboard', headers={'Authorization': 'Bearer test-only'}).status_code, 302)

    def test_saved_message_full_payload_and_safe_html_render(self):
        row = {'id': 2, 'channel': 'website', 'first_name': 'Example', 'created_at': datetime(2026, 10, 13),
               'payload': {'message': '<script>alert(1)</script>\nNeed VA options', 'utm_campaign': 'fall', 'customAnswer': '42'}}
        lead = backend.present_lead(row)
        data = dict(leads=[lead], total_leads=1, queued_leads=1, matched_leads=1, segment_counts={}, sources=[],
                    current_source='', current_channel='', current_segment='', current_status='', messages_only=False,
                    search_query='', page=1, has_next=False)
        with self.client.session_transaction() as session:
            session['admin_logged_in'] = True
        with patch.object(backend, 'read_lead_dashboard', return_value=data):
            for path in ('/admin/dashboard', '/admin/mission-control'):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                self.assertIn('&lt;script&gt;', html)
                self.assertNotIn('<script>alert', html)
                for expected in ('Need VA options', 'utm_campaign', 'customAnswer', 'Mission Control', 'Has a message'):
                    self.assertIn(expected, html)

    def test_legacy_and_manychat_presentation(self):
        self.assertEqual(backend.present_lead({'id': 1, 'payload': '{broken'})['message'], '')
        lead = backend.present_lead({'id': 1, 'channel': 'manychat', 'profile': {'ig_username': 'example'},
                                     'payload': {'notes': 'Hello'}, 'zapier_forwarded': None})
        self.assertEqual(lead['record_key'], 'manychat:1')
        self.assertEqual(lead['ig_username'], 'example')
        self.assertEqual(lead['delivery_status'], 'Not routed through Zapier')

    def test_filter_parameters_pagination_and_connection_cleanup(self):
        conn = Mock(); cur = conn.cursor.return_value
        cur.fetchone.side_effect = [(55,), (60, 3)]
        cur.description = [('id',), ('channel',), ('payload',)]
        cur.fetchall.side_effect = [[(1, 'website', {'message': 'hello'})], [('veteran', 2)], [('website',)]]
        with patch.object(backend, 'get_db_connection', return_value=conn):
            result = backend.read_lead_dashboard({'search': "x'", 'channel': 'manychat', 'messages': '1', 'page': '2'})
        query, params = cur.execute.call_args_list[1].args
        self.assertNotIn("x'", query)
        self.assertIn("%x'%", params)
        self.assertEqual(params[-2:], [50, 50])
        self.assertIn('keyword_leads', query)
        self.assertIn('refiwatch_leads', query)
        self.assertEqual(result['page'], 2)
        cur.close.assert_called_once(); conn.close.assert_called_once()


class ManyChatTests(unittest.TestCase):
    def setUp(self):
        self.client = backend.app.test_client()
        self.payload = {'subscriber_id': '123', 'keyword': 'va', 'name': 'Local test', 'message': 'Can I buy?',
                        'email': 'local@example.test', 'campaign': 'instagram-va', 'secret': 'test-only'}

    def test_capture_fields_and_keep_secret_out_of_storage(self):
        conn = Mock(); conn.cursor.return_value.fetchone.return_value = (4,)
        with patch.object(backend, 'MANYCHAT_WEBHOOK_SECRET', 'test-only'), patch.object(backend, 'PREVIEW_MODE', False), patch.object(backend, 'get_db_connection', return_value=conn):
            response = self.client.post('/api/manychat/enroll', json=self.payload)
        self.assertEqual(response.status_code, 200)
        args = conn.cursor.return_value.execute.call_args.args
        stored = json.loads(args[1][-1])
        self.assertEqual(stored['message'], 'Can I buy?')
        self.assertEqual(stored['keyword'], 'VA')
        self.assertEqual(stored['campaign'], 'instagram-va')
        self.assertNotIn('secret', stored)
        self.assertIn('ON CONFLICT (subscriber_id, keyword)', args[0])
        self.assertIn("NULLIF(EXCLUDED.email, '')", args[0])
        conn.commit.assert_called_once()

    def test_failure_is_retryable_not_false_success(self):
        conn = Mock(); conn.cursor.return_value.execute.side_effect = RuntimeError('private detail')
        with patch.object(backend, 'MANYCHAT_WEBHOOK_SECRET', 'test-only'), patch.object(backend, 'PREVIEW_MODE', False), patch.object(backend, 'get_db_connection', return_value=conn):
            response = self.client.post('/api/manychat/enroll', json=self.payload)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private detail', response.get_data(as_text=True))
        conn.rollback.assert_called_once(); conn.close.assert_called_once()

    def test_unauthorized_invalid_and_preview_never_write(self):
        with patch.object(backend, 'MANYCHAT_WEBHOOK_SECRET', 'test-only'), patch.object(backend, 'get_db_connection') as connect:
            self.assertEqual(self.client.post('/api/manychat/enroll', json=[]).status_code, 400)
            self.assertEqual(self.client.post('/api/manychat/enroll', json={'subscriber_id': '1'}).status_code, 401)
            with patch.object(backend, 'PREVIEW_MODE', True):
                response = self.client.post('/api/manychat/enroll', json=self.payload)
                self.assertFalse(response.get_json()['enrolled'])
            connect.assert_not_called()
