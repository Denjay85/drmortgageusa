import json
import os
from pathlib import Path
import re
import unittest
from urllib.parse import urljoin, urlsplit, unquote
import xml.etree.ElementTree as ET

os.environ['ENABLE_RATE_UPDATER'] = '0'
import app as production_app
from site_presentation import Document, OLD_LINKS, article_content, metadata, shared_chrome
from scripts.audit_discoverability import Page
from scripts.generate_service_pages import PAGES

ROOT = Path(production_app.BASE_DIR)


def visible_text(markup):
    page = Page()
    page.feed(markup)
    return ' '.join(' '.join(page.text).split())


def sitemap_paths():
    ns = {'m': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [urlsplit(node.text).path for node in
            ET.parse(ROOT / 'sitemap.xml').findall('.//m:loc', ns)]


class SitePresentationTests(unittest.TestCase):
    def setUp(self):
        self.client = production_app.app.test_client()

    def test_every_sitemap_page_has_exact_shared_header_footer_and_styles(self):
        chrome = shared_chrome(production_app.REDESIGN_OUT_DIR)
        paths = sitemap_paths() + ['/privacy', '/request-received', '/request-review', '/missing-page-for-test']
        for path in paths:
            with self.subTest(path=path), self.client.get(path) as response:
                self.assertEqual(response.status_code, 405 if path == '/request-review' else
                                 404 if path == '/missing-page-for-test' else 200)
                html = response.get_data(as_text=True)
                self.assertIn(chrome['header'], html)
                self.assertIn(chrome['footer'], html)
                self.assertIn(chrome['mobile_actions'], html)
                self.assertIn(chrome['styles'], html)
                self.assertNotIn('cdn.tailwindcss.com', html)
                self.assertNotIn('landing-pages.css', html)
                doc = Document(html)
                self.assertEqual(sum(n.tag == 'h1' for n in doc.elements), 1)
                self.assertEqual(sum(n.tag == 'main' for n in doc.elements), 1)

    def test_all_article_prose_links_tables_and_structured_data_survive(self):
        for file in (ROOT / 'blog_posts').glob('*.html'):
            if file.name == 'index.html':
                continue
            with self.subTest(article=file.stem):
                source = file.read_text(encoding='utf-8')
                old = Document(source)
                body = old.find('article') or old.find('main')
                with self.client.get('/blog/' + file.stem) as response:
                    rendered = response.get_data(as_text=True)
                text = visible_text(rendered)
                for node in old.elements:
                    if body.start <= node.start < body.end and node.tag in ('h1', 'h2', 'h3', 'p', 'li', 'td', 'th'):
                        self.assertIn(visible_text(old.outer(node)), text)
                    if node.tag == 'a' and body.start <= node.start < body.end:
                        href = node.attrs.get('href', '')
                        new = Document(rendered)
                        links = {n.attrs.get('href') for n in new.elements if n.tag == 'a'}
                        self.assertIn(OLD_LINKS.get(href, href), links)
                before, after = Page(), Page()
                before.feed(source)
                after.feed(rendered)
                self.assertEqual(before.canonicals, after.canonicals)
                self.assertEqual([json.loads(x) for x in before.json_blocks],
                                 [json.loads(x) for x in after.json_blocks])
                self.assertEqual(len(re.findall(r'<table\b', source)), len(re.findall(r'<table\b', rendered)))
                self.assertEqual(Document(rendered).find('body').attrs['data-page-intent'], 'education')
                for node in Document(rendered).elements:
                    if node.tag == 'table':
                        self.assertEqual(node.attrs.get('tabindex'), '0')

    def test_new_blog_files_automatically_receive_shared_presentation(self):
        source = (ROOT / 'blog_posts/pay-off-car-before-buying-home-florida.html').read_text()
        with production_app.app.test_request_context('/'):
            response = production_app.shared_public_page(metadata(source), article_content(source), category='blog')
        self.assertIn('class="site-header"', response.get_data(as_text=True))
        self.assertNotIn('cdn.tailwindcss.com', response.get_data(as_text=True))

    def test_service_forms_preserve_submission_and_contact_permission_contract(self):
        for page in PAGES:
            with self.subTest(page=page['slug']), self.client.get('/' + page['slug']) as response:
                doc = Document(response.get_data(as_text=True))
                form = doc.find('form')
                self.assertEqual(form.attrs['method'], 'post')
                self.assertEqual(form.attrs['action'], '/request-review')
                fields = {n.attrs.get('name'): n.attrs for n in doc.elements if n.tag == 'input'}
                self.assertEqual(fields['source']['value'], page['source'])
                self.assertEqual(fields['segment']['value'], page['segment'])
                for name in ('firstName', 'email', 'emailConsent'):
                    self.assertIn('required', fields[name])
                for name in ('emailConsent', 'callConsent', 'smsConsent'):
                    self.assertNotIn('checked', fields[name])
                for name in ('phone', 'callConsent', 'smsConsent'):
                    self.assertNotIn('required', fields[name])
                if page['slug'] != 'va-loans-orlando':
                    self.assertEqual(form.attrs['data-lead-handler'], 'standalone')
                    self.assertEqual(doc.find('body').attrs['data-page-intent'], page['segment'])

    def test_restyled_services_keep_existing_copy_and_search_metadata(self):
        for page in PAGES:
            if page['slug'] == 'va-loans-orlando':
                continue
            with self.subTest(page=page['slug']), self.client.get('/' + page['slug']) as response:
                rendered = response.get_data(as_text=True)
                text = visible_text(rendered)
                expected = [page[key] for key in ('hero_title', 'hero_lead', 'form_heading', 'form_text', 'cta_text')]
                for section in page['sections']:
                    expected += [section['title'], section['body'], *section['items']]
                for key in ('trust_points', 'process_points', 'faqs'):
                    expected += [item for row in page[key] for item in row]
                for value in expected:
                    self.assertIn(' '.join(value.split()), text)
                source = (ROOT / (page['slug'] + '.html')).read_text()
                self.assertEqual(metadata(source), metadata(rendered))

    def test_internal_page_links_and_fragments_resolve(self):
        paths = sitemap_paths() + ['/privacy', '/request-received']
        pages = {}
        links = set()
        for path in paths:
            with self.client.get(path) as response:
                doc = Document(response.get_data(as_text=True))
            pages[path] = doc
            for node in doc.elements:
                if node.tag != 'a' or not node.attrs.get('href'):
                    continue
                url = urlsplit(urljoin('https://drmortgageusa.com' + path, node.attrs['href']))
                if url.netloc == 'drmortgageusa.com' and url.scheme == 'https':
                    links.add((url.path or '/', unquote(url.fragment)))
        for path, fragment in sorted(links):
            with self.subTest(path=path, fragment=fragment):
                if path not in pages:
                    with self.client.get(path, follow_redirects=True) as response:
                        self.assertEqual(response.status_code, 200)
                        pages[path] = Document(response.get_data(as_text=True))
                if fragment and path == '/tools':
                    # These are calculator-mode commands consumed by the existing
                    # hashchange handler, not document anchor elements.
                    studio = (ROOT / 'site/app/tools/MortgageStudio.tsx').read_text()
                    mode_ids = set(re.findall(r'\{ id: "([a-z-]+)", short:', studio))
                    if fragment in mode_ids:
                        self.assertIn('window.addEventListener("hashchange", syncFromHash)', studio)
                        continue
                if fragment:
                    self.assertTrue(any(n.attrs.get('id') == fragment for n in pages[path].elements))

    def test_legacy_aliases_redirect_without_losing_campaign_queries(self):
        pairs = [('/index.html', '/'), ('/simple.html', '/'), ('/dpa.html', '/dpa'),
                 ('/privacy.html', '/privacy'), ('/heloc-calculator.html', '/heloc-calculator'),
                 ('/blog_posts/index.html', '/blog')]
        pairs += [('/' + page['slug'] + '.html', '/' + page['slug']) for page in PAGES]
        pairs += [(prefix + 'va-loan-occupancy-requirements-florida-2026' + suffix,
                   '/blog/va-loan-occupancy-requirements-florida-2026')
                  for prefix, suffix in [('/blog_posts/', '.html'), ('/blog/', '/index.html'), ('/blog/', '/')]]
        for old, canonical in pairs:
            with self.subTest(path=old), self.client.get(old + '?utm_source=test') as response:
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response.headers['Location'], canonical + '?utm_source=test')

    def test_privacy_text_is_unchanged_and_result_pages_remain_untracked(self):
        source = Document((ROOT / 'privacy.html').read_text())
        with self.client.get('/privacy') as response:
            text = visible_text(response.get_data(as_text=True))
        self.assertIn(visible_text(source.inner(source.find('div', 'container'))), text)
        for path in ('/privacy', '/request-received', '/request-review', '/missing-page-for-test', '/blog/missing-page-for-test'):
            with self.subTest(path=path), self.client.get(path) as response:
                html = response.get_data(as_text=True)
                self.assertNotIn('site-tracking.js', html)
                self.assertNotIn('lead-context.js', html)
                if path != '/privacy':
                    self.assertIn('noindex', response.headers['X-Robots-Tag'])
                    self.assertEqual(response.headers['Cache-Control'], 'no-store')


if __name__ == '__main__':
    unittest.main()
