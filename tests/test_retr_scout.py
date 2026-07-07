import io
import os
import unittest
from unittest.mock import patch


os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("DATABASE_URL", "postgresql://preview:preview@localhost/preview")
os.environ.setdefault("ENABLE_RATE_UPDATER", "0")

import app  # noqa: E402


class RetrFakeCursor:
    def __init__(self):
        self.queries = []
        self.description = None
        self._fetchone_value = None

    def execute(self, query, params=None):
        self.queries.append((query, params))
        if "INSERT INTO retr_import_batches" in query:
            self._fetchone_value = (42,)

    def fetchone(self):
        return self._fetchone_value or (0,)

    def fetchall(self):
        return []

    def close(self):
        return None


class RetrFakeConnection:
    def __init__(self):
        self.cursor_obj = RetrFakeCursor()
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        return None


class RetrScoutTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_scoring_detects_gap_tier_and_team_leader(self):
        target = app.build_retr_target({
            "Agent Name": "Jamie Agent",
            "Brokerage": "Prime Realty",
            "Email": "jamie@example.com",
            "City": "Orlando",
            "Buyer Volume": "$8,000,000",
            "Buyer Units": "16",
            "Seller Volume": "$2,000,000",
            "Seller Units": "4",
            "Preferred Lender": "No",
            "Team Name": "Jamie Agent Group",
        })

        self.assertEqual(target["full_name"], "Jamie Agent")
        self.assertEqual(target["target_tier"], "A")
        self.assertEqual(target["target_score"], 80)
        self.assertTrue(target["lender_loyalty_gap"])
        self.assertTrue(target["team_leader"])
        self.assertTrue(target["bridge_needed"])
        self.assertIn("Draft only - not sent.", target["draft_outreach"])
        self.assertIn("Pre-call battle plan", target["battle_plan"])

    def test_zip_and_lender_loyalty_fields_feed_strategy_stack(self):
        target = app.build_retr_target({
            "Agent Name": "Taylor Zipstack",
            "Market ZIP": "32801",
            "Primary Market": "Downtown Orlando",
            "Total Volume": "$6,000,000",
            "Transactions": "11",
            "Dominant Lender": "Large Retail Bank",
            "Lender Loyalty %": "18%",
        })

        self.assertEqual(target["zip_code"], "32801")
        self.assertEqual(target["primary_zip_codes"], ["32801"])
        self.assertEqual(target["dominant_lender"], "Large Retail Bank")
        self.assertEqual(target["lender_loyalty_pct"], 18)
        self.assertEqual(target["primary_markets"], "Downtown Orlando")
        self.assertTrue(target["lender_loyalty_gap"])
        self.assertIn("ZIP strategy", target["battle_plan"])

        opportunity_score = app.retr_zip_opportunity_score(
            target_count=4,
            avg_loyalty_pct=18,
            gap_count=3,
            priority_count=2,
            bridge_count=1,
        )
        self.assertEqual(opportunity_score, 182.0)

    def test_call_coach_plan_uses_zip_loyalty_and_draft_guardrail(self):
        target = app.build_retr_target({
            "Agent Name": "Casey Coach",
            "Zip Code": "32789",
            "Sales Volume": "$9M",
            "Transactions": "14",
            "Preferred Lender": "No",
            "Lender Loyalty": "12%",
        })

        plan = app.build_retr_call_coach_plan(target)

        self.assertEqual(plan["target"]["primary_zip"], "32789")
        self.assertEqual(plan["zip_strategy"]["lender_loyalty_pct"], 12)
        self.assertIn("Draft-only", plan["guardrail"])
        self.assertIn("strategy call", plan["zip_strategy"]["read"])

    def test_scoring_respects_existing_lender_relationship(self):
        target = app.build_retr_target({
            "Full Name": "Morgan Producer",
            "Sales Volume": "$12M",
            "Transactions": "22",
            "Lender Name": "Trusted Mortgage Partner",
            "Lender Share": "60%",
        })

        self.assertFalse(target["lender_loyalty_gap"])
        self.assertFalse(target["bridge_needed"])
        self.assertTrue(target["has_preferred_lender"])
        self.assertIn(target["target_tier"], ("B", "C"))

    def test_retr_scout_requires_admin_login(self):
        response = self.client.get("/admin/retr-scout")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.headers["Location"])

    def test_zip_rankings_requires_admin_login(self):
        response = self.client.get("/admin/retr-scout/zip-rankings")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.headers["Location"])

    def test_call_coach_station_requires_admin_login(self):
        response = self.client.get("/admin/retr-scout/call-coach")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin", response.headers["Location"])

    def test_call_coach_station_identifies_skill_and_side_panel(self):
        with self.client.session_transaction() as session:
            session["admin_logged_in"] = True

        response = self.client.get("/admin/retr-scout/call-coach")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("RETR Call Coach Sub-Agent", body)
        self.assertIn("$retr-call-coach", body)
        self.assertIn("RETR Scout Side Panel", body)
        self.assertIn("Draft-only guardrail", body)

    @patch("app.requests.post")
    @patch("app.get_db_connection")
    def test_upload_imports_csv_without_external_calls(self, mock_db, mock_post):
        fake_conn = RetrFakeConnection()
        mock_db.return_value = fake_conn
        csv_bytes = (
            b"Agent Name,Brokerage,Email,Buyer Volume,Buyer Units,Preferred Lender\n"
            b"Jamie Agent,Prime Realty,jamie@example.com,$8000000,16,No\n"
        )

        with self.client.session_transaction() as session:
            session["admin_logged_in"] = True

        response = self.client.post(
            "/admin/retr-scout/upload",
            data={"csv_file": (io.BytesIO(csv_bytes), "retr-export.csv")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/retr-scout", response.headers["Location"])
        self.assertTrue(fake_conn.committed)
        self.assertEqual(mock_post.call_count, 0)

        queries = [query for query, _ in fake_conn.cursor_obj.queries]
        self.assertTrue(
            any("INSERT INTO retr_import_batches" in query for query in queries))
        self.assertTrue(
            any("INSERT INTO retr_realtor_targets" in query for query in queries))


if __name__ == "__main__":
    unittest.main()
