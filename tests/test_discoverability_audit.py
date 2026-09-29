import json
import unittest
from scripts.audit_discoverability import (
    BRAND_ID, EMPLOYER_ID, EXPERIENCE, ORIGIN, PERSON_ID, REQUIRED_LINKS,
    BOT_AGENTS, POLICY_TOKENS, inspect_page, resource_issues,
)


class DiscoverabilityTests(unittest.TestCase):
    def result(self, modifier=None, extra="", path="/about"):
        person = {
            "@id": PERSON_ID, "@type": "Person",
            "identifier": {"value": "2018381"}, "sameAs": sorted(REQUIRED_LINKS),
            "worksFor": {"@id": EMPLOYER_ID}, "brand": {"@id": BRAND_ID},
        }
        employer = {"@id": EMPLOYER_ID, "@type": "Organization",
                    "name": "Home 1st Lending, LLC", "identifier": {"value": "1418"}}
        brand = {"@id": BRAND_ID, "@type": "Brand", "name": "DR. Mortgage USA",
                 "owner": {"@id": PERSON_ID}}
        if modifier:
            modifier(person)
        html = (f'<title>Dennis Ross</title><link href="{ORIGIN + path}" rel="canonical">'
                f'<p>Dennis NMLS 2018381; Home 1st NMLS 1418. '
                'VA home loan guidance across Greater Orlando; '
                'not a separate lender or mortgage company and not Dr. Mortgage, LLC.</p>'
                f'<a href="{EXPERIENCE}">Profile</a>'
                '<script type="application/ld+json">'
                + json.dumps({"@graph": [person, employer, brand]}) + '</script>' + extra)
        return dict(url=ORIGIN + path, final_url=ORIGIN + path, status=200,
                    content_type="text/html; charset=utf-8", x_robots="", body=html)

    def test_valid_identity(self):
        self.assertEqual(inspect_page(self.result())["issues"], [])

    def test_removed_profile_fails_even_with_visible_link(self):
        result = self.result(lambda person: person["sameAs"].remove(EXPERIENCE))
        self.assertTrue(any("missing Person identity links" in i
                            for i in inspect_page(result)["issues"]))

    def test_wrong_nmls_association_fails_despite_correct_footer(self):
        result = self.result(lambda person: person.update(identifier={"value": "1418"}))
        self.assertIn("incorrect Dennis NMLS association", inspect_page(result)["issues"])

    def test_malformed_identity_types_fail_without_crashing(self):
        result = self.result(lambda person: person.update(identifier=None, worksFor=[], brand="wrong", sameAs=[{}]))
        issues = inspect_page(result)["issues"]
        self.assertIn("incorrect Dennis NMLS association", issues)
        self.assertIn("incorrect Dennis employer association", issues)

    def test_order_independent_and_agent_specific_robots(self):
        for meta in ('<meta content="none" name="robots">',
                     '<meta content="noindex" name="Googlebot">'):
            self.assertIn("blocking robots directive",
                          inspect_page(self.result(extra=meta))["issues"])

    def test_header_and_malformed_schema_fail(self):
        result = self.result(extra='<script type="application/ld+json">{bad}</script>')
        result["x_robots"] = "googlebot: noindex"
        issues = inspect_page(result)["issues"]
        self.assertIn("blocking robots directive", issues)
        self.assertTrue(any("invalid JSON-LD" in i for i in issues))

    def test_removed_visible_link_and_missing_canonical_fail(self):
        result = self.result()
        result["body"] = result["body"].replace(f'<a href="{EXPERIENCE}">Profile</a>', "")
        self.assertIn("missing visible Experience verification link",
                      inspect_page(result)["issues"])
        result["body"] = result["body"].replace('rel="canonical"', 'rel="alternate"')
        self.assertIn("missing, duplicate, or mismatched canonical",
                      inspect_page(result)["issues"])

    def test_resource_types_are_enforced(self):
        result = self.result()
        self.assertIn("wrong content type", resource_issues(result, "text/plain"))

    def test_policy_tokens_are_not_fetch_agents(self):
        self.assertFalse(set(POLICY_TOKENS) & set(BOT_AGENTS))
        self.assertIn("PerplexityBot", BOT_AGENTS)
        self.assertIn("Amzn-SearchBot", BOT_AGENTS)


if __name__ == "__main__":
    unittest.main()
