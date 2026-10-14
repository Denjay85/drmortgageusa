import unittest
from unittest.mock import Mock, patch

import requests
from flask import Flask
import ask_mortgage


class AskMortgageBridgeTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(ask_mortgage.blueprint)
        self.client = self.app.test_client()
        self.upstream = Mock(status_code=200, ok=True,
                             headers={'Content-Type': 'application/json'})
        self.upstream.json.return_value = {'answer': 'Fixture answer, not real mortgage guidance.'}
        self.upstream.cookies = requests.cookies.RequestsCookieJar()
        self.bridge = patch.object(ask_mortgage.requests, 'request', return_value=self.upstream)
        self.send = self.bridge.start()
        self.addCleanup(self.bridge.stop)

    def post(self, endpoint='ask', payload=None, origin='https://drmortgageusa.com'):
        return self.client.post('/api/ask-dr-mortgage/' + endpoint,
                                json=payload if payload is not None else {'question': 'Synthetic QA question'},
                                headers={'Origin': origin})

    def test_question_uses_fixed_public_engine(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        args, kwargs = self.send.call_args
        self.assertEqual(args, ('POST', ask_mortgage.ENGINE_ORIGIN + '/api/ask'))
        self.assertEqual(kwargs['json']['question'], 'Synthetic QA question')
        self.assertEqual(kwargs['timeout'], (5, 20))
        self.assertFalse(kwargs['allow_redirects'])
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(response.headers['X-Robots-Tag'], 'noindex, nofollow')

    def test_only_tool_cookie_is_forwarded(self):
        for name in ['session', 'admin', '__cf_bm', 'dm_conversation']:
            self.client.set_cookie(name, 'test-token', domain='localhost')
        self.client.post('/api/ask-dr-mortgage/ask', json={'question': 'Synthetic'},
                         headers={'Origin': 'https://drmortgageusa.com',
                                  'Authorization': 'Bearer never-forward-this',
                                  'X-Forwarded-For': '192.0.2.1'})
        kwargs = self.send.call_args.kwargs
        self.assertEqual(kwargs['cookies'], {'dm_conversation': 'test-token'})
        self.assertNotIn('Authorization', kwargs['headers'])
        self.assertNotIn('X-Forwarded-For', kwargs['headers'])

    def test_invalid_cookie_is_not_forwarded(self):
        self.client.set_cookie('dm_conversation', 'invalid; injected', domain='localhost')
        self.post()
        self.assertEqual(self.send.call_args.kwargs['cookies'], {})

    def test_set_cookie_is_scoped_secure_and_httponly(self):
        self.upstream.cookies.set('dm_conversation', 'synthetic-token')
        self.upstream.cookies.set('__cf_bm', 'must-not-expose')
        response = self.post('conversation')
        header = response.headers.get('Set-Cookie', '')
        self.assertIn('dm_conversation=synthetic-token', header)
        for required in ['Path=/api/ask-dr-mortgage', 'Secure', 'HttpOnly', 'SameSite=Lax', 'Max-Age=604800']:
            self.assertIn(required, header)
        self.assertNotIn('__cf_bm', header)
        self.assertNotIn('Domain=', header)

    def test_delete_clears_only_tool_cookie(self):
        response = self.client.delete('/api/ask-dr-mortgage/conversation',
                                      headers={'Origin': 'https://drmortgageusa.com'})
        self.assertEqual(response.status_code, 200)
        header = response.headers['Set-Cookie']
        self.assertIn('dm_conversation=', header)
        self.assertIn('Max-Age=0', header)
        self.assertIn('Path=/api/ask-dr-mortgage', header)
        self.assertNotIn('session=', header)

    def test_owner_and_arbitrary_proxy_endpoints_are_not_exposed(self):
        for endpoint in ['research', 'review', 'sync', 'admin', 'https:evil.example']:
            self.assertEqual(self.client.get('/api/ask-dr-mortgage/' + endpoint).status_code, 404)
        self.send.assert_not_called()

    def test_unsupported_methods_are_rejected(self):
        self.assertEqual(self.client.get('/api/ask-dr-mortgage/ask').status_code, 405)
        self.assertEqual(self.post('library').status_code, 405)
        self.send.assert_not_called()

    def test_cross_origin_and_missing_origin_writes_are_rejected(self):
        for origin in ['https://evil.example', '', 'null', 'https://drmortgageusa.com.evil.example']:
            self.assertEqual(self.post(origin=origin).status_code, 403)
        self.send.assert_not_called()

    def test_both_public_site_origins_work(self):
        self.assertEqual(self.post(origin='https://www.drmortgageusa.com').status_code, 200)

    def test_production_does_not_accept_local_or_arbitrary_host_origins(self):
        self.app.config['TESTING'] = False
        for origin in ['http://localhost', 'http://127.0.0.1', 'https://refi.watch']:
            self.assertEqual(self.post(origin=origin).status_code, 403)
        self.send.assert_not_called()

    def test_bad_payloads_are_rejected(self):
        for payload in [{'question': ''}, {'question': 4}, {'question': 'x' * 1201}, {'question': 'qa', 'history': [{}] * 6}, []]:
            self.assertEqual(self.post(payload=payload).status_code, 400)
        self.send.assert_not_called()

    def test_large_payload_is_rejected(self):
        self.assertEqual(self.post(payload={'question': 'qa', 'junk': 'x' * 66000}).status_code, 413)
        self.send.assert_not_called()

    def test_query_string_is_allowlisted(self):
        self.client.get('/api/ask-dr-mortgage/search?q=VA&url=https://evil.example&token=do-not-forward')
        self.assertEqual(self.send.call_args.kwargs['params'], {'q': 'VA'})
        self.client.get('/api/ask-dr-mortgage/library?url=https://evil.example')
        self.assertIsNone(self.send.call_args.kwargs['params'])

    def test_long_search_is_rejected(self):
        self.assertEqual(self.client.get('/api/ask-dr-mortgage/search', query_string={'q': 'x' * 1201}).status_code, 400)
        self.send.assert_not_called()

    def test_upstream_redirect_and_html_never_reach_visitor(self):
        self.upstream.status_code = 302
        self.assertEqual(self.post().status_code, 502)
        self.upstream.status_code = 200
        self.upstream.headers['Content-Type'] = 'text/html'
        self.assertEqual(self.post().status_code, 502)

    def test_timeout_is_safe_without_private_echo(self):
        self.send.side_effect = requests.Timeout('secret-token question and private upstream URL')
        response = self.post()
        self.assertEqual(response.status_code, 502)
        self.assertNotIn('secret-token', response.get_data(as_text=True))
        self.assertIn('temporarily unavailable', response.get_json()['error'])

    def test_json_error_is_forwarded_without_backend_failure(self):
        self.upstream.status_code = 429
        self.upstream.json.return_value = {'error': 'Please slow down.'}
        response = self.post()
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.get_json()['error'], 'Please slow down.')

    def test_parse_error_is_safe(self):
        self.upstream.json.side_effect = ValueError('invalid response')
        self.assertEqual(self.post().status_code, 502)


if __name__ == '__main__':
    unittest.main()
