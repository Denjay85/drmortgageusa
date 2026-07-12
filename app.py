#!/usr/bin/env python3
"""
Dr.MortgageUSA Backend API
- Serves static files
- Handles quiz submissions (stores in DB + forwards to Zapier)
- Admin dashboard for viewing leads
"""

import os
import json
import secrets
import hashlib
import re
import html as html_lib
import requests
import psycopg2
from datetime import datetime, timezone
from urllib.parse import quote
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, send_file, session, redirect, url_for, render_template_string, Response
from flask_compress import Compress
import mimetypes

app = Flask(__name__, static_folder=None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REDESIGN_OUT_DIR = os.path.join(BASE_DIR, 'site', 'dist', 'client')
SERVICE_PAGE_MAP = {
    'va-loans-orlando': 'va-loans-orlando.html',
    'orlando-mortgage-broker': 'orlando-mortgage-broker.html',
    'first-time-homebuyer-orlando': 'first-time-homebuyer-orlando.html',
    'refinance-florida': 'refinance-florida.html',
    'heloc-orlando': 'heloc-orlando.html',
}

# Enable gzip compression for all responses
Compress(app)
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'application/javascript', 'application/json']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

ZAPIER_WEBHOOK_URL = os.environ.get('ZAPIER_WEBHOOK_URL', '').strip()
META_PIXEL_ID = os.environ.get('META_PIXEL_ID', '444762220810129')
META_ACCESS_TOKEN = os.environ.get('META_CONVERSIONS_API_TOKEN', '')
META_TEST_EVENT_CODE = os.environ.get('META_TEST_EVENT_CODE', '')
REFIWATCH_HOSTS = {
    host.strip().lower()
    for host in os.environ.get('REFIWATCH_HOSTS',
                               'refi.watch,www.refi.watch').split(',')
    if host.strip()
}
REFIWATCH_FUNNEL_DIR = os.path.join(BASE_DIR, 'funnels', 'refiwatch')
REFIWATCH_BUILD_DIR = os.path.join(REFIWATCH_FUNNEL_DIR, 'dist', 'public')


def current_host():
    forwarded_host = (
        request.headers.get('X-Forwarded-Host', '')
        or request.headers.get('X-Original-Host', '')
    )
    raw_host = forwarded_host.split(',')[0].strip() if forwarded_host else request.host
    return raw_host.split(':')[0].lower()


def is_refiwatch_request():
    return current_host() in REFIWATCH_HOSTS


def refiwatch_build_ready():
    return os.path.isfile(os.path.join(REFIWATCH_BUILD_DIR, 'index.html'))


def send_refiwatch_index():
    return send_file(os.path.join(REFIWATCH_BUILD_DIR, 'index.html'),
                     mimetype='text/html')


def send_refiwatch_asset(path):
    if not refiwatch_build_ready():
        return None

    for base_dir in (REFIWATCH_BUILD_DIR, REFIWATCH_FUNNEL_DIR):
        abs_base = os.path.abspath(base_dir)
        abs_path = os.path.abspath(os.path.join(base_dir, path))

        if not abs_path.startswith(abs_base + os.sep):
            continue

        if os.path.isfile(abs_path):
            mimetype, _ = mimetypes.guess_type(abs_path)
            return send_file(abs_path,
                             mimetype=mimetype
                             or 'application/octet-stream',
                             conditional=True)

    return None


def send_redesign_page(path=''):
    """Serve a statically exported redesign page when the build is present."""
    cleaned = (path or '').strip('/')
    if not cleaned:
        candidates = [os.path.join(REDESIGN_OUT_DIR, 'index.html')]
    else:
        candidates = [
            os.path.join(REDESIGN_OUT_DIR, cleaned, 'index.html'),
            os.path.join(REDESIGN_OUT_DIR, f'{cleaned}.html'),
            os.path.join(REDESIGN_OUT_DIR, cleaned),
        ]

    redesign_root = os.path.abspath(REDESIGN_OUT_DIR)
    for candidate in candidates:
        absolute = os.path.abspath(candidate)
        if not absolute.startswith(redesign_root + os.sep):
            continue
        if os.path.isfile(absolute):
            mimetype, _ = mimetypes.guess_type(absolute)
            return send_file(
                absolute,
                mimetype=mimetype or 'text/html',
                conditional=True,
            )
    return None


def normalize_email(value):
    return (value or '').strip().lower()


def normalize_phone(value):
    return ''.join(ch for ch in (value or '') if ch.isdigit())


def is_valid_email(value):
    email = normalize_email(value)
    if not email:
        return False
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value or '').strip().lower() in ('1', 'true', 'yes', 'on')


def sha256_or_none(value):
    cleaned = (value or '').strip()
    if not cleaned:
        return None
    return hashlib.sha256(cleaned.encode('utf-8')).hexdigest()


def get_cookie_value(name):
    return request.cookies.get(name, '') or ''


def build_fbc():
    existing_fbc = get_cookie_value('_fbc')
    if existing_fbc:
        return existing_fbc
    fbclid = request.args.get('fbclid', '') or request.headers.get('X-FB-CLID', '')
    if not fbclid:
        return ''
    return f"fb.1.{int(datetime.now(timezone.utc).timestamp())}.{fbclid}"


def track_meta_server_event(event_name, event_id, data, custom_data=None):
    if not META_ACCESS_TOKEN or not META_PIXEL_ID:
        return {'sent': False, 'reason': 'missing_meta_config'}

    email = normalize_email(data.get('email', ''))
    phone = normalize_phone(data.get('phone', ''))
    first_name = (data.get('firstName') or data.get('first_name') or '').strip().lower()

    user_data = {
        'client_ip_address': request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip(),
        'client_user_agent': request.headers.get('User-Agent', ''),
        'fbp': get_cookie_value('_fbp'),
        'fbc': build_fbc(),
    }

    if email:
        user_data['em'] = [sha256_or_none(email)]
    if phone:
        user_data['ph'] = [sha256_or_none(phone)]
    if first_name:
        user_data['fn'] = [sha256_or_none(first_name)]

    user_data = {k: v for k, v in user_data.items() if v}

    payload = {
        'data': [{
            'event_name': event_name,
            'event_time': int(datetime.now(timezone.utc).timestamp()),
            'event_id': event_id,
            'action_source': 'website',
            'event_source_url': request.url,
            'user_data': user_data,
            'custom_data': custom_data or {}
        }]
    }

    if META_TEST_EVENT_CODE:
        payload['test_event_code'] = META_TEST_EVENT_CODE

    response = requests.post(
        f'https://graph.facebook.com/v19.0/{quote(META_PIXEL_ID)}/events',
        params={'access_token': META_ACCESS_TOKEN},
        json=payload,
        timeout=10,
    )
    return {
        'sent': response.ok,
        'status_code': response.status_code,
        'body': response.text[:500],
    }


def get_admin_password():
    """Get admin password from environment - required for security"""
    password = os.environ.get('ADMIN_PASSWORD')
    if not password:
        raise RuntimeError("ADMIN_PASSWORD environment variable must be set")
    return password


def get_db_connection():
    """Get database connection using environment variables"""
    return psycopg2.connect(os.environ['DATABASE_URL'])


