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

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/6074472/uu7c1t0/"
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
    return request.host.split(':')[0].lower()


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


def normalize_email(value):
    return (value or '').strip().lower()


def normalize_phone(value):
    return ''.join(ch for ch in (value or '') if ch.isdigit())


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


@app.route('/')
def serve_index():
    if is_refiwatch_request() and refiwatch_build_ready():
        return send_refiwatch_index()
    return send_file(os.path.join(BASE_DIR, 'index.html'),
                     mimetype='text/html')


@app.route('/site-tracking.js')
def site_tracking():
    ga_measurement_id = os.environ.get('GA_MEASUREMENT_ID', '').strip()
    gtm_container_id = os.environ.get('GTM_CONTAINER_ID', '').strip()
    js = f"""
(function() {{
  if (window.__drSiteTrackingLoaded) return;
  window.__drSiteTrackingLoaded = true;

  var pixelId = {json.dumps(META_PIXEL_ID)};
  var gaMeasurementId = {json.dumps(ga_measurement_id)};
  var gtmContainerId = {json.dumps(gtm_container_id)};
  var options = window.DR_TRACKING_OPTIONS || {{}};

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

  function initGoogle() {{
    if (gtmContainerId && !window.google_tag_manager) {{
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({{ 'gtm.start': Date.now(), event: 'gtm.js' }});
      loadScript("https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(gtmContainerId));
      return;
    }}

    if (gaMeasurementId && !window.gtag) {{
      window.dataLayer = window.dataLayer || [];
      window.gtag = function() {{ window.dataLayer.push(arguments); }};
      window.gtag('js', new Date());
      window.gtag('config', gaMeasurementId, {{
        page_path: window.location.pathname,
        send_page_view: true
      }});
      loadScript("https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(gaMeasurementId));
    }}
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
  }}

  function bindClickTracking() {{
    if (options.disableAutoClickTracking) return;

    document.querySelectorAll('a[href*="my1003app.com"], a[data-track="apply"]').forEach(function(el) {{
      if (el.dataset.drTrackBoundApply) return;
      el.dataset.drTrackBoundApply = '1';
      el.addEventListener('click', function() {{
        if (typeof window.fbq === 'function') {{
          window.fbq('track', 'CompleteRegistration', {{
            content_name: el.dataset.contentName || document.title,
            content_category: el.dataset.contentCategory || 'apply-click'
          }}, {{ eventID: createEventId('apply_now') }});
        }}
        if (window.gtag && gaMeasurementId) {{
          window.gtag('event', 'generate_lead', {{
            event_category: 'conversion',
            event_label: el.href
          }});
        }}
      }});
    }});

    document.querySelectorAll('a[href^="tel:"], a[data-track="call"]').forEach(function(el) {{
      if (el.dataset.drTrackBoundCall) return;
      el.dataset.drTrackBoundCall = '1';
      el.addEventListener('click', function() {{
        if (typeof window.fbq === 'function') {{
          window.fbq('track', 'Contact', {{
            content_name: el.dataset.contentName || document.title,
            content_category: el.dataset.contentCategory || 'phone-click'
          }}, {{ eventID: createEventId('phone_call') }});
        }}
        if (window.gtag && gaMeasurementId) {{
          window.gtag('event', 'contact', {{
            event_category: 'conversion',
            event_label: el.getAttribute('href')
          }});
        }}
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

        if (typeof window.fbq === 'function') {{
          window.fbq('track', 'Lead', {{
            content_name: payload.segment || document.title,
            content_category: payload.source
          }}, {{ eventID: eventId }});
        }}

        if (window.gtag && gaMeasurementId) {{
          window.gtag('event', 'generate_lead', {{
            event_category: 'form',
            event_label: payload.source
          }});
        }}

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
    getOrCreateFbc: getOrCreateFbc
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
    return Response(js, mimetype='application/javascript')


@app.route('/heloc-calculator')
def heloc_calculator():
    return send_file(os.path.join(BASE_DIR, 'heloc-calculator.html'),
                     mimetype='text/html')



@app.route('/dpa')
def serve_dpa():
    return send_file(os.path.join(BASE_DIR, 'dpa.html'),
                     mimetype='text/html')


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
MANYCHAT_API_KEY = os.environ.get('MANYCHAT_API_KEY', '1852822:98408d8d5653dd3cc23e831449be31a8')
MANYCHAT_WEBHOOK_SECRET = os.environ.get('MANYCHAT_WEBHOOK_SECRET', 'h5d_xK9mP2vR')

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
        
        if secret != MANYCHAT_WEBHOOK_SECRET:
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
    if secret != MANYCHAT_WEBHOOK_SECRET:
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
        if secret != MANYCHAT_WEBHOOK_SECRET:
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


@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('admin') and not is_refiwatch_request():
        return redirect(url_for('admin_login'))

    if is_refiwatch_request():
        response = send_refiwatch_asset(path)
        if response is not None:
            return response

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
        data = request.get_json() or request.form.to_dict()

        first_name = data.get('firstName', data.get('first_name', ''))
        email = data.get('email', '')
        phone = data.get('phone', '')
        segment = data.get('segment', '')
        price_range = data.get('priceRange', data.get('price_range', ''))
        down_payment = data.get('downPayment', data.get('down_payment', ''))
        timeline = data.get('timeline', '')
        credit_score = data.get('creditScore', data.get('credit_score', ''))
        military_status = data.get('militaryStatus',
                                   data.get('military_status', ''))
        property_type = data.get('propertyType', data.get('property_type', ''))
        investor_loan_type = data.get('investorLoanType',
                                      data.get('investor_loan_type', ''))
        event_id = data.get('eventId', '') or data.get('event_id', '') or secrets.token_hex(16)
        source = data.get('source', 'website')

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO leads (first_name, email, phone, segment, price_range, down_payment, 
                             timeline, credit_score, military_status, property_type, investor_loan_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (first_name, email, phone, segment, price_range, down_payment,
              timeline, credit_score, military_status, property_type,
              investor_loan_type))

        result = cur.fetchone()
        lead_id = result[0] if result else None

        zapier_forwarded = False
        try:
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

        cur.execute("UPDATE leads SET zapier_forwarded = %s WHERE id = %s",
                    (zapier_forwarded, lead_id))
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
        # Static assets: cache for 1 week
        if response.content_type and any(
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
    if secret != MANYCHAT_WEBHOOK_SECRET:
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
