"""Real PostgreSQL regression tests. All outbound integrations are mocked.

CI supplies an ephemeral PostgreSQL service; each run uses a unique schema.
Never point TEST_DATABASE_URL at a production database.
"""
import os
import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import psycopg2
from psycopg2 import sql

os.environ['ENABLE_RATE_UPDATER'] = '0'
import app as production_app


@unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'), 'requires isolated PostgreSQL')
class SubmissionIdempotencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = 'submission_test_' + uuid.uuid4().hex
        cls.dsn = os.environ['TEST_DATABASE_URL']
        with psycopg2.connect(cls.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(cls.schema)))
        with patch.object(production_app, 'get_db_connection', side_effect=cls.connect), \
             patch.object(production_app, 'PREVIEW_MODE', False):
            production_app.init_database()

    @classmethod
    def tearDownClass(cls):
        with psycopg2.connect(cls.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(cls.schema)))

    @classmethod
    def connect(cls):
        return psycopg2.connect(cls.dsn, options='-c search_path=' + cls.schema)

    def setUp(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('TRUNCATE leads RESTART IDENTITY')
        self.payload = dict(firstName='Synthetic', email='unit@example.invalid',
                            source='redesign-contact', segment='Test only',
                            emailConsent=True, callConsent=False, smsConsent=False,
                            eventId='isolated-event-1')
        self.db = patch.object(production_app, 'get_db_connection', side_effect=self.connect).start()
        self.zap = patch.object(production_app, 'forward_to_zapier', return_value={'sent': True}).start()
        self.meta = patch.object(production_app, 'track_meta_server_event', return_value={'sent': True}).start()
        patch.object(production_app, 'PREVIEW_MODE', False).start()
        self.addCleanup(patch.stopall)

    def post(self, **changes):
        with production_app.app.test_client() as client:
            return client.post('/api/quiz-submit', json={**self.payload, **changes})

    def rows(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, event_id, zapier_forwarded, zapier_attempts FROM leads ORDER BY id')
                return cur.fetchall()

    def test_same_id_reuses_saved_receipt_without_resending(self):
        first = self.post().get_json()
        again = self.post().get_json()
        self.assertEqual((first['lead_id'], first['event_id']), (again['lead_id'], again['event_id']))
        self.assertTrue(again['replayed'])
        self.assertEqual(len(self.rows()), 1)
        self.zap.assert_called_once()
        self.meta.assert_called_once()

    def test_simultaneous_requests_save_and_forward_once(self):
        start = threading.Barrier(8)
        def send():
            start.wait(timeout=10)
            return self.post()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: send(), range(8)))
        self.assertTrue(all(r.status_code == 200 for r in results))
        self.assertEqual(len({r.get_json()['lead_id'] for r in results}), 1)
        self.assertEqual(len(self.rows()), 1)
        self.zap.assert_called_once()
        self.meta.assert_called_once()

    def test_replay_during_downstream_call_returns_durable_receipt(self):
        entered, release = threading.Event(), threading.Event()
        def slow_send(payload):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('test timed out')
            return {'sent': True}
        self.zap.side_effect = slow_send
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(self.post)
            self.assertTrue(entered.wait(5))
            try:
                again = self.post()
                self.assertEqual(again.status_code, 200)
                self.assertTrue(again.get_json()['replayed'])
            finally:
                release.set()
            self.assertEqual(first.result().get_json()['lead_id'], again.get_json()['lead_id'])
        self.zap.assert_called_once()

    def test_distinct_ids_preserve_genuine_inquiries_from_same_email(self):
        first = self.post().get_json()
        second = self.post(eventId='isolated-event-2').get_json()
        self.assertNotEqual(first['lead_id'], second['lead_id'])
        self.assertEqual(len(self.rows()), 2)
        self.assertEqual(self.zap.call_count, 2)

    def test_same_id_changed_details_conflicts_without_overwrite(self):
        first = self.post().get_json()
        response = self.post(message='Different inquiry')
        self.assertEqual(response.status_code, 409)
        self.assertNotIn('lead_id', response.get_json())
        self.assertEqual(self.rows()[0][0], first['lead_id'])
        self.zap.assert_called_once()

    def test_validation_failure_does_not_consume_id(self):
        self.assertEqual(self.post(email='invalid').status_code, 400)
        self.assertEqual(self.rows(), [])
        self.assertEqual(self.post().status_code, 200)
        self.zap.assert_called_once()

    def test_rollback_before_save_allows_same_id_retry(self):
        original = production_app.existing_submission
        def fail_after_lock(cur, event_id, payload):
            original(cur, event_id, payload)
            raise RuntimeError('isolated failure before insertion')
        with patch.object(production_app, 'existing_submission', side_effect=fail_after_lock):
            self.assertEqual(self.post().status_code, 500)
        self.assertEqual(self.rows(), [])
        self.assertEqual(self.post().status_code, 200)
        self.zap.assert_called_once()

    def test_unknown_webhook_result_stays_queued_without_public_retry(self):
        self.zap.side_effect = TimeoutError('response lost after remote accept')
        first = self.post().get_json()
        again = self.post().get_json()
        self.assertEqual(first['lead_id'], again['lead_id'])
        self.assertEqual(self.rows()[0][2:], (False, 1))
        self.zap.assert_called_once()
        self.meta.assert_called_once()

    def test_status_write_failure_does_not_allow_second_dispatch(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER TABLE leads ADD CONSTRAINT isolated_fail_status CHECK (zapier_attempts = 0)")
        try:
            self.assertEqual(self.post().status_code, 200)
            self.assertTrue(self.post().get_json()['replayed'])
            self.assertEqual(len(self.rows()), 1)
            self.zap.assert_called_once()
        finally:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute('ALTER TABLE leads DROP CONSTRAINT isolated_fail_status')

    def test_worker_exit_after_save_does_not_automatically_redispatch(self):
        self.zap.side_effect = SystemExit('isolated worker exit')
        with self.assertRaises(SystemExit):
            self.post()
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['replayed'])
        self.assertEqual(self.rows()[0][2:], (False, 0))
        self.zap.assert_called_once()
        self.meta.assert_not_called()

    def test_commit_acknowledgment_loss_reuses_saved_receipt(self):
        class LostCommitAck:
            def __init__(self, conn):
                self.conn = conn
            def __getattr__(self, name):
                return getattr(self.conn, name)
            def commit(self):
                self.conn.commit()
                raise psycopg2.OperationalError('isolated lost commit acknowledgment')
        self.db.side_effect = lambda: LostCommitAck(self.connect())
        self.assertEqual(self.post().status_code, 500)
        self.db.side_effect = self.connect
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['replayed'])
        self.assertEqual(len(self.rows()), 1)
        self.zap.assert_not_called()
        self.meta.assert_not_called()

    def test_invalid_event_ids_do_not_touch_database(self):
        for event_id in ['x' * 151, ['invalid'], 'has whitespace', 99]:
            with self.subTest(event_id=event_id):
                self.assertEqual(self.post(eventId=event_id).status_code, 400)
        self.db.assert_not_called()
        self.zap.assert_not_called()


if __name__ == '__main__':
    unittest.main()