def init_database():
    """Create primary app tables if they don't exist."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                segment VARCHAR(50),
                price_range VARCHAR(100),
                down_payment VARCHAR(100),
                timeline VARCHAR(100),
                credit_score VARCHAR(50),
                military_status VARCHAR(50),
                property_type VARCHAR(100),
                investor_loan_type VARCHAR(100),
                zapier_forwarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS source VARCHAR(150)")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS event_id VARCHAR(150)")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_consent BOOLEAN DEFAULT FALSE")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS call_consent BOOLEAN DEFAULT FALSE")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS sms_consent BOOLEAN DEFAULT FALSE")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS payload JSONB DEFAULT '{}'::jsonb")
        cur.execute("ALTER TABLE leads ADD COLUMN IF NOT EXISTS meta_capi_sent BOOLEAN DEFAULT FALSE")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS keyword_leads (
                id SERIAL PRIMARY KEY,
                subscriber_id VARCHAR(100) NOT NULL,
                subscriber_name VARCHAR(200),
                keyword VARCHAR(50),
                ig_username VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                UNIQUE(subscriber_id, keyword)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS refiwatch_leads (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                year_bought INTEGER,
                savings_goal NUMERIC(10, 2),
                current_rate VARCHAR(50) NOT NULL,
                consent BOOLEAN NOT NULL DEFAULT FALSE,
                source VARCHAR(100) DEFAULT 'refiwatch',
                utm_data JSONB,
                zapier_forwarded BOOLEAN DEFAULT FALSE,
                meta_capi_sent BOOLEAN DEFAULT FALSE,
                meta_event_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


def login_required(f):
    """Decorator to require admin login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'service': 'drmortgageusa'}), 200


DPA_PROGRAM_INTRO_RE = re.compile(
    r'(<h2[^>]*>All Florida DPA Programs</h2>\s*)'
    r'<p class="text-gray-400 text-center mb-12 max-w-2xl mx-auto" '
    r'data-aos="fade-up" data-aos-delay="100">.*?</p>',
    re.DOTALL,
)
DPA_PROGRAM_DATE_RE = re.compile(
    r'(?:Rates current as of|Program details and sample rate ranges shown as of) '
    r'([A-Za-z]+ \d{1,2}, \d{4})'
)
DPA_PROGRAM_INTRO_CLASS = (
    'class="text-gray-400 text-center mb-12 max-w-2xl mx-auto" '
    'data-aos="fade-up" data-aos-delay="100"'
)


def normalize_dpa_program_intro(html):
    """Keep the DPA source attribution idempotent after rate bot rewrites."""
    date_match = DPA_PROGRAM_DATE_RE.search(html)
    reviewed_date = date_match.group(1) if date_match else 'May 01, 2026'
    intro_copy = (
        'Compare Florida DPA options side by side. Program details and sample '
        f'rate ranges shown as of {reviewed_date}; availability, income '
        'limits, and pricing can change. Source: eHousingPlus and Florida '
        'Housing Finance Corporation program highlights.'
    )
    replacement = rf'\1<p {DPA_PROGRAM_INTRO_CLASS}>{intro_copy}</p>'
    return DPA_PROGRAM_INTRO_RE.sub(replacement, html, count=1)


@app.route('/')
def serve_index():
    if is_refiwatch_request() and refiwatch_build_ready():
        return send_refiwatch_index()
    redesign = send_redesign_page()
    if redesign is not None:
        return redesign
    return send_file(os.path.join(BASE_DIR, 'index.html'),
                     mimetype='text/html')


