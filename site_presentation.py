"""Present file-backed pages with the actual exported main-site chrome.

Blog publishing can continue adding HTML files without a frontend rebuild.
Only presentation changes here: original metadata, prose and JSON-LD survive.
The shell is read from the current frontend export, not a separately maintained
copy of its navigation. No React hydration is attached to server-rendered pages.
"""
from dataclasses import dataclass
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
from pathlib import Path


VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
OLD_LINKS = {'/#quiz': '/get-started', '/#calculator': '/tools', '/#faq': '/faq'}


@dataclass
class Element:
    tag: str
    attrs: dict
    start: int
    inside: int
    close: int = 0
    end: int = 0

    def has_class(self, name):
        return name in self.attrs.get('class', '').split()


class Document(HTMLParser):
    """Keep source offsets so extracting content does not rewrite prose/entities."""
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        for line in source.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.elements = []
        self.stack = []
        self.feed(source)

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Element(tag, dict(attrs), start, start + len(self.get_starttag_text()))
        self.elements.append(node)
        if tag in VOID:
            node.close = node.end = node.inside
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.close = node.end = node.inside

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                node = self.stack[index]
                node.close = self.position()
                node.end = self.source.index('>', node.close) + 1
                del self.stack[index:]
                break

    def find(self, tag=None, class_name=None):
        return next((node for node in self.elements if node.end and
                     (tag is None or node.tag == tag) and
                     (class_name is None or node.has_class(class_name))), None)

    def outer(self, node):
        return self.source[node.start:node.end]

    def inner(self, node):
        return self.source[node.inside:node.close]


@lru_cache(maxsize=2)
def _chrome(path, modified):
    doc = Document(Path(path).read_text(encoding='utf-8'))
    required = [doc.find(class_name='topline'), doc.find('header', 'site-header'),
                doc.find('footer', 'site-footer'), doc.find(class_name='mobile-actions')]
    if not all(required):
        raise ValueError('Main-site export is missing shared navigation components')
    styles = [doc.outer(node) for node in doc.elements
              if node.tag == 'link' and node.attrs.get('rel') == 'stylesheet']
    if not styles:
        raise ValueError('Main-site stylesheet is missing')
    return dict(header=doc.outer(required[0]) + doc.outer(required[1]),
                footer=doc.outer(required[2]), mobile_actions=doc.outer(required[3]),
                styles='\n'.join(styles))


def shared_chrome(export_dir):
    path = Path(export_dir) / 'index.html'
    return _chrome(str(path), path.stat().st_mtime_ns)


def metadata(source):
    doc = Document(source)
    head = doc.find('head')
    parts = []
    for node in doc.elements:
        if not head or not (head.inside <= node.start < head.close):
            continue
        if node.tag == 'title' or (node.tag == 'meta' and
                'charset' not in node.attrs and node.attrs.get('name') != 'viewport'):
            parts.append(doc.outer(node))
        elif node.tag == 'link' and node.attrs.get('rel') == 'canonical':
            parts.append(doc.outer(node))
        elif node.tag == 'script' and node.attrs.get('type') == 'application/ld+json':
            parts.append(doc.outer(node))
    return '\n'.join(parts)


def presentation_markup(fragment):
    """Map old decorative classes and obsolete local anchors, not article text."""
    doc = Document(fragment)
    replacements = []
    for node in doc.elements:
        attrs = dict(node.attrs)
        classes = attrs.get('class', '').split()
        changed = False
        if node.tag == 'a':
            href = attrs.get('href', '')
            if href in OLD_LINKS:
                attrs['href'] = OLD_LINKS[href]
                changed = True
            if (('bg-gold' in classes or 'bg-[#ffb700]' in classes) and
                    any(x.startswith('py-') for x in classes)) or classes == ['button']:
                attrs['class'] = 'button button-gold'
                changed = True
            elif any(x in classes for x in ('border-gold', 'border-[#ffb700]', 'button-secondary')):
                attrs['class'] = 'button button-outline-light'
                changed = True
        elif node.tag == 'button' and 'button' in classes:
            attrs['class'] = 'button button-gold'
            changed = True
        elif node.tag == 'table':
            attrs.setdefault('tabindex', '0')
            attrs.setdefault('aria-label', 'Comparison table; scroll horizontally for more columns')
            changed = True
        if node.tag in ('div', 'section') and (node.has_class('cta') or
                (any(x in classes for x in ('bg-navy', 'bg-[#001f3f]')) and
                 any(x in classes for x in ('p-8', 'p-6', 'mt-12', 'py-12')))):
            attrs['class'] = 'article-cta'
            changed = True
        if changed:
            rendered = ''.join(' ' + name + ('' if value is None else
                               '="' + escape(value, quote=True) + '"')
                               for name, value in attrs.items())
            replacements.append((node.start, node.inside, '<' + node.tag + rendered + '>'))
    for start, end, replacement in reversed(replacements):
        fragment = fragment[:start] + replacement + fragment[end:]
    return fragment


def article_content(source):
    doc = Document(source)
    article = doc.find('article')
    if article:
        content = doc.inner(article)
        footer = doc.find('footer')
        body = doc.find('body')
        trailing = source[article.end:footer.start if footer else body.close].strip()
        if trailing:
            content += '<div>' + trailing + '</div>'
        if footer:
            content += '<div class="article-disclosure">' + doc.inner(footer) + '</div>'
    else:
        # One older educational article uses header/main/footer instead.
        header, main, footer = doc.find('header'), doc.find('main'), doc.find('footer')
        if not (header and main):
            raise ValueError('Article content is missing')
        content = '<div>' + doc.outer(header) + '<div class="prose">' + doc.inner(main) + '</div>'
        if footer:
            content += '<div class="article-disclosure">' + doc.inner(footer) + '</div>'
        content += '</div>'
    return '<article class="site-article">' + presentation_markup(content) + '</article>'


def privacy_content(source):
    doc = Document(source)
    container = doc.find('div', 'container')
    if container is None:
        raise ValueError('Privacy content is missing')
    return '<article class="site-article site-policy"><div>' + doc.inner(container) + '</div></article>'


def service_form(source):
    doc = Document(source)
    form = doc.find('form')
    if form is None:
        raise ValueError('Service form is missing')
    return presentation_markup(doc.outer(form))
