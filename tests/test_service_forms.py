import os
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

os.environ['ENABLE_RATE_UPDATER'] = '0'

import app as production_app
from scripts.generate_service_pages import PAGES, render_page


class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class ServiceFormTests(unittest.TestCase):
    def setUp(self):
        self.client = production_app.app.test_client()
        self.payload = {
            'firstName': 'Local Test', 'email': 'local@example.test',
            'source': 'service-page-va-loans-orlando', 'segment': 'veteran',
            'emailConsent': 'on',
        }

    def test_generated_pages_have_accessible_independent_post_forms(self):
        for page in PAGES:
            with self.subTest(page=page['slug']):
                path = Path(production_app.BASE_DIR) / (page['slug'] + '.html')
                html = path.read_text(encoding='utf-8')
                self.assertEqual(html, render_page(page))
                tags = Elements(html).tags
                forms = [attrs for tag, attrs in tags if tag == 'form']
                self.assertEqual(len(forms), 1)
                self.assertEqual(forms[0]['method'], 'post')
                self.assertEqual(forms[0]['action'], '/request-review')
                self.assertEqual(forms[0]['data-lead-handler'], 'standalone')
                self.assertGreaterEqual(sum(tag == 'label' for tag, _ in tags), 7)
                checkboxes = {attrs['name']: attrs for tag, attrs in tags
                              if tag == 'input' and attrs.get('type') == 'checkbox'}
                self.assertIn('required', checkboxes['emailConsent'])
                for name in ('callConsent', 'smsConsent'):
                    self.assertNotIn('required', checkboxes[name])
                    self.assertNotIn('checked', checkboxes[name])
                self.assertIn('/assets/lead-forms.js?v=20261008-1', html)
                self.assertIn('href="#request-review"', html)
                self.assertIn('href="/privacy"', html)
                self.assertNotIn('href="#request-review" data-track="apply"', html)

    def test_native_post_redirect_has_no_contact_details_and_no_external_calls_in_preview(self):
        with patch.object(production_app, 'PREVIEW_MODE', True), \
             patch.object(production_app, 'get_db_connection') as database, \
             patch.object(production_app, 'forward_to_zapier') as zapier, \
             patch.object(production_app, 'track_meta_server_event') as meta:
            response = self.client.post('/request-review', data=self.payload)
            self.assertEqual(response.status_code, 303)
            self.assertEqual(response.headers['Location'], '/request-received?preview=1')
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            page = self.client.get(response.headers['Location'])
            self.assertIn('No lead was saved or sent', page.get_data(as_text=True))
            self.assertNotIn('local@example.test', page.get_data(as_text=True))
            database.assert_not_called()
            zapier.assert_not_called()
            meta.assert_not_called()

    def test_service_requests_require_email_permission_on_both_paths(self):
        for endpoint in ('/api/quiz-submit', '/request-review'):
            for fields in ({'emailConsent': ''}, {'firstName': ''},
                           {'email': ''}, {'phone': '', 'smsConsent': 'on'}):
                with self.subTest(endpoint=endpoint, fields=fields), \
                     patch.object(production_app, 'get_db_connection') as database:
                    payload = {**self.payload, **fields}
                    response = self.client.post(endpoint, data=payload)
                    self.assertEqual(response.status_code, 400)
                    database.assert_not_called()

    def test_native_post_only_confirms_a_successful_saved_lead(self):
        with patch.object(production_app, 'quiz_submit', return_value=(
                {'success': True, 'lead_id': 123}, 200)):
            response = self.client.post('/request-review', data=self.payload)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/request-received')

        for result in ({'success': False}, {'success': True, 'lead_id': None}):
            with patch.object(production_app, 'quiz_submit', return_value=(result, 200)):
                response = self.client.post('/request-review', data=self.payload)
            self.assertEqual(response.status_code, 503)
            self.assertIn('could not confirm delivery', response.get_data(as_text=True))

    def test_errors_do_not_expose_backend_details_or_contact_data(self):
        with patch.object(production_app, 'quiz_submit', return_value=(
                {'success': False, 'error': 'private database password'}, 500)):
            response = self.client.post('/request-review', data=self.payload)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private database', response.get_data(as_text=True))
        self.assertNotIn(self.payload['email'], response.get_data(as_text=True))
        self.assertIn('noindex', response.headers['X-Robots-Tag'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_unknown_source_cannot_become_a_redirect_or_submit(self):
        with patch.object(production_app, 'quiz_submit') as submit:
            response = self.client.post('/request-review', data={
                **self.payload, 'source': 'https://example.test/redirect',
            })
        self.assertEqual(response.status_code, 400)
        self.assertNotIn('example.test/redirect', response.get_data(as_text=True))
        submit.assert_not_called()

    def test_confirmation_and_method_errors_are_not_indexable_or_cached(self):
        for path, status in (('/request-review', 405), ('/request-received', 200)):
            response = self.client.get(path)
            self.assertEqual(response.status_code, status)
            self.assertIn('noindex', response.headers['X-Robots-Tag'])
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertNotIn('site-tracking.js', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