@app.route('/site-tracking.js')
def site_tracking():
    ga_measurement_id = os.environ.get('GA_MEASUREMENT_ID', '').strip()
    gtm_container_id = os.environ.get('GTM_CONTAINER_ID', '').strip()
    # Render Blueprint env vars do not backfill existing services reliably.
    # These browser-side Google Ads identifiers are public, so keep live
    # tracking resilient if the service env is currently unset.
    google_ads_id = os.environ.get('GOOGLE_ADS_ID', 'AW-18055212874').strip()
    google_ads_apply_label = os.environ.get(
        'GOOGLE_ADS_APPLY_CONVERSION_LABEL',
        'ZoE7CPuPg6kcEMresqFD',
    ).strip()
    google_ads_phone_label = os.environ.get(
        'GOOGLE_ADS_PHONE_CONVERSION_LABEL',
        'pIxfCP6Pg6kcEMresqFD',
    ).strip()
    google_ads_lead_form_label = os.environ.get(
        'GOOGLE_ADS_LEAD_FORM_CONVERSION_LABEL',
        '90H9CJrk-agcEMresqFD',
    ).strip()
    js = f"""
(function() {{
  if (window.__drSiteTrackingLoaded) return;
  window.__drSiteTrackingLoaded = true;

  var pixelId = {json.dumps(META_PIXEL_ID)};
  var gaMeasurementId = {json.dumps(ga_measurement_id)};
  var gtmContainerId = {json.dumps(gtm_container_id)};
  var googleAdsId = {json.dumps(google_ads_id)};
  var googleAdsApplyLabel = {json.dumps(google_ads_apply_label)};
  var googleAdsPhoneLabel = {json.dumps(google_ads_phone_label)};
  var googleAdsLeadFormLabel = {json.dumps(google_ads_lead_form_label)};
  var options = window.DR_TRACKING_OPTIONS || {{}};
  var googleTagLoaded = false;

  function loadScript(src, onload) {{
    var script = document.createElement('script');
    script.async = true;
    script.src = src;
    if (onload) script.onload = onload;
    document.head.appendChild(script);
  }}

  function getCookie(name) {{
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    return parts.length === 2 ? parts.pop().split(';').shift() : '';
  }}

  function setCookie(name, value, days) {{
    var expires = new Date(Date.now() + (days * 86400000)).toUTCString();
    document.cookie = name + "=" + value + "; expires=" + expires + "; path=/; SameSite=Lax";
  }}

  function getOrCreateFbp() {{
    var fbp = getCookie('_fbp');
    if (!fbp) {{
      fbp = "fb.1." + Date.now() + "." + Math.floor(Math.random() * 1000000000);
      setCookie('_fbp', fbp, 90);
    }}
    return fbp;
  }}

  function getOrCreateFbc() {{
    var fbc = getCookie('_fbc');
    var params = new URLSearchParams(window.location.search);
    var fbclid = params.get('fbclid');
    if (fbclid) {{
      fbc = "fb.1." + Date.now() + "." + fbclid;
      setCookie('_fbc', fbc, 90);
    }}
    return fbc || '';
  }}

  function createEventId(prefix) {{
    return prefix + "_" + Date.now() + "_" + Math.random().toString(36).slice(2, 10);
  }}

  function pushDataLayerEvent(eventName, payload) {{
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({{ event: eventName }}, payload || {{}}));
  }}

  function ensureGoogleTag() {{
    if (window.gtag) return true;
    if (!gaMeasurementId && !googleAdsId) return false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function() {{ window.dataLayer.push(arguments); }};
    window.gtag('js', new Date());
    if (!googleTagLoaded) {{
      googleTagLoaded = true;
      loadScript("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(gaMeasurementId || googleAdsId));
    }}
    return true;
  }}

  function configGoogleTag(tagId, config) {{
    if (!window.gtag || !tagId) return;
    window.gtag('config', tagId, config || {{}});
  }}

  function initGoogle() {{
    if (gtmContainerId && !window.google_tag_manager) {{
      pushDataLayerEvent('gtm.js', {{ 'gtm.start': Date.now() }});
      loadScript("https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(gtmContainerId));
      return;
    }}

    if (ensureGoogleTag()) {{
      if (gaMeasurementId) {{
        configGoogleTag(gaMeasurementId, {{
          page_path: window.location.pathname,
          send_page_view: true
        }});
      }}
      if (googleAdsId) {{
        configGoogleTag(googleAdsId, {{
          page_path: window.location.pathname
        }});
      }}
    }}
  }}

  function sendGoogleAdsConversion(label, eventId, extra) {{
    if (!window.gtag || !googleAdsId || !label) return;
    var payload = Object.assign({{
      send_to: googleAdsId + '/' + label
    }}, extra || {{}});
    if (eventId) payload.transaction_id = eventId;
    window.gtag('event', 'conversion', payload);
  }}

  function trackGoogleEvent(eventName, params) {{
    if (!window.gtag) return;
    var payload = Object.assign({{}}, params || {{}});
    if (!gaMeasurementId && googleAdsId) {{
      payload.send_to = googleAdsId;
    }}
    window.gtag('event', eventName, payload);
  }}

  function buildTrackingPayload(defaults, overrides) {{
    return Object.assign({{
      page_title: document.title,
      page_path: window.location.pathname,
      page_location: window.location.href
    }}, defaults || {{}}, overrides || {{}});
  }}

  function trackApplyClick(details) {{
    var eventId = (details && details.eventId) || createEventId('apply_now');
    var payload = buildTrackingPayload({{
      content_name: document.title,
      content_category: 'apply-click'
    }}, details);
    pushDataLayerEvent('dr_apply_click', payload);

    if (typeof window.fbq === 'function') {{
      window.fbq('track', 'CompleteRegistration', {{
        content_name: payload.content_name,
        content_category: payload.content_category
      }}, {{ eventID: eventId }});
    }}

    trackGoogleEvent('generate_lead', {{
      event_category: 'conversion',
      event_label: payload.href || payload.content_category,
      page_path: payload.page_path
    }});
    sendGoogleAdsConversion(googleAdsApplyLabel, eventId);
    return eventId;
  }}

  function trackPhoneClick(details) {{
    var eventId = (details && details.eventId) || createEventId('phone_call');
    var payload = buildTrackingPayload({{
      content_name: document.title,
      content_category: 'phone-click'
    }}, details);
    pushDataLayerEvent('dr_phone_click', payload);

    if (typeof window.fbq === 'function') {{
      window.fbq('track', 'Contact', {{
        content_name: payload.content_name,
        content_category: payload.content_category
      }}, {{ eventID: eventId }});
    }}

    trackGoogleEvent('contact', {{
      event_category: 'conversion',
      event_label: payload.href || payload.content_category,
      page_path: payload.page_path
    }});
    sendGoogleAdsConversion(googleAdsPhoneLabel, eventId);
    return eventId;
  }}

  function trackLeadSubmit(details) {{
    var eventId = (details && details.eventId) || createEventId('lead_submit');
    var payload = buildTrackingPayload({{
      content_name: document.title,
      content_category: 'lead-form'
    }}, details);
    pushDataLayerEvent('dr_lead_form_submit', payload);

    if (typeof window.fbq === 'function') {{
      window.fbq('track', 'Lead', {{
        content_name: payload.content_name,
        content_category: payload.content_category
      }}, {{ eventID: eventId }});
    }}

    trackGoogleEvent('generate_lead', {{
      event_category: 'form',
      event_label: payload.source || payload.content_category,
      page_path: payload.page_path
    }});
    sendGoogleAdsConversion(googleAdsLeadFormLabel, eventId);
    return eventId;
  }}

  function trackSecondaryLandingView(details) {{
    var payload = buildTrackingPayload({{
      content_name: document.title,
      content_category: 'landing-page-view'
    }}, details);
    pushDataLayerEvent('dr_secondary_landing_view', payload);
    trackGoogleEvent('view_item', {{
      event_category: 'secondary',
      event_label: payload.content_category,
      page_path: payload.page_path
    }});
  }}

  function initMeta() {{
    if (options.disableMetaInit || !pixelId || typeof window.fbq === 'function') return;
    !function(f,b,e,v,n,t,s)
    {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', pixelId);
    window.fbq('track', 'PageView');
  }}

  function fireIntentView() {{
    if (options.disableIntentViewTracking || typeof window.fbq !== 'function') return;
    var pageIntent = document.body && document.body.dataset ? document.body.dataset.pageIntent : '';
    var pageCategory = document.body && document.body.dataset ? document.body.dataset.pageCategory : '';
    if (!pageIntent && !pageCategory) return;
    window.fbq('trackCustom', 'IntentPageView', {{
      content_name: document.title,
      content_category: pageCategory || 'page',
      content_type: pageIntent || 'general'
    }}, {{ eventID: createEventId('intent_view') }});
    trackSecondaryLandingView({{
      content_category: pageCategory || 'page',
      content_type: pageIntent || 'general'
    }});
  }}

  function bindClickTracking() {{
    if (options.disableAutoClickTracking) return;

    document.querySelectorAll('a[href*="my1003app.com"], a[data-track="apply"]').forEach(function(el) {{
      if (el.dataset.drTrackBoundApply) return;
      el.dataset.drTrackBoundApply = '1';
      el.addEventListener('click', function() {{
        trackApplyClick({{
          href: el.href,
          content_name: el.dataset.contentName || document.title,
          content_category: el.dataset.contentCategory || 'apply-click'
        }});
      }});
    }});

    document.querySelectorAll('a[href^="tel:"], a[data-track="call"]').forEach(function(el) {{
      if (el.dataset.drTrackBoundCall) return;
      el.dataset.drTrackBoundCall = '1';
      el.addEventListener('click', function() {{
        trackPhoneClick({{
          href: el.getAttribute('href'),
          content_name: el.dataset.contentName || document.title,
          content_category: el.dataset.contentCategory || 'phone-click'
        }});
      }});
    }});
  }}

  function bindLeadForms() {{
    document.querySelectorAll('form[data-lead-form]').forEach(function(form) {{
      if (form.dataset.drLeadBound) return;
      form.dataset.drLeadBound = '1';
      form.addEventListener('submit', function(event) {{
        event.preventDefault();

        var formData = new FormData(form);
        var submitButton = form.querySelector('button[type="submit"]');
        var message = form.querySelector('[data-form-message]');
        var originalText = submitButton ? submitButton.textContent : '';
        var eventId = createEventId(form.dataset.eventPrefix || 'service_lead');
        var payload = {{
          firstName: formData.get('firstName') || formData.get('first_name') || '',
          email: formData.get('email') || '',
          phone: formData.get('phone') || '',
          segment: formData.get('segment') || form.dataset.segment || '',
          timeline: formData.get('timeline') || '',
          priceRange: formData.get('priceRange') || '',
          downPayment: formData.get('downPayment') || '',
          source: formData.get('source') || form.dataset.source || 'service-page',
          eventId: eventId,
          fbp: getOrCreateFbp(),
          fbc: getOrCreateFbc()
        }};

        formData.forEach(function(value, key) {{
          if (!(key in payload)) payload[key] = value;
        }});

        if (submitButton) {{
          submitButton.disabled = true;
          submitButton.textContent = 'Submitting...';
        }}
        if (message) {{
          message.textContent = '';
          message.classList.remove('is-success');
        }}

        fetch('/api/quiz-submit', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }}).then(function(response) {{
          if (!response.ok) throw new Error('Lead submission failed');
          trackLeadSubmit({{
            eventId: eventId,
            content_name: payload.segment || document.title,
            content_category: payload.source,
            source: payload.source
          }});
          if (message) {{
            message.textContent = form.dataset.successMessage || 'Thanks. Dennis will reach out shortly.';
            message.classList.add('is-success');
          }}
          form.reset();
        }}).catch(function() {{
          if (message) {{
            message.textContent = 'Something went wrong. Please call 850-346-8514.';
            message.classList.remove('is-success');
          }}
        }}).finally(function() {{
          if (submitButton) {{
            submitButton.disabled = false;
            submitButton.textContent = originalText;
          }}
        }});
      }});
    }});
  }}

  window.DrMortgageTracking = {{
    createEventId: createEventId,
    getOrCreateFbp: getOrCreateFbp,
    getOrCreateFbc: getOrCreateFbc,
    pushDataLayerEvent: pushDataLayerEvent,
    trackApplyClick: trackApplyClick,
    trackPhoneClick: trackPhoneClick,
    trackLeadSubmit: trackLeadSubmit,
    trackSecondaryLandingView: trackSecondaryLandingView
  }};

  getOrCreateFbp();
  getOrCreateFbc();
  initGoogle();
  initMeta();
  bindClickTracking();
  bindLeadForms();

  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', fireIntentView, {{ once: true }});
  }} else {{
    fireIntentView();
  }}
}})();
"""
    response = Response(js, mimetype='application/javascript')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/heloc-calculator')
