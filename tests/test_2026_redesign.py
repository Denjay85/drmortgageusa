import os
import json
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path
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
                self.assertNotIn(chr(8212), response.get_data(as_text=True), route)
            response.close()

    def test_public_pages_do_not_publish_the_unrelated_plains_commerce_nmls(self):
        sitemap_response = self.client.get('/sitemap.xml')
        sitemap = sitemap_response.get_data(as_text=True)
        sitemap_response.close()
        routes = [
            re.sub(r'^https://drmortgageusa\.com', '', value) or '/'
            for value in re.findall(r'<loc>(.*?)</loc>', sitemap)
        ]

        for route in routes:
            response = self.client.get(route)
            body = response.get_data(as_text=True)
            self.assertNotIn('463950', body, route)
            response.close()

    def test_live_data_endpoints_feed_the_redesign(self):
        snapshot = {
            'rates': {
                'conv30': '6.71',
                'conv15': '6.18',
                'fha30': '6.30',
                'va30': '6.32',
                'jumbo30': '6.84',
            },
            'as_of': datetime.now(timezone.utc).date().isoformat(),
            'source': 'Mortgage News Daily',
            'source_url': 'https://www.mortgagenewsdaily.com/mortgage-rates',
        }
        production_app._mnd_rate_cache.update(snapshot=None, fetched_at=0.0)
        with patch.object(production_app, 'fetch_mnd_snapshot', return_value=snapshot):
            rates = self.client.get('/api/rates')
        self.assertEqual(rates.status_code, 200)
        rate_payload = rates.get_json()
        self.assertTrue(rate_payload['verified'])
        self.assertEqual(rate_payload['rates']['Conventional 30-year'], '6.71%')
        self.assertNotIn('USDA 30-year', rate_payload['rates'])

        blog = self.client.get('/api/blog')
        self.assertEqual(blog.status_code, 200)
        self.assertGreaterEqual(len(blog.get_json()['posts']), 40)

        with patch.object(production_app.requests, 'get', side_effect=RuntimeError('offline test')):
            dpa = self.client.get('/api/dpa-rates')
        self.assertEqual(dpa.status_code, 200)
        self.assertFalse(dpa.get_json()['live'])
        self.assertEqual(len(dpa.get_json()['snapshot']['groups']), 5)

    def test_rate_api_never_uses_static_numbers_when_mnd_is_unavailable(self):
        production_app._mnd_rate_cache.update(snapshot=None, fetched_at=0.0)
        with patch.object(
            production_app,
            'fetch_mnd_snapshot',
            side_effect=RuntimeError('source unavailable'),
        ):
            response = self.client.get('/api/rates')

        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload['status'], 'unavailable')
        self.assertFalse(payload['verified'])
        self.assertEqual(payload['rates'], {})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

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

    def test_preview_lead_submission_never_reaches_live_integrations(self):
        payload = {
            'firstName': 'Preview Test',
            'email': 'preview@example.com',
            'phone': '8503468514',
            'segment': 'Purchase mortgage plan',
            'source': 'redesign-build-my-plan',
            'eventId': 'preview_lead_123',
            'emailConsent': True,
            'callConsent': False,
            'smsConsent': True,
        }

        with patch.object(production_app, 'PREVIEW_MODE', True), \
             patch.object(production_app, 'get_db_connection') as database, \
             patch.object(production_app.requests, 'post') as external_post:
            response = self.client.post('/api/quiz-submit', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        self.assertTrue(response.get_json()['preview'])
        self.assertEqual(response.get_json()['event_id'], 'preview_lead_123')
        database.assert_not_called()
        external_post.assert_not_called()

    def test_preview_tracking_script_does_not_load_ad_networks(self):
        with patch.object(production_app, 'PREVIEW_MODE', True):
            response = self.client.get('/site-tracking.js')

        script = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('__drPreviewMode', script)
        self.assertNotIn('connect.facebook.net', script)
        self.assertNotIn('googletagmanager.com', script)

    def test_preview_pages_send_a_noindex_header(self):
        with patch.object(production_app, 'PREVIEW_MODE', True):
            response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers['X-Robots-Tag'],
            'noindex, nofollow, noarchive, nosnippet',
        )

    def test_indexnow_key_is_publicly_verifiable(self):
        response = self.client.get(
            '/48a2679b14df424496b53777bbb1e2a4.txt'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True).strip(),
            '48a2679b14df424496b53777bbb1e2a4',
        )
        self.assertTrue(response.content_type.startswith('text/plain'))
        response.close()

    def test_llms_manifest_is_plain_text_and_uses_canonical_identity(self):
        response = self.client.get('/llms.txt')
        manifest = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content_type.startswith('text/plain'))
        self.assertIn('# DR. Mortgage USA', manifest)
        self.assertIn('https://drmortgageusa.com/about', manifest)
        self.assertIn('https://drmortgageusa.com/va-loans-orlando', manifest)
        self.assertIn('NMLS 2018381', manifest)
        self.assertIn('Home 1st Lending, LLC, NMLS 1418', manifest)
        self.assertIn('Greater Orlando', manifest)
        self.assertIn('DR. Mortgage USA is not a separate lender or mortgage company', manifest)
        self.assertIn('does not refer to Dr. Mortgage, LLC', manifest)
        self.assertIn('https://www.google.com/maps?cid=3829412552217676351', manifest)
        self.assertIn(
            'https://www.va.gov/housing-assistance/home-loans/eligibility/',
            manifest,
        )
        response.close()

    def test_blog_articles_link_dennis_to_his_canonical_profile(self):
        blog_directory = Path(production_app.BASE_DIR) / 'blog_posts'
        article_count = 0

        for blog_path in blog_directory.glob('*.html'):
            html = blog_path.read_text(encoding='utf-8')
            for raw_schema in re.findall(
                r'<script\s+type="application/ld\+json">\s*({.*?})\s*</script>',
                html,
                flags=re.DOTALL,
            ):
                schema = json.loads(raw_schema)
                if schema.get('@type') not in ('Article', 'BlogPosting'):
                    continue

                article_count += 1
                self.assertEqual(
                    schema['author']['@id'],
                    'https://drmortgageusa.com/about#dennis-ross',
                    blog_path.name,
                )
                self.assertEqual(
                    schema['author']['identifier']['value'],
                    '2018381',
                    blog_path.name,
                )
                self.assertEqual(
                    schema['publisher']['@id'],
                    'https://drmortgageusa.com/#organization',
                    blog_path.name,
                )
                self.assertEqual(
                    schema['mainEntityOfPage']['@id'],
                    schema['url'],
                    blog_path.name,
                )
                self.assertEqual(
                    schema['image'],
                    ['https://drmortgageusa.com/assets/client-collage.jpg'],
                    blog_path.name,
                )
                self.assertRegex(
                    schema['datePublished'],
                    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$',
                    blog_path.name,
                )
                self.assertRegex(
                    schema['dateModified'],
                    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$',
                    blog_path.name,
                )
                self.assertGreaterEqual(
                    schema['dateModified'][:10],
                    '2026-08-11',
                    blog_path.name,
                )
                self.assertIn(
                    '<meta property="og:image" content="https://drmortgageusa.com/assets/client-collage.jpg">',
                    html,
                    blog_path.name,
                )
                self.assertIn(
                    '<meta name="twitter:image" content="https://drmortgageusa.com/assets/client-collage.jpg">',
                    html,
                    blog_path.name,
                )

        self.assertGreaterEqual(article_count, 58)

    def test_service_pages_share_the_canonical_business_entity(self):
        for route in (
            '/va-loans-orlando',
            '/orlando-mortgage-broker',
            '/first-time-homebuyer-orlando',
            '/refinance-florida',
            '/heloc-orlando',
        ):
            response = self.client.get(route)
            html = response.get_data(as_text=True)
            raw_schema = re.search(
                r'<script\s+type="application/ld\+json">\s*({.*?})\s*</script>',
                html,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(raw_schema, route)
            schema = json.loads(raw_schema.group(1))
            service = next(
                entity for entity in schema['@graph']
                if entity.get('@id', '').endswith('#service')
            )
            self.assertEqual(service['@type'], 'Service', route)
            self.assertIn('description', service, route)
            self.assertNotEqual(service['name'], 'DR. Mortgage USA - Dennis Ross', route)
            self.assertEqual(
                service['provider']['@id'],
                'https://drmortgageusa.com/#organization',
                route,
            )
            self.assertEqual(
                service['provider']['address']['addressLocality'],
                'Lake Mary',
                route,
            )
            self.assertIn(
                'https://www.google.com/maps?cid=3829412552217676351',
                service['provider']['sameAs'],
                route,
            )
            self.assertIn(
                'https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023',
                service['provider']['sameAs'],
                route,
            )
            self.assertIn(
                'https://www.experience.com/reviews/dennis-14873595',
                service['provider']['sameAs'],
                route,
            )
            self.assertIn(
                'https://www.zillow.com/lender-profile/dennis0564/',
                service['provider']['sameAs'],
                route,
            )
            self.assertEqual(
                service['provider']['founder']['@id'],
                'https://drmortgageusa.com/about#dennis-ross',
                route,
            )
            self.assertIn(
                'not a separate lender or mortgage company',
                service['provider']['description'],
                route,
            )
            self.assertIn(
                'does not identify Dr. Mortgage, LLC',
                service['provider']['disambiguatingDescription'],
                route,
            )
            dennis_entities = [
                entity for entity in schema['@graph']
                if entity.get('@id') == 'https://drmortgageusa.com/about#dennis-ross'
            ]
            for dennis in dennis_entities:
                self.assertEqual(
                    dennis['worksFor']['@id'],
                    'https://myhome1st.com/#organization',
                    route,
                )
                self.assertIn('https://myhome1st.com/dennis/', dennis['sameAs'], route)
                self.assertIn(
                    'https://www.google.com/maps?cid=3829412552217676351',
                    dennis['sameAs'],
                    route,
                )
                self.assertIn(
                    'https://www.bing.com/maps?ss=ypid.YN215EB5A5FBD32023',
                    dennis['sameAs'],
                    route,
                )
                self.assertIn(
                    'https://www.experience.com/reviews/dennis-14873595',
                    dennis['sameAs'],
                    route,
                )
                self.assertIn(
                    'https://www.zillow.com/lender-profile/dennis0564/',
                    dennis['sameAs'],
                    route,
                )
            self.assertIn('<a href="/about">About Dennis</a>', html, route)
            self.assertIn(
                'https://www.nmlsconsumeraccess.org/EntityDetails.aspx/INDIVIDUAL/2018381',
                html,
                route,
            )
            self.assertIn('https://myhome1st.com/dennis/', html, route)
            self.assertNotIn('retargeting traffic', html.lower(), route)
            self.assertNotIn('why this page exists', html.lower(), route)

            if route == '/va-loans-orlando':
                served_names = {
                    area['name'] for area in service['areaServed']
                }
                self.assertTrue(
                    {'Orlando', 'Lake Mary', 'Winter Park', 'Sanford',
                     'Altamonte Springs', 'Oviedo'}.issubset(served_names)
                )
                self.assertIn('VA loan guidance across Greater Orlando', html)
                self.assertIn(
                    'https://www.va.gov/housing-assistance/home-loans/eligibility/',
                    html,
                )
                self.assertIn(
                    'https://www.va.gov/housing-assistance/home-loans/loan-types/purchase-loan/',
                    html,
                )
                self.assertIn(
                    '<meta name="twitter:image" content="https://drmortgageusa.com/dennis-ross-headshot.png">',
                    html,
                )
                self.assertIn('Independent client evidence:', html)
                self.assertIn(
                    'specifically recommends Dennis to veterans looking to buy a home',
                    html,
                )
                self.assertIn('Read the public Google reviews.', html)
                self.assertNotIn('"@type": "Review"', html)
                self.assertNotIn('"aggregateRating"', html)
            response.close()

    def test_sitemap_lastmod_covers_the_current_authority_release(self):
        response = self.client.get('/sitemap.xml')
        sitemap = response.get_data(as_text=True)
        lastmod_values = re.findall(r'<lastmod>(.*?)</lastmod>', sitemap)

        self.assertEqual(len(lastmod_values), 77)
        self.assertTrue(all(value >= '2026-08-11' for value in lastmod_values))
        response.close()

    def test_sitemap_generator_uses_article_modified_date(self):
        from update_blog import build_sitemap

        sitemap = build_sitemap([
            {
                'url': 'https://drmortgageusa.com/blog/example',
                'lastmod': '2026-08-11',
            },
        ])
        article_block = re.search(
            r'<url>\s*<loc>https://drmortgageusa.com/blog/example</loc>'
            r'\s*<lastmod>(.*?)</lastmod>',
            sitemap,
        )
        self.assertIsNotNone(article_block)
        self.assertEqual(article_block.group(1), '2026-08-11')

    def test_missing_zapier_configuration_queues_the_lead(self):
        connection = FakeConnection()
        payload = {
            'firstName': 'Queue Test',
            'email': 'queue@example.com',
            'phone': '8503468514',
            'segment': 'Purchase mortgage plan',
            'source': 'redesign-build-my-plan',
            'eventId': 'queued_lead_123',
            'emailConsent': True,
            'callConsent': False,
            'smsConsent': False,
        }

        with patch.object(production_app, 'get_db_connection', return_value=connection), \
             patch.object(production_app, 'ZAPIER_WEBHOOK_URL', ''), \
             patch.object(production_app, 'track_meta_server_event', return_value={'sent': False}):
            response = self.client.post('/api/quiz-submit', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        update_params = connection.cursor_instance.executions[1][1]
        self.assertFalse(update_params[0])
        self.assertEqual(update_params[2], 'not_configured')

    def test_zapier_delivery_helper_does_not_send_without_configuration(self):
        with patch.object(production_app, 'ZAPIER_WEBHOOK_URL', ''), \
             patch.object(production_app.requests, 'post') as external_post:
            result = production_app.forward_to_zapier({'eventId': 'queue_test'})

        self.assertFalse(result['sent'])
        self.assertEqual(result['reason'], 'not_configured')
        external_post.assert_not_called()

    def test_integration_status_is_admin_only_and_redacts_secrets(self):
        unauthenticated = self.client.get('/admin/integrations')
        self.assertEqual(unauthenticated.status_code, 302)

        connection = FakeConnection()
        with self.client.session_transaction() as session:
            session['admin_logged_in'] = True

        with patch.object(production_app, 'get_db_connection', return_value=connection), \
             patch.object(production_app, 'ZAPIER_WEBHOOK_URL', ''), \
             patch.object(production_app, 'META_ACCESS_TOKEN', 'configured'):
            authenticated = self.client.get('/admin/integrations')

        self.assertEqual(authenticated.status_code, 200)
        status = authenticated.get_json()
        self.assertFalse(status['zapier_bonzo'])
        self.assertTrue(status['meta_capi'])
        self.assertEqual(status['queued_leads'], 101)
        self.assertNotIn('configured', authenticated.get_data(as_text=True))

    def test_admin_dashboard_renders_integration_readiness_panel(self):
        with production_app.app.test_request_context('/admin/dashboard'):
            dashboard = production_app.render_template_string(
                production_app.ADMIN_DASHBOARD_TEMPLATE,
                leads=[],
                total_leads=4,
                queued_leads=2,
                integration_status={
                    'zapier_bonzo': False,
                    'meta_pixel': True,
                    'meta_capi': True,
                    'google_ads': True,
                    'manychat': False,
                },
                delivery_result='',
                segment_counts={},
                current_segment='',
                search_query='',
            )

        self.assertIn('DR. Mortgage USA', dashboard)
        self.assertIn('Integration readiness', dashboard)
        self.assertIn('Leads waiting for Bonzo', dashboard)
        self.assertIn('Waiting for credentials', dashboard)

    def test_production_tracking_script_contains_configured_ad_destinations(self):
        environment = {
            'GOOGLE_ADS_ID': 'AW-123456789',
            'GOOGLE_ADS_APPLY_CONVERSION_LABEL': 'apply-label',
            'GOOGLE_ADS_PHONE_CONVERSION_LABEL': 'phone-label',
            'GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL': 'lead-label',
            'GA_MEASUREMENT_ID': 'G-TEST123',
        }
        with patch.object(production_app, 'PREVIEW_MODE', False), \
             patch.object(production_app, 'META_PIXEL_ID', '987654321'), \
             patch.dict(production_app.os.environ, environment, clear=False):
            response = self.client.get('/site-tracking.js')

        script = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('connect.facebook.net', script)
        self.assertIn('987654321', script)
        self.assertIn('AW-123456789', script)
        self.assertIn('apply-label', script)
        self.assertIn('phone-label', script)
        self.assertIn('lead-label', script)
        self.assertIn('G-TEST123', script)

    def test_meta_capi_uses_matching_event_id_and_hashed_contact_data(self):
        graph_response = Mock(ok=True, status_code=200, text='ok')
        with production_app.app.test_request_context(
            '/api/quiz-submit',
            headers={'User-Agent': 'Migration QA'},
        ), patch.object(production_app, 'META_PIXEL_ID', '987654321'), \
             patch.object(production_app, 'META_ACCESS_TOKEN', 'private-token'), \
             patch.object(production_app, 'META_TEST_EVENT_CODE', 'TEST123'), \
             patch.object(production_app.requests, 'post', return_value=graph_response) as graph_post:
            result = production_app.track_meta_server_event(
                'Lead',
                'matching_event_123',
                {
                    'firstName': 'Dennis',
                    'email': 'dennis@example.com',
                    'phone': '8503468514',
                },
                custom_data={'content_name': 'migration_test'},
            )

        self.assertTrue(result['sent'])
        call = graph_post.call_args
        self.assertIn('/987654321/events', call.args[0])
        self.assertEqual(call.kwargs['params']['access_token'], 'private-token')
        event = call.kwargs['json']['data'][0]
        self.assertEqual(event['event_id'], 'matching_event_123')
        self.assertEqual(call.kwargs['json']['test_event_code'], 'TEST123')
        self.assertEqual(
            event['user_data']['em'][0],
            production_app.sha256_or_none('dennis@example.com'),
        )


if __name__ == '__main__':
    unittest.main()
