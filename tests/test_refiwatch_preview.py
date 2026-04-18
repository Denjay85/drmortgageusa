import json
import os
import unittest
from unittest.mock import Mock, patch


os.environ.setdefault("DATABASE_URL", "postgresql://preview:preview@localhost/preview")
os.environ.setdefault("META_CONVERSIONS_API_TOKEN", "test-meta-token")
os.environ.setdefault("ENABLE_RATE_UPDATER", "0")

import app  # noqa: E402


class FakeCursor:
    def __init__(self):
        self.queries = []
        self._fetchone_value = (101,)

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchone(self):
        return self._fetchone_value

    def close(self):
        return None


class FakeConnection:
    def __init__(self):
        self.cursor_obj = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        return None


class RefiWatchPreviewTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_refiwatch_host_serves_owned_funnel_index(self):
        response = self.client.get("/", headers={"Host": "refi.watch"})
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("RefiWatch | DrMortgageUSA", body)
        self.assertIn("/assets/", body)

    def test_main_host_still_serves_primary_site(self):
        response = self.client.get("/", headers={"Host": "drmortgageusa.com"})
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Dr.MortgageUSA", body)

    def test_forwarded_refiwatch_host_serves_owned_funnel_index(self):
        response = self.client.get(
            "/",
            headers={
                "Host": "internal.render.local",
                "X-Forwarded-Host": "refi.watch",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("RefiWatch | DrMortgageUSA", body)

    def test_refiwatch_lead_validation_blocks_invalid_payload(self):
        response = self.client.post(
            "/api/refiwatch/lead",
            headers={"Host": "refi.watch"},
            json={"name": "", "email": "bad", "consent": False},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertFalse(payload["success"])
        self.assertTrue(payload["errors"])

    @patch("app.requests.post")
    @patch("app.get_db_connection")
    def test_refiwatch_lead_submission_writes_owned_record_and_forwards(self, mock_db, mock_post):
        fake_conn = FakeConnection()
        mock_db.return_value = fake_conn

        zapier_response = Mock()
        zapier_response.ok = True
        zapier_response.status_code = 200
        zapier_response.text = "ok"

        meta_response = Mock()
        meta_response.ok = True
        meta_response.status_code = 200
        meta_response.text = '{"events_received":1}'

        mock_post.side_effect = [zapier_response, meta_response]

        response = self.client.post(
            "/api/refiwatch/lead",
            headers={"Host": "refi.watch"},
            json={
                "name": "Dennis Ross",
                "email": "dennis@example.com",
                "phone": "850-555-1212",
                "currentRate": "6.75%",
                "consent": True,
                "source": "rate-watch",
                "utmData": json.dumps(
                    {
                        "utm_source": "meta",
                        "utm_campaign": "refiwatch-test",
                        "fbclid": "abc123",
                    }
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["lead_id"], 101)
        self.assertTrue(fake_conn.committed)
        self.assertEqual(mock_post.call_count, 2)

        insert_query, insert_params = fake_conn.cursor_obj.queries[0]
        self.assertIn("INSERT INTO refiwatch_leads", insert_query)
        self.assertEqual(insert_params[0], "Dennis Ross")
        self.assertEqual(insert_params[1], "dennis@example.com")
        self.assertEqual(insert_params[5], "6.75%")


if __name__ == "__main__":
    unittest.main()