def heloc_calculator():
    redesign = send_redesign_page('heloc-calculator')
    if redesign is not None:
        return redesign
    return send_file(os.path.join(BASE_DIR, 'heloc-calculator.html'),
                     mimetype='text/html')



@app.route('/dpa')
def serve_dpa():
    redesign = send_redesign_page('down-payment-assistance')
    if redesign is not None:
        return redesign
    with open(os.path.join(BASE_DIR, 'dpa.html'), encoding='utf-8') as f:
        html = normalize_dpa_program_intro(f.read())
    return Response(html, mimetype='text/html')


@app.route('/va-loans-orlando')
@app.route('/orlando-mortgage-broker')
@app.route('/first-time-homebuyer-orlando')
@app.route('/refinance-florida')
@app.route('/heloc-orlando')
def serve_service_page():
    page_slug = request.path.lstrip('/')
    return send_file(os.path.join(BASE_DIR, SERVICE_PAGE_MAP[page_slug]),
                     mimetype='text/html')


@app.route('/privacy')
def privacy():
    return send_file(os.path.join(BASE_DIR, 'privacy.html'),
                     mimetype='text/html')

@app.route('/blog/<path:slug>')
def serve_blog_post(slug):
    blog_path = os.path.join(BASE_DIR, 'blog_posts', f'{slug}.html')
    if os.path.isfile(blog_path):
        return send_file(blog_path, mimetype='text/html')
    return send_file(os.path.join(BASE_DIR, 'index.html'),
                     mimetype='text/html'), 404

@app.route('/robots.txt')
def serve_robots():
    return send_file(os.path.join(BASE_DIR, 'robots.txt'), mimetype='text/plain')

@app.route('/sitemap.xml')
def serve_sitemap():
    return send_file(os.path.join(BASE_DIR, 'sitemap.xml'), mimetype='application/xml')

# --- ManyChat Webhook: HELOC 5DAYS Sequence Enrollment ---
MANYCHAT_API_KEY = os.environ.get('MANYCHAT_API_KEY', '')
MANYCHAT_WEBHOOK_SECRET = os.environ.get('MANYCHAT_WEBHOOK_SECRET', '')

SEQUENCE_FLOWS = {
    1: 'content20260303172444_148265',  # Day 1: Debt consolidation
    2: 'content20260303174725_228524',  # Day 2: Objection buster
    3: 'content20260303174822_719478',  # Day 3: Social proof
    5: 'content20260303174926_623999',  # Day 5: Final nudge
}

@app.route('/api/manychat/enroll-redirect', methods=['GET'])
def manychat_enroll_redirect():
    """Called when ManyChat user clicks 'Run My Numbers' link.
    Enrolls them in the sequence and redirects to main site."""
    try:
        subscriber_id = request.args.get('sid', '')
        name = request.args.get('name', 'Unknown')
        
        if subscriber_id:
            app.logger.info(f'HELOC 5DAYS enrollment via link: subscriber={subscriber_id}, name={name}')
        
        return redirect('https://drmortgageusa.com/heloc-calculator')
    except Exception as e:
        app.logger.error(f'ManyChat redirect error: {e}')
        return redirect('https://drmortgageusa.com')


