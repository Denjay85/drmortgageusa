import os
import unittest
from unittest.mock import patch

os.environ['ENABLE_RATE_UPDATER'] = '0'

import app as production_app


class LeadEndpointTests(unittest.TestCase):
    def setUp(self):
        production_app.app.config.update(TESTING=True)
        self.client = production_app.app.test_client()

    def test_get_and_head_never_fall_back_to_the_homepage(self):
        with patch.object(production_app, 'get_db_connection') as database, \
             patch.object(production_app, 'forward_to_zapier') as zapier, \
             patch.object(production_app, 'track_meta_server_event') as meta:
            for method in ('GET', 'HEAD'):
                with self.subTest(method=method):
                    response = self.client.open('/api/quiz-submit', method=method)
                    self.assertEqual(response.status_code, 405)
                    self.assertEqual(response.mimetype, 'application/json')
                    self.assertEqual(response.headers['Allow'], 'POST, OPTIONS')
                    self.assertEqual(response.headers['X-Robots-Tag'], 'noindex, nofollow')
                    self.assertEqual(response.headers['Cache-Control'], 'no-store')
                    if method == 'GET':
                        self.assertFalse(response.get_json()['success'])
                    else:
                        self.assertEqual(response.data, b'')
            database.assert_not_called()
            zapier.assert_not_called()
            meta.assert_not_called()

    def test_query_parameters_are_not_reflected_in_the_response(self):
        response = self.client.get('/api/quiz-submit?email=private%40example.test')
        self.assertEqual(response.status_code, 405)
        self.assertNotIn('private', response.get_data(as_text=True))

    def test_post_preview_still_accepts_json_and_html_form_bodies(self):
        payload = {'firstName': 'Local test', 'email': 'local@example.test'}
        with patch.object(production_app, 'PREVIEW_MODE', True), \
             patch.object(production_app, 'get_db_connection') as database, \
             patch.object(production_app, 'forward_to_zapier') as zapier, \
             patch.object(production_app, 'track_meta_server_event') as meta:
            for body in ({'json': payload}, {'data': payload}):
                response = self.client.post('/api/quiz-submit', **body)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.get_json()['success'])
                self.assertTrue(response.get_json()['preview'])
            database.assert_not_called()
            zapier.assert_not_called()
            meta.assert_not_called()

    def test_invalid_post_still_returns_validation_errors(self):
        with patch.object(production_app, 'get_db_connection') as database:
            response = self.client.post('/api/quiz-submit', json={})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()['success'])
        database.assert_not_called()


if __name__ == '__main__':
    unittest.main()