@app.route('/api/manychat/enroll', methods=['POST'])
def manychat_enroll():
    """Webhook called by ManyChat when someone triggers ANY keyword.
    Stores lead in Postgres DB with keyword, subscriber info, and timestamp."""
    try:
        data = request.get_json(force=True)
        subscriber_id = data.get('subscriber_id') or data.get('id')
        name = data.get('name', data.get('first_name', 'Unknown'))
        keyword = data.get('keyword', '5DAYS')
        ig_username = data.get('ig_username', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        secret = data.get('secret') or request.headers.get('X-Webhook-Secret')
        
        if not MANYCHAT_WEBHOOK_SECRET or secret != MANYCHAT_WEBHOOK_SECRET:
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
        
        if not subscriber_id:
            return jsonify({'status': 'error', 'message': 'subscriber_id required'}), 400
        
        # Store in Postgres
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO keyword_leads (subscriber_id, subscriber_name, keyword, ig_username, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (subscriber_id, keyword) DO UPDATE SET
                    subscriber_name = EXCLUDED.subscriber_name,
                    ig_username = EXCLUDED.ig_username,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone
            """, (str(subscriber_id), name, keyword.upper(), ig_username, email, phone))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_err:
            app.logger.error(f'DB insert error: {db_err}')
        
        app.logger.info(f'ManyChat keyword lead: subscriber={subscriber_id}, name={name}, keyword={keyword}, ig=@{ig_username}')
        return jsonify({'status': 'success', 'enrolled': True, 'subscriber_id': subscriber_id, 'keyword': keyword})
    except Exception as e:
        app.logger.error(f'ManyChat webhook error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/manychat/leads', methods=['GET'])
def manychat_leads():
    """API endpoint for Closer agent to pull new leads."""
    secret = request.args.get('secret') or request.headers.get('X-Webhook-Secret')
    if not MANYCHAT_WEBHOOK_SECRET or secret != MANYCHAT_WEBHOOK_SECRET:
        return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
    
    try:
        since = request.args.get('since', '2026-01-01')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT subscriber_id, subscriber_name, keyword, ig_username, email, phone, created_at, processed
            FROM keyword_leads
            WHERE created_at >= %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (since,))
        rows = cur.fetchall()
        leads = []
        for r in rows:
            leads.append({
                'subscriber_id': r[0], 'name': r[1], 'keyword': r[2],
                'ig_username': r[3], 'email': r[4], 'phone': r[5],
                'created_at': r[6].isoformat() if r[6] else None, 'processed': r[7]
            })
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'leads': leads, 'count': len(leads)})
    except Exception as e:
        app.logger.error(f'Leads fetch error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/manychat/send-sequence', methods=['POST'])
def manychat_send_sequence():
    """Called by cron to send a specific sequence message to a subscriber."""
    try:
        data = request.get_json(force=True)
        secret = data.get('secret')
        if not MANYCHAT_WEBHOOK_SECRET or secret != MANYCHAT_WEBHOOK_SECRET:
            return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
        
        subscriber_id = data.get('subscriber_id')
        day = data.get('day')
        
        if not subscriber_id or day not in SEQUENCE_FLOWS:
            return jsonify({'status': 'error', 'message': 'invalid params'}), 400
        
        flow_ns = SEQUENCE_FLOWS[day]
        resp = requests.post(
            'https://api.manychat.com/fb/sending/sendFlow',
            headers={
                'Authorization': f'Bearer {MANYCHAT_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={'subscriber_id': int(subscriber_id), 'flow_ns': flow_ns}
        )
        
        result = resp.json()
        return jsonify(result)
    except Exception as e:
        app.logger.error(f'Send sequence error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/refiwatch/lead', methods=['POST'])
def refiwatch_lead_submit():
    """Minimal owned lead endpoint for the RefiWatch funnel."""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

        name = (data.get('name') or '').strip()
        email = normalize_email(data.get('email', ''))
        phone = (data.get('phone') or '').strip()
        current_rate = (data.get('currentRate') or data.get('current_rate')
                        or '').strip()
        source = (data.get('source') or 'refiwatch').strip()
        utm_data_raw = data.get('utmData') or data.get('utm_data') or '{}'
        event_id = data.get('eventId') or data.get('event_id') or secrets.token_hex(16)

        consent = data.get('consent', False)
        if isinstance(consent, str):
            consent = consent.strip().lower() in ('1', 'true', 'yes', 'on')

        year_bought = data.get('yearBought') or data.get('year_bought')
        if year_bought in ('', None):
            year_bought = None
        elif isinstance(year_bought, str):
            year_bought = int(year_bought)

        savings_goal = data.get('savingsGoal') or data.get('savings_goal')
        if savings_goal in ('', None):
            savings_goal = None
        elif isinstance(savings_goal, str):
            savings_goal = float(savings_goal)

        utm_data = {}
        if isinstance(utm_data_raw, str):
            try:
                utm_data = json.loads(utm_data_raw) if utm_data_raw else {}
            except json.JSONDecodeError:
                utm_data = {'raw': utm_data_raw}
        elif isinstance(utm_data_raw, dict):
            utm_data = utm_data_raw

        errors = []
        if not name:
            errors.append('name is required')
        if not email or '@' not in email:
            errors.append('valid email is required')
        if not current_rate:
            errors.append('current rate is required')
        if consent is not True:
            errors.append('consent is required')

        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO refiwatch_leads
                (name, email, phone, year_bought, savings_goal, current_rate, consent, source, utm_data, meta_event_id)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            RETURNING id
            """,
            (
                name,
                email,
                phone or None,
                year_bought,
                savings_goal,
                current_rate,
                consent,
                source,
                json.dumps(utm_data or {}),
                event_id,
            ),
        )
        result = cur.fetchone()
        lead_id = result[0] if result else None

        zapier_payload = {
            'leadType': 'refiwatch',
            'source': source,
            'funnel': 'refiwatch',
            'host': current_host(),
            'name': name,
            'firstName': name.split(' ')[0],
            'email': email,
            'phone': phone,
            'yearBought': year_bought,
            'savingsGoal': savings_goal,
            'currentRate': current_rate,
            'consent': consent,
            'utmData': utm_data,
            'eventId': event_id,
            'submittedAt': datetime.now(timezone.utc).isoformat(),
        }

        zapier_forwarded = False
        try:
            if not ZAPIER_WEBHOOK_URL:
                raise RuntimeError('ZAPIER_WEBHOOK_URL is not configured')
            zapier_response = requests.post(ZAPIER_WEBHOOK_URL,
                                            json=zapier_payload,
                                            timeout=10)
            if zapier_response.ok:
                zapier_forwarded = True
        except Exception as e:
            app.logger.error(f'RefiWatch Zapier forward failed: {e}')

        meta_result = {'sent': False, 'reason': 'not_attempted'}
        try:
            meta_result = track_meta_server_event(
                'Lead',
                event_id,
                {
                    'email': email,
                    'phone': phone,
                    'firstName': name.split(' ')[0],
                },
                custom_data={
                    'content_name': 'refiwatch_lead',
                    'content_category': 'refiwatch',
                    'value': 1,
                    'currency': 'USD',
                },
            )
        except Exception as e:
            meta_result = {'sent': False, 'reason': str(e)}
            app.logger.error(f'RefiWatch Meta CAPI forward failed: {e}')

        cur.execute(
            """
            UPDATE refiwatch_leads
            SET zapier_forwarded = %s, meta_capi_sent = %s
            WHERE id = %s
            """,
            (zapier_forwarded, bool(meta_result.get('sent')), lead_id),
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'lead_id': lead_id,
            'event_id': event_id,
            'meta_capi': meta_result,
        })
    except Exception as e:
        app.logger.error(f'RefiWatch lead submission error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


def _meta_content(document, key):
    escaped = re.escape(key)
    patterns = [
        rf'<meta[^>]+(?:name|property)=["\']{escaped}["\'][^>]+content=["\']([^"\']*)["\']',
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:name|property)=["\']{escaped}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, document, re.IGNORECASE)
        if match:
            return html_lib.unescape(match.group(1)).strip()
    return ''


def _blog_category(title, description):
    haystack = f'{title} {description}'.lower()
    if any(word in haystack for word in ('va loan', 'veteran', 'irrrl', 'entitlement')):
        return 'VA loans'
    if any(word in haystack for word in ('self-employed', '1099', 'bank statement', 'investor')):
        return 'Self-employed'
    if any(word in haystack for word in ('market', 'rate buydown', 'builder incentive', 'price reduction')):
        return 'Market strategy'
    if any(word in haystack for word in ('homeowner', 'escrow', 'homestead', 'home equity', 'heloc', 'refinanc')):
        return 'Homeownership'
    return 'Buying'


@app.route('/api/rates', methods=['GET'])
def mortgage_rates_api():
    """Expose the existing updater's current market ranges to the redesign."""
    rates_path = os.path.join(BASE_DIR, 'index.html')
    rates = {}
    reviewed = ''
    try:
        with open(rates_path, encoding='utf-8') as rates_file:
            document = rates_file.read()
        block_match = re.search(
            r'const\s+MORTGAGE_RATES\s*=\s*\{(.*?)\};',
            document,
            re.DOTALL,
        )
        if block_match:
            raw_rates = dict(re.findall(r'["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']', block_match.group(1)))
            key_map = {
                'Conventional 30-Year': 'Conventional 30-year',
                'Conventional 15-Year': 'Conventional 15-year',
                'FHA 30-Year': 'FHA 30-year',
                'VA 30-Year': 'VA 30-year',
                'USDA 30-Year': 'USDA 30-year',
                'Jumbo 30-Year': 'Jumbo 30-year',
            }
            rates = {target: raw_rates[source] for source, target in key_map.items() if source in raw_rates}

        reviewed_match = re.search(r'const\s+RATE_UPDATE_DATE\s*=\s*["\']([^"\']+)["\']', document)
        reviewed = reviewed_match.group(1).strip() if reviewed_match else ''
        if not re.search(r'\b20\d{2}\b', reviewed):
            reviewed = datetime.fromtimestamp(
                os.path.getmtime(rates_path),
                tz=timezone.utc,
            ).strftime('%B %-d, %Y')
    except Exception as error:
        app.logger.error(f'Mortgage rate API failed: {error}')

    response = jsonify({'rates': rates, 'reviewed': reviewed})
    response.headers['Cache-Control'] = 'public, max-age=900, stale-while-revalidate=3600'
    return response


@app.route('/api/blog', methods=['GET'])
def blog_archive_api():
    """Return current article metadata generated by the existing blog workflow."""
    posts = []
    sitemap_dates = {}
    try:
        sitemap_path = os.path.join(BASE_DIR, 'sitemap.xml')
        if os.path.isfile(sitemap_path):
            with open(sitemap_path, encoding='utf-8') as sitemap_file:
                sitemap_document = sitemap_file.read()
            for block in re.findall(r'<url>(.*?)</url>', sitemap_document, re.DOTALL):
                loc_match = re.search(r'<loc>(.*?)</loc>', block, re.DOTALL)
                date_match = re.search(r'<lastmod>(.*?)</lastmod>', block, re.DOTALL)
                if loc_match and date_match:
                    sitemap_dates[loc_match.group(1).strip()] = date_match.group(1).strip()

        blog_dir = os.path.join(BASE_DIR, 'blog_posts')
        for filename in os.listdir(blog_dir):
            if not filename.endswith('.html') or filename == 'index.html':
                continue
            slug = filename[:-5]
            path = os.path.join(blog_dir, filename)
            with open(path, encoding='utf-8') as post_file:
                document = post_file.read()

            title = _meta_content(document, 'og:title')
            if not title:
                title_match = re.search(r'<title>(.*?)</title>', document, re.IGNORECASE | re.DOTALL)
                title = html_lib.unescape(title_match.group(1)).strip() if title_match else slug.replace('-', ' ').title()
                title = title.split('|')[0].strip()
            description = _meta_content(document, 'description')
            published = _meta_content(document, 'article:published_time')
            url = f'/blog/{slug}'
            canonical = f'https://drmortgageusa.com{url}'
            published = published[:10] or sitemap_dates.get(canonical, '')

            posts.append({
                'title': title,
                'description': description,
                'date': published,
                'category': _blog_category(title, description),
                'url': url,
            })
    except Exception as error:
        app.logger.error(f'Blog archive API failed: {error}')
        return jsonify({'posts': [], 'syncedAt': None, 'source': '/blog'}), 503

    posts.sort(key=lambda post: post.get('date') or '', reverse=True)
    response = jsonify({
        'posts': posts,
        'syncedAt': datetime.now(timezone.utc).isoformat(),
        'source': '/blog',
    })
    response.headers['Cache-Control'] = 'public, max-age=900, stale-while-revalidate=3600'
    return response


def _dpa_fallback_snapshot():
    return {
        'asOf': 'July 10, 2026',
        'notice': 'Hometown Heroes 2026 is anticipated to become available July 13, 2026.',
        'source': 'https://www.ehousingplus.com/homeownership/florida-housing-finance-corporation/program-highlights/',
        'groups': [
            {'id': 'standard-bond', 'label': 'Standard Bond', 'assistance': 'FL Assist $10,000 or FL HLP $12,500', 'fico': '640 minimum program score', 'entries': [
                {'label': 'FHA, VA, or USDA-RD', 'rate': '6.750%'},
                {'label': 'Fannie Mae HFA Preferred', 'rate': '7.500%'},
                {'label': 'Freddie Mac HFA Advantage', 'rate': '7.250%'},
            ]},
            {'id': 'standard-tba', 'label': 'Standard TBA', 'assistance': 'FL Assist $10,000 or FL HLP $12,500', 'fico': '640 minimum program score', 'entries': [
                {'label': 'FHA, VA, or USDA-RD', 'rate': '7.125%'},
                {'label': 'Freddie Mac HFA Advantage', 'detail': 'At or below 80% AMI', 'rate': '7.375%'},
                {'label': 'Freddie Mac HFA Advantage', 'detail': 'Over 80% AMI', 'rate': '7.500%'},
            ]},
            {'id': 'plus-tba', 'label': 'PLUS TBA', 'assistance': 'Forgivable assistance based on total loan amount', 'fico': '640 minimum program score', 'entries': [
                {'label': '3% DPA', 'detail': 'At or below 80% AMI', 'rate': '7.250%'},
                {'label': '4% DPA', 'detail': 'At or below 80% AMI', 'rate': '7.500%'},
                {'label': '5% DPA', 'detail': 'At or below 80% AMI', 'rate': '7.875%'},
                {'label': '3% DPA', 'detail': 'Over 80% AMI', 'rate': '7.375%'},
                {'label': '4% DPA', 'detail': 'Over 80% AMI', 'rate': '7.625%'},
                {'label': '5% DPA', 'detail': 'Over 80% AMI', 'rate': 'N/A'},
            ]},
            {'id': 'heroes-bond', 'label': 'Hometown Heroes Bond', 'assistance': '5% of the first mortgage, up to $35,000', 'fico': '640 minimum program score', 'status': 'Expected to open July 13', 'entries': [
                {'label': 'FHA, VA, or USDA-RD', 'rate': '6.000%'},
                {'label': 'Fannie Mae HFA Preferred', 'rate': '7.000%'},
                {'label': 'Freddie Mac HFA Advantage', 'rate': '6.500%'},
            ]},
            {'id': 'heroes-tba', 'label': 'Hometown Heroes TBA', 'assistance': '5% of the first mortgage, up to $35,000', 'fico': '640 minimum program score', 'status': 'Expected to open July 13', 'entries': [
                {'label': 'FHA, VA, or USDA-RD', 'rate': '6.375%'},
                {'label': 'Freddie Mac HFA Advantage', 'detail': 'At or below 80% AMI', 'rate': '6.625%'},
                {'label': 'Freddie Mac HFA Advantage', 'detail': 'Over 80% AMI', 'rate': '6.750%'},
            ]},
        ],
    }


def _dpa_cell(document, cell_id):
    match = re.search(
        rf'data-cell-id=["\']{re.escape(cell_id)}["\'][^>]*>(.*?)</t[dh]>',
        document,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ''
    value = re.sub(r'<br\s*/?\s*>', ' ', match.group(1), flags=re.IGNORECASE)
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', html_lib.unescape(value)).strip()


@app.route('/api/dpa-rates', methods=['GET'])
def dpa_rates_api():
    source = 'https://www.ehousingplus.com/homeownership/florida-housing-finance-corporation/program-highlights/'
    snapshot = _dpa_fallback_snapshot()
    live = False
    try:
        source_response = requests.get(source, timeout=12, headers={'User-Agent': 'DRMortgageUSA/2026'})
        source_response.raise_for_status()
        document = source_response.text
        date_match = re.search(
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
            _dpa_cell(document, 'A1'),
        )
        if not date_match or not _dpa_cell(document, 'G5'):
            raise ValueError('Official DPA table could not be parsed')

        def cell_rate(cell_id, fallback):
            rate_match = re.search(r'(?:\d+\.\d+%|n/a)', _dpa_cell(document, cell_id), re.IGNORECASE)
            return rate_match.group(0) if rate_match else fallback

        cell_groups = [
            ['G5', 'G6', 'G7'],
            ['G10', 'G11', 'G12'],
            ['G15', 'G16', 'G17', 'G18', 'G19', 'G20'],
            ['G23', 'G24', 'G25'],
            ['G28', 'G29', 'G30'],
        ]
        snapshot['asOf'] = date_match.group(0)
        snapshot['notice'] = _dpa_cell(document, 'A2') or snapshot['notice']
        for group, cell_ids in zip(snapshot['groups'], cell_groups):
            for entry, cell_id in zip(group['entries'], cell_ids):
                entry['rate'] = cell_rate(cell_id, entry['rate'])
        live = True
    except Exception as error:
        app.logger.warning(f'DPA rate API is using the verified fallback: {error}')

    response = jsonify({
        'snapshot': snapshot,
        'live': live,
        'syncedAt': datetime.now(timezone.utc).isoformat() if live else None,
    })
    response.headers['Cache-Control'] = 'public, max-age=900, stale-while-revalidate=3600'
    return response


@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('admin') and not is_refiwatch_request():
        return redirect(url_for('admin_login'))

    if is_refiwatch_request():
        response = send_refiwatch_asset(path)
        if response is not None:
            return response

    redesign = send_redesign_page(path)
    if redesign is not None:
        return redesign

    try:
        abs_path = os.path.join(BASE_DIR, path)
        if os.path.isfile(abs_path):
            mimetype, _ = mimetypes.guess_type(abs_path)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(abs_path, mimetype=mimetype, conditional=True)
    except Exception as e:
        app.logger.error(f'Error serving {path}: {e}')

    if is_refiwatch_request() and refiwatch_build_ready():
        return send_refiwatch_index()

    return send_file(os.path.join(BASE_DIR, 'index.html'),
                     mimetype='text/html')


@app.route('/api/quiz-submit', methods=['POST'])
def quiz_submit():
    """Receive quiz submission, store in DB, forward to Zapier"""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()

        first_name = (data.get('firstName', data.get('first_name', '')) or '').strip()
        email = normalize_email(data.get('email', ''))
        phone = normalize_phone(data.get('phone', ''))
        segment = (data.get('segment', '') or '').strip()
        price_range = (data.get('priceRange', data.get('price_range', '')) or '').strip()
        down_payment = (data.get('downPayment', data.get('down_payment', '')) or '').strip()
        timeline = (data.get('timeline', '') or '').strip()
        credit_score = (data.get('creditScore', data.get('credit_score', '')) or '').strip()
        military_status = data.get('militaryStatus',
                                   data.get('military_status', '')) or ''
        property_type = data.get('propertyType', data.get('property_type', '')) or ''
        investor_loan_type = data.get('investorLoanType',
                                      data.get('investor_loan_type', '')) or ''
        event_id = data.get('eventId', '') or data.get('event_id', '') or secrets.token_hex(16)
        source = (data.get('source', 'website') or 'website').strip()
        email_consent = as_bool(data.get('emailConsent', data.get('email_consent')))
        call_consent = as_bool(data.get('callConsent', data.get('call_consent')))
        sms_consent = as_bool(data.get('smsConsent', data.get('sms_consent')))

        errors = []
        if email and not is_valid_email(email):
            errors.append('valid email is required')
        if phone and len(phone) < 10:
            errors.append('valid phone is required')
        if not email and not phone:
            errors.append('email or phone is required')
        if not first_name and not email and not phone:
            errors.append('lead details are required')

        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        data['firstName'] = first_name
        data['email'] = email
        data['phone'] = phone
        data['segment'] = segment
        data['priceRange'] = price_range
        data['downPayment'] = down_payment
        data['timeline'] = timeline
        data['source'] = source
        data['eventId'] = event_id
        data['emailConsent'] = email_consent
        data['callConsent'] = call_consent
        data['smsConsent'] = sms_consent

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO leads (first_name, email, phone, segment, price_range, down_payment,
                             timeline, credit_score, military_status, property_type, investor_loan_type,
                             source, event_id, email_consent, call_consent, sms_consent, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id
        """, (first_name, email, phone, segment, price_range, down_payment,
              timeline, credit_score, military_status, property_type,
              investor_loan_type, source, event_id, email_consent,
              call_consent, sms_consent, json.dumps(data)))

        result = cur.fetchone()
        lead_id = result[0] if result else None

        zapier_forwarded = False
        try:
            if not ZAPIER_WEBHOOK_URL:
                raise RuntimeError('ZAPIER_WEBHOOK_URL is not configured')
            zapier_response = requests.post(ZAPIER_WEBHOOK_URL,
                                            json=data,
                                            timeout=10)
            if zapier_response.status_code == 200:
                zapier_forwarded = True
        except Exception as e:
            print(f"Zapier forward failed: {e}")

        meta_result = {'sent': False, 'reason': 'not_attempted'}
        try:
            meta_result = track_meta_server_event(
                'Lead',
                event_id,
                data,
                custom_data={
                    'content_name': segment or 'lead',
                    'content_category': source,
                    'value': 1,
                    'currency': 'USD'
                }
            )
        except Exception as e:
            meta_result = {'sent': False, 'reason': str(e)}
            print(f"Meta CAPI forward failed: {e}")

        cur.execute(
            "UPDATE leads SET zapier_forwarded = %s, meta_capi_sent = %s WHERE id = %s",
            (zapier_forwarded, bool(meta_result.get('sent')), lead_id),
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "lead_id": lead_id,
            "event_id": event_id,
            "meta_capi": meta_result,
        })

    except Exception as e:
        print(f"Quiz submission error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/admin')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    return render_template_string(ADMIN_LOGIN_TEMPLATE)


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    password = request.form.get('password', '')

    try:
        admin_pw = get_admin_password()
    except RuntimeError:
        return render_template_string(ADMIN_LOGIN_TEMPLATE,
                                      error="Admin not configured")

    if secrets.compare_digest(password, admin_pw):
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))

    return render_template_string(ADMIN_LOGIN_TEMPLATE,
                                  error="Invalid password")


@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/delete/<int:lead_id>', methods=['POST'])
@login_required
def delete_lead(lead_id):
    """Delete a lead from the database (not from Zapier)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM leads WHERE id = %s", (lead_id, ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error deleting lead: {e}")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard showing all leads"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                segment VARCHAR(50),
                price_range VARCHAR(100),
                down_payment VARCHAR(100),
                timeline VARCHAR(100),
                credit_score VARCHAR(50),
                military_status VARCHAR(50),
                property_type VARCHAR(100),
                investor_loan_type VARCHAR(100),
                zapier_forwarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        segment_filter = request.args.get('segment', '')
        search = request.args.get('search', '')

        query = "SELECT * FROM leads WHERE 1=1"
        params = []

        if segment_filter:
            query += " AND segment = %s"
            params.append(segment_filter)

        if search:
            query += " AND (first_name ILIKE %s OR email ILIKE %s OR phone ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        query += " ORDER BY created_at DESC"

        cur.execute(query, params)
        columns = [desc[0]
                   for desc in cur.description] if cur.description else []
        leads = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.execute("SELECT COUNT(*) FROM leads")
        count_result = cur.fetchone()
        total_leads = count_result[0] if count_result else 0

        cur.execute("SELECT segment, COUNT(*) FROM leads GROUP BY segment")
        segment_counts = dict(cur.fetchall())

        cur.close()
        conn.close()

        return render_template_string(ADMIN_DASHBOARD_TEMPLATE,
                                      leads=leads,
                                      total_leads=total_leads,
                                      segment_counts=segment_counts,
                                      current_segment=segment_filter,
                                      search_query=search)
    except Exception as e:
        error_msg = f"Database error: {str(e)}"
        print(error_msg)
        return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head><title>Dashboard Error</title>
            <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100 min-h-screen flex items-center justify-center">
                <div class="bg-white rounded-xl shadow-lg p-8 max-w-lg">
                    <h1 class="text-2xl font-bold text-red-600 mb-4">Database Connection Error</h1>
                    <p class="text-gray-700 mb-4">{{ error }}</p>
                    <p class="text-gray-600 text-sm mb-4">This usually means the production database needs to be set up. Please contact support if this persists.</p>
                    <a href="/admin/logout" class="bg-blue-600 text-white px-4 py-2 rounded">Logout</a>
                </div>
            </body>
            </html>
        ''',
                                      error=error_msg)


ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Dr.MortgageUSA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        navy: '#001f3f',
                        gold: '#ffb700',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-navy min-h-screen flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-bold text-navy">Admin Login</h1>
            <p class="text-gray-600 mt-2">Dr.MortgageUSA Lead Dashboard</p>
        </div>
        
        {% if error %}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" action="/admin/login">
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Password</label>
                <input type="password" name="password" 
                       class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-gold focus:outline-none"
                       placeholder="Enter admin password" required>
            </div>
            <button type="submit" 
                    class="w-full bg-gold text-navy font-bold py-3 px-6 rounded-lg hover:bg-yellow-500 transition-colors">
                Login
            </button>
        </form>
        
        <div class="mt-6 text-center">
            <a href="/" class="text-navy hover:text-gold">Back to Website</a>
        </div>
    </div>
</body>
</html>
'''

ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Dashboard - Dr.MortgageUSA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        navy: '#001f3f',
                        gold: '#ffb700',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gray-100 min-h-screen">
    <nav class="bg-navy text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">Dr.MortgageUSA <span class="text-gold">Lead Dashboard</span></h1>
            <div class="flex items-center gap-4">
                <a href="/" class="hover:text-gold">View Site</a>
                <a href="/admin/logout" class="bg-gold text-navy px-4 py-2 rounded-lg hover:bg-yellow-500">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mx-auto p-6">
        <div class="grid md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl font-bold text-navy">{{ total_leads }}</div>
                <div class="text-gray-600">Total Leads</div>
            </div>
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl font-bold text-green-600">{{ segment_counts.get('first-time', 0) }}</div>
                <div class="text-gray-600">First-Time Buyers</div>
            </div>
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl font-bold text-blue-600">{{ segment_counts.get('veteran', 0) }}</div>
                <div class="text-gray-600">Veterans</div>
            </div>
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl font-bold text-purple-600">{{ segment_counts.get('investor', 0) }}</div>
                <div class="text-gray-600">Investors</div>
            </div>
        </div>
        
        <div class="bg-white rounded-xl shadow mb-6 p-4">
            <form class="flex flex-wrap gap-4 items-end">
                <div class="flex-1 min-w-[200px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Search</label>
                    <input type="text" name="search" value="{{ search_query }}" 
                           placeholder="Search by name, email, or phone..."
                           class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                </div>
                <div class="min-w-[150px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Segment</label>
                    <select name="segment" class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                        <option value="">All Segments</option>
                        <option value="first-time" {% if current_segment == 'first-time' %}selected{% endif %}>First-Time Buyer</option>
                        <option value="veteran" {% if current_segment == 'veteran' %}selected{% endif %}>Veteran</option>
                        <option value="credit" {% if current_segment == 'credit' %}selected{% endif %}>Credit Improvement</option>
                        <option value="repeat-buyer" {% if current_segment == 'repeat-buyer' %}selected{% endif %}>Repeat Buyer</option>
                        <option value="investor" {% if current_segment == 'investor' %}selected{% endif %}>Investor</option>
                    </select>
                </div>
                <button type="submit" class="bg-gold text-navy font-bold px-6 py-2 rounded-lg hover:bg-yellow-500">
                    Filter
                </button>
                <a href="/admin/dashboard" class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300">
                    Clear
                </a>
            </form>
        </div>
        
        <div class="bg-white rounded-xl shadow overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-navy text-white">
                        <tr>
                            <th class="px-4 py-3 text-left">Date</th>
                            <th class="px-4 py-3 text-left">Name</th>
                            <th class="px-4 py-3 text-left">Email</th>
                            <th class="px-4 py-3 text-left">Phone</th>
                            <th class="px-4 py-3 text-left">Segment</th>
                            <th class="px-4 py-3 text-left">Timeline</th>
                            <th class="px-4 py-3 text-left">Price Range</th>
                            <th class="px-4 py-3 text-center">Zapier</th>
                            <th class="px-4 py-3 text-center">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if leads %}
                        {% for lead in leads %}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-3 text-sm">{{ lead.created_at.strftime('%m/%d/%Y %I:%M %p') if lead.created_at else 'N/A' }}</td>
                            <td class="px-4 py-3 font-semibold">{{ lead.first_name or 'N/A' }}</td>
                            <td class="px-4 py-3">
                                <a href="mailto:{{ lead.email }}" class="text-blue-600 hover:underline">{{ lead.email }}</a>
                            </td>
                            <td class="px-4 py-3">
                                <a href="tel:{{ lead.phone }}" class="text-blue-600 hover:underline">{{ lead.phone or 'N/A' }}</a>
                            </td>
                            <td class="px-4 py-3">
                                <span class="px-2 py-1 rounded-full text-xs font-semibold
                                    {% if lead.segment == 'first-time' %}bg-green-100 text-green-800
                                    {% elif lead.segment == 'veteran' %}bg-blue-100 text-blue-800
                                    {% elif lead.segment == 'credit' %}bg-yellow-100 text-yellow-800
                                    {% elif lead.segment == 'investor' %}bg-purple-100 text-purple-800
                                    {% else %}bg-gray-100 text-gray-800{% endif %}">
                                    {{ lead.segment or 'Unknown' }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm">{{ lead.timeline or 'N/A' }}</td>
                            <td class="px-4 py-3 text-sm">{{ lead.price_range or 'N/A' }}</td>
                            <td class="px-4 py-3 text-center">
                                {% if lead.zapier_forwarded %}
                                <span class="text-green-600">&#10003;</span>
                                {% else %}
                                <span class="text-red-600">&#10007;</span>
                                {% endif %}
                            </td>
                            <td class="px-4 py-3 text-center">
                                <form method="POST" action="/admin/delete/{{ lead.id }}" 
                                      onsubmit="return confirm('Delete this lead? This only removes it from the dashboard, not from Zapier.');">
                                    <button type="submit" class="text-red-600 hover:text-red-800 hover:bg-red-100 px-2 py-1 rounded text-sm">
                                        Delete
                                    </button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                        {% else %}
                        <tr>
                            <td colspan="9" class="px-4 py-8 text-center text-gray-500">
                                No leads found. Quiz submissions will appear here.
                            </td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
'''

init_database()

# ============================================
# AUTO-REFRESH RATE UPDATER (Background Thread)
# Fetches rates from MortgageNewsDaily every 2 hours
# during market hours and updates index.html on disk
# ============================================
import threading
import time as _time


def _rate_update_scheduler():
    from update_rates import fetch_mnd_rates, update_html_rates
    import pytz
    from datetime import datetime as dt
    _time.sleep(30)
    while True:
        try:
            est = pytz.timezone('US/Eastern')
            now = dt.now(est)
            hour = now.hour
            weekday = now.weekday()
            if 6 <= hour <= 21:
                print(
                    f"[Auto-Updater] Fetching rates at {now.strftime('%I:%M %p ET')}"
                )
                rates = fetch_mnd_rates()
                if rates:
                    success = update_html_rates(rates)
                    print(
                        f"[Auto-Updater] Rates {'updated' if success else 'unchanged'}"
                    )
                else:
                    print("[Auto-Updater] Could not fetch rates from MND")
            else:
                print(
                    f"[Auto-Updater] Outside market hours ({hour}:00 ET), skipping"
                )
            interval = 21600 if weekday >= 5 else 7200
            _time.sleep(interval)
        except Exception as e:
            print(f"[Auto-Updater] Error: {e}")
            _time.sleep(300)


RATE_UPDATER_ENABLED = os.environ.get('ENABLE_RATE_UPDATER', '1').strip().lower() not in ('0', 'false', 'no')

if RATE_UPDATER_ENABLED:
    _rate_thread = threading.Thread(target=_rate_update_scheduler, daemon=True)
    _rate_thread.start()
    print("[Auto-Updater] Started - 2hr weekdays, 6hr weekends, market hours only")
else:
    print("[Auto-Updater] Disabled by environment")


# --- Blog Routes ---
@app.route('/blog')
@app.route('/blog/')
def blog_index():
    redesign = send_redesign_page('blog')
    if redesign is not None:
        return redesign
    return send_from_directory(os.path.join(BASE_DIR, 'blog_posts'), 'index.html')


@app.route('/blog/<slug>')
def blog_post(slug):
    filename = f"{slug}.html"
    filepath = os.path.join(BASE_DIR, 'blog_posts', filename)
    if os.path.exists(filepath):
        return send_from_directory(os.path.join(BASE_DIR, 'blog_posts'), filename)
    return send_from_directory(BASE_DIR, 'index.html'), 404


# --- Performance: Caching Headers ---
@app.after_request
def add_cache_headers(response):
    try:
        if response.headers.get('Cache-Control'):
            pass
        # Static assets: cache for 1 week
        elif response.content_type and any(
                t in response.content_type for t in
            ['image/', 'font/', 'text/css', 'javascript', 'video/']):
            response.headers[
                'Cache-Control'] = 'public, max-age=604800, immutable'
        # HTML: cache for 5 minutes (allows rate updates to propagate)
        elif response.content_type and 'text/html' in response.content_type:
            response.headers[
                'Cache-Control'] = 'public, max-age=300, must-revalidate'
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers[
            'Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(self), payment=()'
    except Exception as e:
        app.logger.error(f'Error in after_request: {e}')
    return response


@app.errorhandler(404)
def page_not_found(e):
    try:
        return send_file(os.path.join(BASE_DIR, '404.html'),
                         mimetype='text/html'), 404
    except Exception:
        return '<h1>404 - Page Not Found</h1>', 404


@app.errorhandler(500)
def server_error(e):
    try:
        return send_file(os.path.join(BASE_DIR, '404.html'),
                         mimetype='text/html'), 500
    except Exception:
        return '<h1>500 - Server Error</h1>', 500


@app.route('/api/db/migrate', methods=['POST'])
def db_migrate():
    """One-time migration endpoint. Creates keyword_leads table."""
    secret = request.args.get('secret') or request.headers.get('X-Webhook-Secret')
    if not MANYCHAT_WEBHOOK_SECRET or secret != MANYCHAT_WEBHOOK_SECRET:
        return jsonify({'status': 'error', 'message': 'unauthorized'}), 401
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS keyword_leads (
                id SERIAL PRIMARY KEY,
                subscriber_id VARCHAR(100) NOT NULL,
                subscriber_name VARCHAR(200),
                keyword VARCHAR(50),
                ig_username VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                UNIQUE(subscriber_id, keyword)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'keyword_leads table created'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# deploy v3 static-folder-fix all-sendfile
