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
import csv
import io
import re
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


def normalize_email(value):
    return (value or '').strip().lower()


def normalize_phone(value):
    return ''.join(ch for ch in (value or '') if ch.isdigit())


def is_valid_email(value):
    email = normalize_email(value)
    if not email:
        return False
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None


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


RETR_STATUS_OPTIONS = [
    ('new', 'New'),
    ('reviewing', 'Reviewing'),
    ('battle_plan_ready', 'Battle Plan Ready'),
    ('approved_to_contact', 'Approved To Contact'),
    ('contacted', 'Contacted'),
    ('nurture', 'Nurture'),
    ('passed', 'Passed'),
]
RETR_STATUS_LABELS = dict(RETR_STATUS_OPTIONS)
RETR_CALL_COACH_SKILL_PATH = os.path.expanduser('~/.codex/skills/retr-call-coach')


def ensure_retr_tables(cur):
    """Create RETR Scout tables without touching any external systems."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS retr_import_batches (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255),
            total_rows INTEGER DEFAULT 0,
            imported_rows INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS retr_realtor_targets (
            id SERIAL PRIMARY KEY,
            batch_id INTEGER REFERENCES retr_import_batches(id) ON DELETE SET NULL,
            source_row JSONB,
            full_name VARCHAR(255) NOT NULL,
            brokerage VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(75),
            city VARCHAR(120),
            state VARCHAR(50),
            buyer_volume NUMERIC(14, 2) DEFAULT 0,
            seller_volume NUMERIC(14, 2) DEFAULT 0,
            total_volume NUMERIC(14, 2) DEFAULT 0,
            buyer_units INTEGER DEFAULT 0,
            seller_units INTEGER DEFAULT 0,
            total_units INTEGER DEFAULT 0,
            zip_code VARCHAR(20),
            primary_zip_codes JSONB DEFAULT '[]'::jsonb,
            agent_type VARCHAR(80),
            primary_markets TEXT,
            property_mix TEXT,
            lender_name VARCHAR(255),
            dominant_lender VARCHAR(255),
            lender_loyalty_pct NUMERIC(6, 2) DEFAULT 0,
            has_preferred_lender BOOLEAN DEFAULT FALSE,
            lender_loyalty_gap BOOLEAN DEFAULT FALSE,
            buyer_score INTEGER DEFAULT 0,
            seller_score INTEGER DEFAULT 0,
            target_score INTEGER DEFAULT 0,
            target_tier VARCHAR(1) DEFAULT 'D',
            team_leader BOOLEAN DEFAULT FALSE,
            bridge_needed BOOLEAN DEFAULT FALSE,
            draft_outreach TEXT,
            battle_plan TEXT,
            web_intel TEXT,
            instagram_intel TEXT,
            call_coach_plan JSONB,
            call_coach_generated_at TIMESTAMP,
            call_coach_pdf_path TEXT,
            call_coach_approved_at TIMESTAMP,
            status VARCHAR(50) DEFAULT 'new',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for column_sql in (
        "ADD COLUMN IF NOT EXISTS zip_code VARCHAR(20)",
        "ADD COLUMN IF NOT EXISTS primary_zip_codes JSONB DEFAULT '[]'::jsonb",
        "ADD COLUMN IF NOT EXISTS agent_type VARCHAR(80)",
        "ADD COLUMN IF NOT EXISTS primary_markets TEXT",
        "ADD COLUMN IF NOT EXISTS property_mix TEXT",
        "ADD COLUMN IF NOT EXISTS dominant_lender VARCHAR(255)",
        "ADD COLUMN IF NOT EXISTS lender_loyalty_pct NUMERIC(6, 2) DEFAULT 0",
        "ADD COLUMN IF NOT EXISTS web_intel TEXT",
        "ADD COLUMN IF NOT EXISTS instagram_intel TEXT",
        "ADD COLUMN IF NOT EXISTS call_coach_plan JSONB",
        "ADD COLUMN IF NOT EXISTS call_coach_generated_at TIMESTAMP",
        "ADD COLUMN IF NOT EXISTS call_coach_pdf_path TEXT",
        "ADD COLUMN IF NOT EXISTS call_coach_approved_at TIMESTAMP",
    ):
        cur.execute(f"ALTER TABLE retr_realtor_targets {column_sql}")

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_retr_targets_score
        ON retr_realtor_targets (target_score DESC)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_retr_targets_tier
        ON retr_realtor_targets (target_tier)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_retr_targets_status
        ON retr_realtor_targets (status)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_retr_targets_zip
        ON retr_realtor_targets (zip_code)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_retr_targets_loyalty
        ON retr_realtor_targets (lender_loyalty_pct)
    """)


def _normalize_retr_key(value):
    return re.sub(r'[^a-z0-9]+', '', (value or '').strip().lower())


def _retr_row_lookup(row):
    return {_normalize_retr_key(key): key for key in row.keys()}


def get_retr_csv_value(row, candidates, token_groups=None):
    lookup = _retr_row_lookup(row)
    for candidate in candidates:
        raw_key = lookup.get(_normalize_retr_key(candidate))
        if raw_key is not None:
            return (row.get(raw_key) or '').strip()

    for group in token_groups or []:
        normalized_tokens = [_normalize_retr_key(token) for token in group]
        for normalized_key, raw_key in lookup.items():
            if all(token and token in normalized_key
                   for token in normalized_tokens):
                return (row.get(raw_key) or '').strip()

    return ''


def parse_retr_number(value):
    text = str(value or '').strip()
    if not text:
        return 0.0

    negative = text.startswith('(') and text.endswith(')')
    text = text.replace(',', '').replace('$', '').replace('%', '').strip().lower()
    text = text.strip('()')

    multiplier = 1.0
    if text.endswith('m'):
        multiplier = 1000000.0
        text = text[:-1]
    elif text.endswith('k'):
        multiplier = 1000.0
        text = text[:-1]

    text = re.sub(r'[^0-9.\-]+', '', text)
    if not text or text in ('-', '.', '-.'):
        return 0.0

    try:
        number = float(text) * multiplier
    except ValueError:
        return 0.0
    return -number if negative else number


def parse_retr_int(value):
    return int(round(parse_retr_number(value)))


def parse_retr_percent(value):
    percent = parse_retr_number(value)
    if 0 < percent <= 1:
        percent *= 100
    return max(0.0, min(percent, 100.0))


def parse_retr_bool(value):
    text = str(value or '').strip().lower()
    if text in ('1', 'true', 'yes', 'y', 'preferred', 'has lender'):
        return True
    if text in ('0', 'false', 'no', 'n', 'none', 'no lender'):
        return False
    return False


def format_retr_money(value):
    number = float(value or 0)
    if number >= 1000000:
        return f"${number / 1000000:.1f}M"
    if number >= 1000:
        return f"${number / 1000:.0f}K"
    return f"${number:,.0f}"


def format_retr_percent(value):
    number = float(value or 0)
    if not number:
        return "0%"
    return f"{number:.0f}%"


def retr_production_score(volume, units):
    score = 0
    volume = float(volume or 0)
    units = int(units or 0)

    if volume >= 10000000:
        score += 35
    elif volume >= 5000000:
        score += 27
    elif volume >= 2000000:
        score += 18
    elif volume > 0:
        score += 10

    if units >= 25:
        score += 25
    elif units >= 12:
        score += 18
    elif units >= 6:
        score += 10
    elif units > 0:
        score += 5

    return min(score, 60)


def retr_target_tier(score):
    if score >= 80:
        return 'A'
    if score >= 60:
        return 'B'
    if score >= 40:
        return 'C'
    return 'D'


def _retr_lender_has_value(lender_name):
    normalized = (lender_name or '').strip().lower()
    return bool(normalized) and normalized not in (
        'none', 'n/a', 'na', 'unknown', 'tbd', 'cash', 'no lender',
        'not listed'
    )


def normalize_retr_zip(value):
    matches = re.findall(r'\b\d{5}(?:-\d{4})?\b', str(value or ''))
    return matches[0][:5] if matches else ''


def extract_retr_zip_codes(row):
    explicit_zip = get_retr_csv_value(
        row,
        ('zip', 'zipcode', 'zip code', 'postal code', 'primary zip',
         'market zip', 'property zip', 'transaction zip', 'mailing zip'),
        token_groups=(('zip', ), ('postal', 'code')),
    )
    candidates = []
    if explicit_zip:
        candidates.append(explicit_zip)

    for key, value in row.items():
        normalized_key = _normalize_retr_key(key)
        if any(token in normalized_key for token in (
                'zip', 'postal', 'address', 'marketarea', 'farmarea')):
            candidates.append(value)

    zip_codes = []
    seen = set()
    for value in candidates:
        for match in re.findall(r'\b\d{5}(?:-\d{4})?\b', str(value or '')):
            zip_code = match[:5]
            if zip_code not in seen:
                seen.add(zip_code)
                zip_codes.append(zip_code)
    return zip_codes


def classify_retr_agent_type(buyer_units, seller_units, buyer_volume,
                             seller_volume, total_units):
    buyer_signal = int(buyer_units or 0) or (float(buyer_volume or 0) / 1000000)
    seller_signal = int(seller_units or 0) or (float(seller_volume or 0) / 1000000)
    if not buyer_signal and not seller_signal and total_units:
        return 'Balanced producer'
    if buyer_signal and seller_signal:
        if buyer_signal >= seller_signal * 1.6:
            return 'Buyer-side heavy'
        if seller_signal >= buyer_signal * 1.6:
            return 'Listing-side heavy'
        return 'Balanced producer'
    if buyer_signal:
        return 'Buyer-side focused'
    if seller_signal:
        return 'Listing-side focused'
    return 'Production unknown'


def detect_retr_team_leader(row):
    role_blob = ' '.join([
        get_retr_csv_value(row, ('role', 'title', 'agent title', 'position')),
        get_retr_csv_value(row, ('team name', 'team', 'group name')),
        get_retr_csv_value(row, ('bio', 'profile', 'description')),
    ]).lower()
    team_size = parse_retr_int(
        get_retr_csv_value(row, ('team size', 'team members', 'agents on team'),
                           token_groups=(('team', 'size'), ('team', 'members'))))
    leader_terms = (
        'team lead', 'team leader', 'team owner', 'rainmaker',
        'broker owner', 'broker/owner', 'principal', 'managing broker'
    )
    has_team_name = bool(
        get_retr_csv_value(row, ('team name', 'team', 'group name')))
    return any(term in role_blob
               for term in leader_terms) or team_size >= 2 or has_team_name


def detect_retr_lender_gap(row, lender_name, total_volume, total_units):
    preferred_raw = get_retr_csv_value(
        row,
        ('preferred lender', 'lender partner', 'mortgage partner',
         'in-house lender', 'preferred mortgage lender'),
        token_groups=(('preferred', 'lender'), ('mortgage', 'partner'),
                      ('lender', 'partner')),
    )
    lender_share = parse_retr_percent(
        get_retr_csv_value(
            row,
            ('lender share', 'preferred lender share',
             'mortgage capture rate', 'capture rate', 'lender loyalty',
             'lender loyalty pct', 'lender loyalty %', 'dominant lender share'),
            token_groups=(('lender', 'share'), ('capture', 'rate'),
                          ('lender', 'loyalty'), ('dominant', 'lender',
                                                  'share'))))
    has_preferred_lender = (
        parse_retr_bool(preferred_raw)
        if preferred_raw else _retr_lender_has_value(lender_name)
    )
    if not has_preferred_lender and lender_share >= 35:
        has_preferred_lender = True
    meaningful_production = float(total_volume or 0) >= 1500000 or int(total_units
                                                                       or 0) >= 4

    if not meaningful_production:
        return has_preferred_lender, False

    if has_preferred_lender and (not lender_share or lender_share >= 35):
        return True, False

    if lender_share and lender_share < 25:
        return has_preferred_lender, True

    return has_preferred_lender, not has_preferred_lender


def extract_retr_dominant_lender(row, fallback_lender):
    return get_retr_csv_value(
        row,
        ('dominant lender', 'top lender', 'primary lender',
         'most used lender', 'buyer side lender', 'preferred lender'),
        token_groups=(('dominant', 'lender'), ('top', 'lender'),
                      ('primary', 'lender'), ('buyer', 'lender')),
    ) or fallback_lender


def extract_retr_lender_loyalty_pct(row):
    return parse_retr_percent(
        get_retr_csv_value(
            row,
            ('lender loyalty pct', 'lender loyalty %', 'lender loyalty',
             'preferred lender share', 'dominant lender share',
             'lender share', 'mortgage capture rate', 'capture rate'),
            token_groups=(('lender', 'loyalty'), ('preferred', 'lender',
                                                  'share'),
                          ('dominant', 'lender', 'share'),
                          ('lender', 'share'), ('capture', 'rate')),
        ))


def retr_zip_opportunity_score(target_count, avg_loyalty_pct, gap_count,
                               priority_count, bridge_count):
    loyalty_gap_points = max(0.0, 35.0 - float(avg_loyalty_pct or 0))
    volume_points = min(int(target_count or 0) * 5, 25)
    return round(
        loyalty_gap_points + volume_points + (int(gap_count or 0) * 30) +
        (int(priority_count or 0) * 20) + (int(bridge_count or 0) * 15),
        1,
    )


def build_retr_draft_outreach(target):
    first_name = target['full_name'].split()[0] if target['full_name'] else 'there'
    strongest_side = 'buyer-side' if target['buyer_score'] >= target[
        'seller_score'] else 'seller-side'
    production = format_retr_money(target['total_volume'])
    zip_line = (
        f" The primary ZIP I have on file is {target.get('zip_code')}."
        if target.get('zip_code') else ''
    )
    gap_line = (
        "I noticed there may be room to strengthen the lending side of your pipeline."
        if target['lender_loyalty_gap'] else
        "I wanted to compare notes on where a lending partner could be useful without disrupting what already works."
    )
    return (
        "Draft only - not sent.\n\n"
        f"Hi {first_name}, I was reviewing your recent {strongest_side} activity "
        f"and saw roughly {production} in tracked production.{zip_line} {gap_line}\n\n"
        "If Dennis approves outreach, the conversation should stay consultative: "
        "production fit, current lender coverage, and whether a bridge partner "
        "would help on tricky buyer files."
    )


def build_retr_battle_plan(target):
    strengths = []
    if target['buyer_score'] >= 35:
        strengths.append("strong buyer-side activity")
    if target['seller_score'] >= 35:
        strengths.append("meaningful seller-side listing activity")
    if target['team_leader']:
        strengths.append("team or leadership signal")
    if not strengths:
        strengths.append("emerging production signal")

    lender_angle = (
        "Open the lender-loyalty gap gently: ask who currently handles hard files, "
        "fast preapprovals, VA, DPA, or self-employed buyers."
        if target['lender_loyalty_gap'] else
        "Do not challenge the existing lender relationship; look for overflow, niche, "
        "or second-opinion opportunities."
    )
    bridge_line = (
        "Bridge needed: look for a warm intro path before any direct outreach."
        if target['bridge_needed'] else
        "Bridge optional: direct outreach can wait for Dennis approval."
    )
    zip_line = (
        f"ZIP strategy: use {target.get('zip_code')} as the local market lens, "
        f"with lender loyalty at {format_retr_percent(target.get('lender_loyalty_pct'))}."
        if target.get('zip_code') else
        "ZIP strategy: no primary ZIP was found in the RETR export; confirm market focus before prioritizing."
    )
    return "\n".join([
        "Pre-call battle plan",
        "",
        f"1. Lead with the observed signal: {', '.join(strengths)}.",
        f"2. Production read: buyer score {target['buyer_score']}, seller score {target['seller_score']}, tier {target['target_tier']}.",
        f"3. {zip_line}",
        f"4. {lender_angle}",
        f"5. {bridge_line}",
        "6. Guardrail: this is draft-only scouting until Dennis approves the next step."
    ])


def build_retr_call_coach_plan(target):
    loyalty_pct = float(target.get('lender_loyalty_pct') or 0)
    zip_code = target.get('zip_code') or 'Unconfirmed'
    loyalty_read = (
        "Open lane: lender loyalty appears thin enough to warrant a strategy call."
        if target.get('lender_loyalty_gap') or loyalty_pct < 25 else
        "Protected relationship: do not challenge the current lender; look for overflow or niche files."
    )
    first_name = target.get('full_name', 'there').split()[0]
    production = format_retr_money(target.get('total_volume'))

    return {
        'title': 'Draft-only RETR Call Coach Battle Plan',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'guardrail':
        'Draft-only. No DMs, emails, calls, CRM writes, RETR writes, ad changes, Zapier actions, or ManyChat actions.',
        'target': {
            'name': target.get('full_name'),
            'brokerage': target.get('brokerage'),
            'tier': target.get('target_tier'),
            'target_score': target.get('target_score'),
            'agent_type': target.get('agent_type') or 'Production unknown',
            'primary_zip': zip_code,
            'market': target.get('primary_markets') or target.get('city'),
            'production': production,
        },
        'zip_strategy': {
            'primary_zip': zip_code,
            'lender_loyalty_pct': loyalty_pct,
            'dominant_lender': target.get('dominant_lender')
            or target.get('lender_name') or 'Not listed',
            'read': loyalty_read,
            'priority_reason':
            'Prioritize when this ZIP also has A/B agents, multiple lender gaps, or bridge-needed targets.',
        },
        'call_openers': [
            f"{first_name}, I was looking at activity around {zip_code} and wanted to compare notes on buyer financing friction without stepping on what already works.",
            f"The reason I thought a strategy call might be useful is the production signal around {production} and the lender-loyalty read in the RETR data.",
        ],
        'talking_points': [
            'Ask who handles hard-to-place buyers, fast preapprovals, VA, DPA, self-employed, and second-opinion scenarios.',
            'Use the ZIP as the local lens: inventory pressure, buyer affordability, and where lender speed creates listing-side confidence.',
            'Keep the conversation consultative until Dennis approves any external outreach step.',
        ],
        'predicted_objections': [
            {
                'objection': 'I already have a lender.',
                'response':
                'That makes sense. I am not trying to replace a good relationship. I am looking for the gaps: overflow, niche files, or second opinions when a deal needs a save.'
            },
            {
                'objection': 'My buyers are already preapproved.',
                'response':
                'Perfect. The value may be in speed, certainty, and backup options when the first approval gets shaky.'
            },
        ],
        'first_touch_draft': target.get('draft_outreach') or '',
        'mock_script': [
            f"Dennis: {first_name}, quick question. In {zip_code}, where do buyer files usually get stuck right now?",
            "Realtor: It depends on the buyer.",
            "Dennis: That is exactly the lane I am looking for. I do not need to disrupt your lender stack; I want to be useful when the normal path is not enough.",
        ],
        'scorecard_focus': [
            'Did we identify the current lender relationship without attacking it?',
            'Did we find a concrete ZIP-specific financing pain point?',
            'Did we leave with an approved next step instead of creating external automation?'
        ],
    }


def build_retr_target(row, batch_id=None):
    full_name = get_retr_csv_value(
        row,
        ('agent name', 'realtor name', 'full name', 'name', 'contact name',
         'agent'),
        token_groups=(('agent', 'name'), ('realtor', 'name')))
    if not full_name:
        first = get_retr_csv_value(row, ('first name', 'firstname'))
        last = get_retr_csv_value(row, ('last name', 'lastname'))
        full_name = f"{first} {last}".strip() or 'Unknown Realtor'

    brokerage = get_retr_csv_value(
        row, ('brokerage', 'company', 'office', 'agency', 'brokerage name'))
    email = get_retr_csv_value(row, ('email', 'email address', 'agent email'))
    phone = get_retr_csv_value(
        row, ('phone', 'phone number', 'mobile phone', 'cell', 'agent phone'))
    city = get_retr_csv_value(row, ('city', 'market', 'primary city'))
    state = get_retr_csv_value(row, ('state', 'province'))
    lender_name = get_retr_csv_value(
        row,
        ('lender', 'lender name', 'preferred lender', 'mortgage lender',
         'loan officer', 'loan officer name'),
        token_groups=(('lender', 'name'), ('loan', 'officer')))
    zip_codes = extract_retr_zip_codes(row)
    zip_code = zip_codes[0] if zip_codes else ''
    primary_markets = get_retr_csv_value(
        row,
        ('primary market', 'markets', 'market area', 'farm area',
         'territory', 'service area'),
        token_groups=(('primary', 'market'), ('market', 'area'),
                      ('farm', 'area'), ('service', 'area')),
    ) or ', '.join(value for value in (city, state, zip_code) if value)
    property_mix = get_retr_csv_value(
        row,
        ('property mix', 'property type', 'specialty', 'niche',
         'listing mix'),
        token_groups=(('property', 'mix'), ('property', 'type'),
                      ('listing', 'mix')),
    )
    dominant_lender = extract_retr_dominant_lender(row, lender_name)
    lender_loyalty_pct = extract_retr_lender_loyalty_pct(row)
    web_intel = get_retr_csv_value(
        row, ('web intel', 'website notes', 'profile notes', 'bio'))
    instagram_intel = get_retr_csv_value(
        row, ('instagram intel', 'instagram notes', 'ig notes',
              'instagram handle', 'ig username'))

    buyer_volume = parse_retr_number(
        get_retr_csv_value(row,
                           ('buyer volume', 'buy side volume',
                            'buyer-side volume', 'buyer sales volume'),
                           token_groups=(('buyer', 'volume'),
                                         ('buy', 'side', 'volume'))))
    seller_volume = parse_retr_number(
        get_retr_csv_value(row,
                           ('seller volume', 'sell side volume',
                            'seller-side volume', 'listing volume'),
                           token_groups=(('seller', 'volume'),
                                         ('listing', 'volume'))))
    total_volume = parse_retr_number(
        get_retr_csv_value(row,
                           ('total volume', 'sales volume',
                            'closed volume', 'production volume'),
                           token_groups=(('total', 'volume'),
                                         ('sales', 'volume'))))
    buyer_units = parse_retr_int(
        get_retr_csv_value(row,
                           ('buyer units', 'buy side units',
                            'buyer-side units', 'buyer transactions'),
                           token_groups=(('buyer', 'units'),
                                         ('buyer', 'transactions'))))
    seller_units = parse_retr_int(
        get_retr_csv_value(row,
                           ('seller units', 'sell side units',
                            'seller-side units', 'listing units'),
                           token_groups=(('seller', 'units'),
                                         ('listing', 'units'))))
    total_units = parse_retr_int(
        get_retr_csv_value(row,
                           ('total units', 'transactions', 'sides',
                            'closed units'),
                           token_groups=(('total', 'units'),
                                         ('closed', 'units'))))

    side_detail_missing = (
        not buyer_volume and not seller_volume and not buyer_units
        and not seller_units
    )

    if not total_volume:
        total_volume = buyer_volume + seller_volume
    if not total_units:
        total_units = buyer_units + seller_units

    if not buyer_volume and not seller_volume and total_volume:
        buyer_volume = total_volume / 2
        seller_volume = total_volume / 2
    if not buyer_units and not seller_units and total_units:
        buyer_units = total_units // 2
        seller_units = total_units - buyer_units

    buyer_score = retr_production_score(buyer_volume, buyer_units)
    seller_score = retr_production_score(seller_volume, seller_units)
    total_score = (
        retr_production_score(total_volume, total_units)
        if side_detail_missing else 0
    )
    agent_type = classify_retr_agent_type(buyer_units, seller_units,
                                          buyer_volume, seller_volume,
                                          total_units)
    has_preferred_lender, lender_gap = detect_retr_lender_gap(
        row, lender_name or dominant_lender, total_volume, total_units)
    team_leader = detect_retr_team_leader(row)

    target_score = max(buyer_score, seller_score, total_score)
    if lender_gap:
        target_score += 20
    if team_leader:
        target_score += 10
    if email or phone:
        target_score += 5
    target_score = min(target_score, 100)
    target_tier = retr_target_tier(target_score)
    bridge_needed = lender_gap and target_tier in ('A', 'B', 'C')

    target = {
        'batch_id': batch_id,
        'source_row': row,
        'full_name': full_name,
        'brokerage': brokerage,
        'email': email,
        'phone': phone,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'primary_zip_codes': zip_codes,
        'agent_type': agent_type,
        'primary_markets': primary_markets,
        'property_mix': property_mix,
        'buyer_volume': buyer_volume,
        'seller_volume': seller_volume,
        'total_volume': total_volume,
        'buyer_units': buyer_units,
        'seller_units': seller_units,
        'total_units': total_units,
        'lender_name': lender_name,
        'dominant_lender': dominant_lender,
        'lender_loyalty_pct': lender_loyalty_pct,
        'has_preferred_lender': has_preferred_lender,
        'lender_loyalty_gap': lender_gap,
        'buyer_score': buyer_score,
        'seller_score': seller_score,
        'target_score': target_score,
        'target_tier': target_tier,
        'team_leader': team_leader,
        'bridge_needed': bridge_needed,
        'web_intel': web_intel,
        'instagram_intel': instagram_intel,
        'status': 'new',
        'notes': '',
    }
    target['draft_outreach'] = build_retr_draft_outreach(target)
    target['battle_plan'] = build_retr_battle_plan(target)
    return target


def insert_retr_target(cur, target):
    cur.execute(
        """
        INSERT INTO retr_realtor_targets (
            batch_id, source_row, full_name, brokerage, email, phone, city, state,
            zip_code, primary_zip_codes, agent_type, primary_markets,
            property_mix,
            buyer_volume, seller_volume, total_volume, buyer_units, seller_units,
            total_units, lender_name, dominant_lender, lender_loyalty_pct,
            has_preferred_lender, lender_loyalty_gap,
            buyer_score, seller_score, target_score, target_tier, team_leader,
            bridge_needed, draft_outreach, battle_plan, web_intel,
            instagram_intel, status, notes
        )
        VALUES (
            %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            target['batch_id'],
            json.dumps(target['source_row']),
            target['full_name'],
            target['brokerage'] or None,
            target['email'] or None,
            target['phone'] or None,
            target['city'] or None,
            target['state'] or None,
            target['zip_code'] or None,
            json.dumps(target['primary_zip_codes']),
            target['agent_type'] or None,
            target['primary_markets'] or None,
            target['property_mix'] or None,
            target['buyer_volume'],
            target['seller_volume'],
            target['total_volume'],
            target['buyer_units'],
            target['seller_units'],
            target['total_units'],
            target['lender_name'] or None,
            target['dominant_lender'] or None,
            target['lender_loyalty_pct'],
            target['has_preferred_lender'],
            target['lender_loyalty_gap'],
            target['buyer_score'],
            target['seller_score'],
            target['target_score'],
            target['target_tier'],
            target['team_leader'],
            target['bridge_needed'],
            target['draft_outreach'],
            target['battle_plan'],
            target['web_intel'] or None,
            target['instagram_intel'] or None,
            target['status'],
            target['notes'],
        ),
    )


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

        ensure_retr_tables(cur)

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
    return send_file(os.path.join(BASE_DIR, 'heloc-calculator.html'),
                     mimetype='text/html')



@app.route('/dpa')
def serve_dpa():
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


def cursor_rows_as_dicts(cur):
    columns = [desc[0] for desc in cur.description] if cur.description else []
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_retr_target(cur, target_id):
    cur.execute("SELECT * FROM retr_realtor_targets WHERE id = %s",
                (target_id, ))
    columns = [desc[0] for desc in cur.description] if cur.description else []
    row = cur.fetchone()
    if not row:
        return None
    target = dict(zip(columns, row))
    if isinstance(target.get('source_row'), str):
        try:
            target['source_row'] = json.loads(target['source_row'])
        except json.JSONDecodeError:
            target['source_row'] = {}
    if isinstance(target.get('primary_zip_codes'), str):
        try:
            target['primary_zip_codes'] = json.loads(target['primary_zip_codes'])
        except json.JSONDecodeError:
            target['primary_zip_codes'] = []
    if isinstance(target.get('call_coach_plan'), str):
        try:
            target['call_coach_plan'] = json.loads(target['call_coach_plan'])
        except json.JSONDecodeError:
            target['call_coach_plan'] = None
    return target


@app.route('/admin/retr-scout')
@login_required
def admin_retr_scout():
    """RETR Realtor Scout dashboard."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        conn.commit()

        tier_filter = request.args.get('tier', '').strip().upper()
        status_filter = request.args.get('status', '').strip()
        search = request.args.get('search', '').strip()
        zip_filter = normalize_retr_zip(request.args.get('zip', '').strip())
        bridge_filter = request.args.get('bridge', '').strip() == '1'

        where = ["1=1"]
        params = []
        if tier_filter in ('A', 'B', 'C', 'D'):
            where.append("target_tier = %s")
            params.append(tier_filter)
        if status_filter in RETR_STATUS_LABELS:
            where.append("status = %s")
            params.append(status_filter)
        if bridge_filter:
            where.append("bridge_needed = TRUE")
        if zip_filter:
            where.append("zip_code = %s")
            params.append(zip_filter)
        if search:
            where.append(
                "(full_name ILIKE %s OR brokerage ILIKE %s OR email ILIKE %s OR city ILIKE %s OR zip_code ILIKE %s OR dominant_lender ILIKE %s)"
            )
            search_param = f"%{search}%"
            params.extend(
                [search_param, search_param, search_param, search_param,
                 search_param, search_param])

        where_sql = " AND ".join(where)
        cur.execute(f"""
            SELECT id, full_name, brokerage, email, phone, city, state,
                   zip_code, agent_type, dominant_lender, lender_loyalty_pct,
                   buyer_score, seller_score, target_score, target_tier,
                   lender_loyalty_gap, team_leader, bridge_needed, status,
                   created_at, updated_at
            FROM retr_realtor_targets
            WHERE {where_sql}
            ORDER BY target_score DESC, updated_at DESC, id DESC
            LIMIT 250
        """, params)
        targets = cursor_rows_as_dicts(cur)

        cur.execute("SELECT COUNT(*) FROM retr_realtor_targets")
        total_targets = cur.fetchone()[0]
        cur.execute("""
            SELECT target_tier, COUNT(*)
            FROM retr_realtor_targets
            GROUP BY target_tier
        """)
        tier_counts = dict(cur.fetchall())
        cur.execute("""
            SELECT status, COUNT(*)
            FROM retr_realtor_targets
            GROUP BY status
        """)
        status_counts = dict(cur.fetchall())
        cur.execute("""
            SELECT COUNT(*)
            FROM retr_realtor_targets
            WHERE lender_loyalty_gap = TRUE
        """)
        gap_count = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(*)
            FROM retr_realtor_targets
            WHERE bridge_needed = TRUE
        """)
        bridge_count = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(DISTINCT zip_code)
            FROM retr_realtor_targets
            WHERE zip_code IS NOT NULL AND zip_code <> ''
        """)
        zip_count = cur.fetchone()[0]
        cur.execute("""
            SELECT filename, imported_rows, created_at
            FROM retr_import_batches
            ORDER BY created_at DESC, id DESC
            LIMIT 5
        """)
        batches = cursor_rows_as_dicts(cur)

        cur.close()
        conn.close()

        flash = session.pop('retr_flash', None)
        return render_template_string(
            RETR_SCOUT_TEMPLATE,
            targets=targets,
            batches=batches,
            total_targets=total_targets,
            tier_counts=tier_counts,
            status_counts=status_counts,
            gap_count=gap_count,
            bridge_count=bridge_count,
            status_options=RETR_STATUS_OPTIONS,
            status_labels=RETR_STATUS_LABELS,
            current_tier=tier_filter,
            current_status=status_filter,
            search_query=search,
            zip_filter=zip_filter,
            bridge_filter=bridge_filter,
            zip_count=zip_count,
            format_money=format_retr_money,
            format_percent=format_retr_percent,
            flash=flash,
        )
    except Exception as e:
        app.logger.error(f"RETR Scout dashboard error: {e}")
        return render_template_string(RETR_ERROR_TEMPLATE,
                                      error=f"RETR Scout error: {e}")


@app.route('/admin/retr-scout/zip-rankings')
@login_required
def admin_retr_zip_rankings():
    """Rank ZIP codes by lender-loyalty opportunity for strategy calls."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        conn.commit()

        cur.execute("""
            SELECT zip_code,
                   COUNT(*) AS target_count,
                   ROUND(AVG(target_score)::numeric, 1) AS avg_target_score,
                   ROUND(AVG(COALESCE(lender_loyalty_pct, 0))::numeric, 1) AS avg_loyalty_pct,
                   SUM(CASE WHEN lender_loyalty_gap THEN 1 ELSE 0 END) AS gap_count,
                   SUM(CASE WHEN bridge_needed THEN 1 ELSE 0 END) AS bridge_count,
                   SUM(CASE WHEN target_tier IN ('A', 'B') THEN 1 ELSE 0 END) AS priority_count,
                   MAX(total_volume) AS top_volume,
                   STRING_AGG(DISTINCT NULLIF(COALESCE(dominant_lender, lender_name), ''), ', ') AS lenders
            FROM retr_realtor_targets
            WHERE zip_code IS NOT NULL AND zip_code <> ''
            GROUP BY zip_code
        """)
        rankings = cursor_rows_as_dicts(cur)
        for row in rankings:
            row['opportunity_score'] = retr_zip_opportunity_score(
                row.get('target_count'),
                row.get('avg_loyalty_pct'),
                row.get('gap_count'),
                row.get('priority_count'),
                row.get('bridge_count'),
            )
        rankings.sort(key=lambda row: (
            row.get('opportunity_score') or 0,
            row.get('gap_count') or 0,
            row.get('priority_count') or 0,
            row.get('target_count') or 0,
        ),
                      reverse=True)
        rankings = rankings[:100]

        cur.execute("""
            SELECT zip_code, id, full_name, brokerage, target_tier, target_score,
                   lender_loyalty_gap, bridge_needed, agent_type
            FROM (
                SELECT zip_code, id, full_name, brokerage, target_tier,
                       target_score, lender_loyalty_gap, bridge_needed,
                       agent_type,
                       ROW_NUMBER() OVER (
                           PARTITION BY zip_code
                           ORDER BY target_score DESC, updated_at DESC, id DESC
                       ) AS row_number
                FROM retr_realtor_targets
                WHERE zip_code IS NOT NULL AND zip_code <> ''
            ) ranked
            WHERE row_number <= 3
            ORDER BY zip_code, target_score DESC, id DESC
        """)
        top_targets_by_zip = {}
        for row in cursor_rows_as_dicts(cur):
            top_targets_by_zip.setdefault(row['zip_code'], []).append(row)

        cur.close()
        conn.close()

        return render_template_string(
            RETR_ZIP_RANKINGS_TEMPLATE,
            rankings=rankings,
            top_targets_by_zip=top_targets_by_zip,
            format_money=format_retr_money,
            format_percent=format_retr_percent,
        )
    except Exception as e:
        app.logger.error(f"RETR ZIP rankings error: {e}")
        return render_template_string(RETR_ERROR_TEMPLATE,
                                      error=f"RETR ZIP ranking error: {e}")


@app.route('/admin/retr-scout/upload', methods=['POST'])
@login_required
def admin_retr_scout_upload():
    """Upload a RETR CSV export and create local scouting targets."""
    conn = None
    try:
        upload = request.files.get('csv_file')
        if not upload or not upload.filename:
            session['retr_flash'] = {
                'type': 'error',
                'message': 'Choose a RETR CSV export before uploading.'
            }
            return redirect(url_for('admin_retr_scout'))

        raw = upload.stream.read()
        text = raw.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            session['retr_flash'] = {
                'type': 'error',
                'message': 'The uploaded file does not look like a CSV export.'
            }
            return redirect(url_for('admin_retr_scout'))

        rows = [
            row for row in reader
            if any((value or '').strip() for value in row.values())
        ]

        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        cur.execute(
            """
            INSERT INTO retr_import_batches (filename, total_rows, imported_rows)
            VALUES (%s, %s, 0)
            RETURNING id
            """, (upload.filename, len(rows)))
        batch_id = cur.fetchone()[0]

        imported = 0
        for row in rows:
            target = build_retr_target(row, batch_id=batch_id)
            insert_retr_target(cur, target)
            imported += 1

        cur.execute(
            """
            UPDATE retr_import_batches
            SET imported_rows = %s
            WHERE id = %s
            """, (imported, batch_id))
        conn.commit()
        cur.close()
        conn.close()

        session['retr_flash'] = {
            'type': 'success',
            'message': f'Imported {imported} RETR scout targets. No outreach was sent.'
        }
        return redirect(url_for('admin_retr_scout'))
    except UnicodeDecodeError:
        session['retr_flash'] = {
            'type': 'error',
            'message': 'Upload failed. Please export the RETR file as UTF-8 CSV.'
        }
        return redirect(url_for('admin_retr_scout'))
    except Exception as e:
        if conn and hasattr(conn, 'rollback'):
            conn.rollback()
        app.logger.error(f"RETR Scout upload error: {e}")
        session['retr_flash'] = {
            'type': 'error',
            'message': f'Upload failed: {e}'
        }
        return redirect(url_for('admin_retr_scout'))


@app.route('/admin/retr-scout/target/<int:target_id>')
@login_required
def admin_retr_target_detail(target_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        conn.commit()
        target = fetch_retr_target(cur, target_id)
        cur.close()
        conn.close()

        if not target:
            return render_template_string(RETR_ERROR_TEMPLATE,
                                          error="RETR target not found"), 404

        flash = session.pop('retr_flash', None)
        return render_template_string(
            RETR_TARGET_DETAIL_TEMPLATE,
            target=target,
            status_options=RETR_STATUS_OPTIONS,
            status_labels=RETR_STATUS_LABELS,
            format_money=format_retr_money,
            format_percent=format_retr_percent,
            flash=flash,
        )
    except Exception as e:
        app.logger.error(f"RETR target detail error: {e}")
        return render_template_string(RETR_ERROR_TEMPLATE,
                                      error=f"RETR target error: {e}")


@app.route('/admin/retr-scout/target/<int:target_id>/status', methods=['POST'])
@login_required
def admin_retr_target_status(target_id):
    try:
        status = request.form.get('status', 'new').strip()
        if status not in RETR_STATUS_LABELS:
            status = 'new'
        notes = request.form.get('notes', '').strip()
        bridge_needed = request.form.get('bridge_needed') == 'on'

        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        cur.execute(
            """
            UPDATE retr_realtor_targets
            SET status = %s, notes = %s, bridge_needed = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """, (status, notes, bridge_needed, target_id))
        conn.commit()
        cur.close()
        conn.close()

        session['retr_flash'] = {
            'type': 'success',
            'message': 'Local RETR Scout status updated.'
        }
        return redirect(url_for('admin_retr_target_detail',
                                target_id=target_id))
    except Exception as e:
        app.logger.error(f"RETR target status error: {e}")
        session['retr_flash'] = {
            'type': 'error',
            'message': f'Status update failed: {e}'
        }
        return redirect(url_for('admin_retr_target_detail',
                                target_id=target_id))


@app.route('/admin/retr-scout/target/<int:target_id>/call-coach/generate',
           methods=['POST'])
@login_required
def admin_retr_call_coach_generate(target_id):
    """Create a local draft-only Call Coach plan for a RETR target."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        ensure_retr_tables(cur)
        target = fetch_retr_target(cur, target_id)
        if not target:
            cur.close()
            conn.close()
            return render_template_string(RETR_ERROR_TEMPLATE,
                                          error="RETR target not found"), 404

        plan = build_retr_call_coach_plan(target)
        cur.execute(
            """
            UPDATE retr_realtor_targets
            SET call_coach_plan = %s::jsonb,
                call_coach_generated_at = CURRENT_TIMESTAMP,
                status = CASE
                    WHEN status = 'new' THEN 'battle_plan_ready'
                    ELSE status
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """, (json.dumps(plan), target_id))
        conn.commit()
        cur.close()
        conn.close()

        session['retr_flash'] = {
            'type': 'success',
            'message': 'Draft-only RETR Call Coach plan generated locally.'
        }
        return redirect(url_for('admin_retr_target_detail',
                                target_id=target_id))
    except Exception as e:
        app.logger.error(f"RETR Call Coach plan error: {e}")
        session['retr_flash'] = {
            'type': 'error',
            'message': f'Call Coach plan generation failed: {e}'
        }
        return redirect(url_for('admin_retr_target_detail',
                                target_id=target_id))


@app.route('/admin/retr-scout/call-coach')
@login_required
def admin_retr_call_coach():
    """Mission Control station for the draft-only RETR Call Coach sub-agent."""
    target_id = request.args.get('target_id', '').strip()
    target = None
    warning = None

    if target_id.isdigit():
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            ensure_retr_tables(cur)
            conn.commit()
            target = fetch_retr_target(cur, int(target_id))
            cur.close()
            conn.close()
        except Exception as e:
            warning = f"Target context could not be loaded: {e}"
            if conn and hasattr(conn, 'close'):
                conn.close()

    return render_template_string(
        RETR_CALL_COACH_TEMPLATE,
        target=target,
        warning=warning,
        skill_path=RETR_CALL_COACH_SKILL_PATH,
        format_percent=format_retr_percent,
    )


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
                <a href="/admin/retr-scout" class="hover:text-gold">RETR Scout</a>
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


RETR_ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RETR Scout Error - Dr.MortgageUSA</title>
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
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-6">
    <div class="bg-white rounded-lg shadow p-6 max-w-xl">
        <h1 class="text-2xl font-bold text-red-700 mb-3">RETR Scout Error</h1>
        <p class="text-gray-700 mb-5">{{ error }}</p>
        <a href="/admin/retr-scout" class="inline-flex bg-navy text-white px-4 py-2 rounded-lg hover:bg-blue-900">Back to RETR Scout</a>
    </div>
</body>
</html>
'''


RETR_SCOUT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RETR Realtor Scout - Dr.MortgageUSA</title>
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
        <div class="container mx-auto flex flex-wrap justify-between items-center gap-3">
            <h1 class="text-2xl font-bold">Dr.MortgageUSA <span class="text-gold">RETR Realtor Scout</span></h1>
            <div class="flex items-center gap-4">
                <a href="/admin/retr-scout/zip-rankings" class="hover:text-gold">ZIP Rankings</a>
                <a href="/admin/dashboard" class="hover:text-gold">Lead Dashboard</a>
                <a href="/" class="hover:text-gold">View Site</a>
                <a href="/admin/logout" class="bg-gold text-navy px-4 py-2 rounded-lg hover:bg-yellow-500">Logout</a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto p-6">
        {% if flash %}
        <div class="mb-5 rounded-lg border px-4 py-3 {% if flash.type == 'success' %}bg-green-50 border-green-200 text-green-800{% else %}bg-red-50 border-red-200 text-red-800{% endif %}">
            {{ flash.message }}
        </div>
        {% endif %}

        <div class="grid lg:grid-cols-[minmax(0,1fr)_320px] gap-6 mb-6">
        <section class="bg-white rounded-lg shadow p-5">
            <div class="flex flex-wrap items-start justify-between gap-5">
                <div>
                    <h2 class="text-xl font-bold text-navy">Scout Imports</h2>
                    <p class="text-sm text-gray-600 mt-1">Draft-only scouting. No DMs, emails, CRM writes, RETR writes, ad changes, or calls are triggered here.</p>
                </div>
                <form method="POST" action="/admin/retr-scout/upload" enctype="multipart/form-data" class="flex flex-wrap items-end gap-3">
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-1">RETR CSV Export</label>
                        <input type="file" name="csv_file" accept=".csv,text/csv" required
                               class="block w-72 max-w-full text-sm text-gray-700 border rounded-lg file:mr-4 file:border-0 file:bg-gray-200 file:px-4 file:py-2 file:text-gray-700">
                    </div>
                    <button type="submit" class="bg-gold text-navy font-bold px-5 py-2 rounded-lg hover:bg-yellow-500">
                        Upload CSV
                    </button>
                </form>
            </div>
            {% if batches %}
            <div class="mt-5 border-t pt-4">
                <div class="text-sm font-semibold text-gray-700 mb-2">Recent batches</div>
                <div class="grid md:grid-cols-5 gap-2 text-sm text-gray-700">
                    {% for batch in batches %}
                    <div class="rounded-lg border p-3">
                        <div class="font-semibold truncate">{{ batch.filename or 'RETR export' }}</div>
                        <div>{{ batch.imported_rows }} targets</div>
                        <div class="text-xs text-gray-500">{{ batch.created_at.strftime('%m/%d/%Y %I:%M %p') if batch.created_at else 'N/A' }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </section>

        <aside class="bg-white rounded-lg shadow p-5">
            <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Mission Control Side Panel</div>
            <h2 class="text-xl font-bold text-navy mt-1">Active Sub-Agents</h2>
            <div class="mt-4 space-y-3">
                <a href="/admin/retr-scout/call-coach" class="block rounded-lg border-2 border-gold bg-yellow-50 p-4 hover:bg-yellow-100">
                    <div class="flex items-center justify-between gap-3">
                        <div class="font-bold text-navy">RETR Call Coach</div>
                        <span class="rounded-full bg-gold px-2 py-1 text-xs font-bold text-navy">Priority</span>
                    </div>
                    <p class="text-sm text-gray-700 mt-2">Pre-call plans, first-touch drafts, mock scripts, and transcript scorecards.</p>
                    <p class="text-xs text-red-700 font-semibold mt-2">Draft-only. No external outreach.</p>
                </a>
                <div class="rounded-lg border p-4">
                    <div class="font-bold text-navy">RETR Scout Assistant</div>
                    <p class="text-sm text-gray-700 mt-2">CSV imports, target scoring, tiers, lender gaps, and local status workflow.</p>
                </div>
                <a href="/admin/retr-scout/zip-rankings" class="block rounded-lg border p-4 hover:bg-gray-50">
                    <div class="font-bold text-navy">ZIP Loyalty Stack</div>
                    <p class="text-sm text-gray-700 mt-2">Rack and stack ZIP codes by loyalty gaps, A/B targets, bridge needs, and production density.</p>
                </a>
            </div>
        </aside>
        </div>

        <section class="grid md:grid-cols-3 lg:grid-cols-7 gap-4 mb-6">
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-navy">{{ total_targets }}</div>
                <div class="text-sm text-gray-600">Total Targets</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-green-700">{{ tier_counts.get('A', 0) }}</div>
                <div class="text-sm text-gray-600">A Tier</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-blue-700">{{ tier_counts.get('B', 0) }}</div>
                <div class="text-sm text-gray-600">B Tier</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-yellow-700">{{ tier_counts.get('C', 0) }}</div>
                <div class="text-sm text-gray-600">C Tier</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-red-700">{{ gap_count }}</div>
                <div class="text-sm text-gray-600">Lender Gaps</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-purple-700">{{ bridge_count }}</div>
                <div class="text-sm text-gray-600">Bridge Needed</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-3xl font-bold text-navy">{{ zip_count }}</div>
                <div class="text-sm text-gray-600">ZIP Markets</div>
            </div>
        </section>

        <section class="bg-white rounded-lg shadow mb-6 p-4">
            <form class="flex flex-wrap gap-4 items-end">
                <div class="flex-1 min-w-[220px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Search</label>
                    <input type="text" name="search" value="{{ search_query }}"
                           placeholder="Name, brokerage, email, or city"
                           class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                </div>
                <div class="min-w-[130px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Tier</label>
                    <select name="tier" class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                        <option value="">All Tiers</option>
                        {% for tier in ['A', 'B', 'C', 'D'] %}
                        <option value="{{ tier }}" {% if current_tier == tier %}selected{% endif %}>{{ tier }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="min-w-[130px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">ZIP</label>
                    <input type="text" name="zip" value="{{ zip_filter }}" maxlength="10"
                           class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                </div>
                <div class="min-w-[190px]">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Status</label>
                    <select name="status" class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                        <option value="">All Statuses</option>
                        {% for value, label in status_options %}
                        <option value="{{ value }}" {% if current_status == value %}selected{% endif %}>{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>
                <label class="flex items-center gap-2 border rounded-lg px-4 py-2 text-sm text-gray-700">
                    <input type="checkbox" name="bridge" value="1" {% if bridge_filter %}checked{% endif %}>
                    Bridge needed
                </label>
                <button type="submit" class="bg-gold text-navy font-bold px-6 py-2 rounded-lg hover:bg-yellow-500">
                    Filter
                </button>
                <a href="/admin/retr-scout" class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300">Clear</a>
            </form>
        </section>

        <section class="bg-white rounded-lg shadow overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-navy text-white">
                        <tr>
                            <th class="px-4 py-3 text-left">Target</th>
                            <th class="px-4 py-3 text-left">Market</th>
                            <th class="px-4 py-3 text-center">ZIP</th>
                            <th class="px-4 py-3 text-center">Tier</th>
                            <th class="px-4 py-3 text-center">Score</th>
                            <th class="px-4 py-3 text-center">Buyer</th>
                            <th class="px-4 py-3 text-center">Seller</th>
                            <th class="px-4 py-3 text-center">Loyalty</th>
                            <th class="px-4 py-3 text-center">Gap</th>
                            <th class="px-4 py-3 text-center">Team</th>
                            <th class="px-4 py-3 text-left">Status</th>
                            <th class="px-4 py-3 text-center">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if targets %}
                        {% for target in targets %}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-3">
                                <div class="font-semibold text-navy">{{ target.full_name }}</div>
                                <div class="text-sm text-gray-600">{{ target.brokerage or 'No brokerage listed' }}</div>
                                <div class="text-xs text-gray-500">{{ target.email or target.phone or 'No contact data' }}</div>
                            </td>
                            <td class="px-4 py-3 text-sm">{{ target.city or 'N/A' }}{% if target.state %}, {{ target.state }}{% endif %}</td>
                            <td class="px-4 py-3 text-center text-sm">
                                {% if target.zip_code %}
                                <a href="/admin/retr-scout?zip={{ target.zip_code }}" class="font-semibold text-navy hover:text-gold">{{ target.zip_code }}</a>
                                {% else %}
                                <span class="text-gray-500">N/A</span>
                                {% endif %}
                            </td>
                            <td class="px-4 py-3 text-center">
                                <span class="inline-flex items-center justify-center w-9 h-9 rounded-lg font-bold
                                    {% if target.target_tier == 'A' %}bg-green-100 text-green-800
                                    {% elif target.target_tier == 'B' %}bg-blue-100 text-blue-800
                                    {% elif target.target_tier == 'C' %}bg-yellow-100 text-yellow-800
                                    {% else %}bg-gray-100 text-gray-700{% endif %}">
                                    {{ target.target_tier }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-center font-semibold">{{ target.target_score }}</td>
                            <td class="px-4 py-3 text-center">{{ target.buyer_score }}</td>
                            <td class="px-4 py-3 text-center">{{ target.seller_score }}</td>
                            <td class="px-4 py-3 text-center text-sm">{{ format_percent(target.lender_loyalty_pct) }}</td>
                            <td class="px-4 py-3 text-center">
                                {% if target.lender_loyalty_gap %}
                                <span class="text-red-700 font-semibold">Gap</span>
                                {% else %}
                                <span class="text-gray-500">No</span>
                                {% endif %}
                            </td>
                            <td class="px-4 py-3 text-center">
                                {% if target.team_leader %}
                                <span class="text-purple-700 font-semibold">Lead</span>
                                {% else %}
                                <span class="text-gray-500">No</span>
                                {% endif %}
                            </td>
                            <td class="px-4 py-3 text-sm">{{ status_labels.get(target.status, target.status or 'New') }}</td>
                            <td class="px-4 py-3 text-center">
                                <a href="/admin/retr-scout/target/{{ target.id }}"
                                   class="bg-navy text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-900">Open</a>
                            </td>
                        </tr>
                        {% endfor %}
                        {% else %}
                        <tr>
                            <td colspan="12" class="px-4 py-8 text-center text-gray-500">
                                No RETR targets found. Upload a CSV export to start scouting.
                            </td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </section>
    </main>
</body>
</html>
'''


RETR_ZIP_RANKINGS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RETR ZIP Rankings - Dr.MortgageUSA</title>
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
        <div class="container mx-auto flex flex-wrap justify-between items-center gap-3">
            <h1 class="text-2xl font-bold">RETR Scout <span class="text-gold">ZIP Loyalty Stack</span></h1>
            <div class="flex items-center gap-4">
                <a href="/admin/retr-scout" class="hover:text-gold">RETR Scout</a>
                <a href="/admin/retr-scout/call-coach" class="hover:text-gold">Call Coach</a>
                <a href="/admin/dashboard" class="hover:text-gold">Lead Dashboard</a>
                <a href="/admin/logout" class="bg-gold text-navy px-4 py-2 rounded-lg hover:bg-yellow-500">Logout</a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto p-6">
        <section class="bg-white rounded-lg shadow p-6 mb-6">
            <div class="flex flex-wrap justify-between gap-4">
                <div>
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Strategy Call Prioritization</div>
                    <h2 class="text-3xl font-bold text-navy mt-1">Rack and Stack ZIP Codes by Lender Loyalty</h2>
                    <p class="text-gray-700 mt-3 max-w-4xl">
                        Opportunity score favors ZIPs with low average lender loyalty, visible lender gaps, A/B targets,
                        bridge-needed targets, and enough target density to justify a focused outreach strategy.
                    </p>
                </div>
                <div class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 max-w-md">
                    Draft-only guardrail: this page ranks strategy-call opportunities only. It does not send outreach,
                    write to RETR, write to CRM, or trigger external automations.
                </div>
            </div>
        </section>

        <section class="bg-white rounded-lg shadow overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-navy text-white">
                        <tr>
                            <th class="px-4 py-3 text-left">Rank</th>
                            <th class="px-4 py-3 text-left">ZIP</th>
                            <th class="px-4 py-3 text-center">Opportunity</th>
                            <th class="px-4 py-3 text-center">Targets</th>
                            <th class="px-4 py-3 text-center">Avg Loyalty</th>
                            <th class="px-4 py-3 text-center">Gaps</th>
                            <th class="px-4 py-3 text-center">A/B</th>
                            <th class="px-4 py-3 text-center">Bridge</th>
                            <th class="px-4 py-3 text-left">Top Targets</th>
                            <th class="px-4 py-3 text-left">Lender Read</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if rankings %}
                        {% for row in rankings %}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-4 font-bold text-navy">#{{ loop.index }}</td>
                            <td class="px-4 py-4">
                                <a href="/admin/retr-scout?zip={{ row.zip_code }}" class="text-lg font-bold text-navy hover:text-gold">{{ row.zip_code }}</a>
                                <div class="text-xs text-gray-500">Top volume {{ format_money(row.top_volume) }}</div>
                            </td>
                            <td class="px-4 py-4 text-center">
                                <span class="inline-flex min-w-14 justify-center rounded-lg bg-yellow-100 px-3 py-2 font-bold text-yellow-900">{{ row.opportunity_score }}</span>
                            </td>
                            <td class="px-4 py-4 text-center font-semibold">{{ row.target_count }}</td>
                            <td class="px-4 py-4 text-center font-semibold {% if row.avg_loyalty_pct < 25 %}text-red-700{% else %}text-gray-800{% endif %}">
                                {{ format_percent(row.avg_loyalty_pct) }}
                            </td>
                            <td class="px-4 py-4 text-center text-red-700 font-semibold">{{ row.gap_count }}</td>
                            <td class="px-4 py-4 text-center font-semibold">{{ row.priority_count }}</td>
                            <td class="px-4 py-4 text-center text-purple-700 font-semibold">{{ row.bridge_count }}</td>
                            <td class="px-4 py-4 text-sm">
                                {% for target in top_targets_by_zip.get(row.zip_code, []) %}
                                <div class="mb-2 last:mb-0">
                                    <a href="/admin/retr-scout/target/{{ target.id }}" class="font-semibold text-navy hover:text-gold">{{ target.full_name }}</a>
                                    <span class="text-gray-500">{{ target.target_tier }}/{{ target.target_score }}</span>
                                    <div class="text-xs text-gray-500">{{ target.brokerage or 'No brokerage' }} · {{ target.agent_type or 'Production unknown' }}</div>
                                </div>
                                {% endfor %}
                            </td>
                            <td class="px-4 py-4 text-sm">
                                <div class="font-semibold text-gray-800">{{ row.lenders or 'No dominant lender listed' }}</div>
                                <div class="text-gray-600 mt-1">
                                    {% if row.avg_loyalty_pct < 25 %}
                                    Low-loyalty ZIP. Good candidate for a strategy-call stack.
                                    {% elif row.gap_count %}
                                    Mixed loyalty with visible gaps. Review bridge paths first.
                                    {% else %}
                                    Loyalty looks more protected. Use niche or overflow positioning.
                                    {% endif %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                        {% else %}
                        <tr>
                            <td colspan="10" class="px-4 py-8 text-center text-gray-500">
                                No ZIP data found yet. Upload a RETR CSV with ZIP or postal-code columns to build the stack.
                            </td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </section>
    </main>
</body>
</html>
'''


RETR_TARGET_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ target.full_name }} - RETR Scout</title>
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
        <div class="container mx-auto flex flex-wrap justify-between items-center gap-3">
            <h1 class="text-2xl font-bold">RETR Scout <span class="text-gold">Target Detail</span></h1>
            <div class="flex items-center gap-4">
                <a href="/admin/retr-scout" class="hover:text-gold">RETR Scout</a>
                <a href="/admin/retr-scout/zip-rankings" class="hover:text-gold">ZIP Rankings</a>
                <a href="/admin/dashboard" class="hover:text-gold">Lead Dashboard</a>
                <a href="/admin/logout" class="bg-gold text-navy px-4 py-2 rounded-lg hover:bg-yellow-500">Logout</a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto p-6">
        {% if flash %}
        <div class="mb-5 rounded-lg border px-4 py-3 {% if flash.type == 'success' %}bg-green-50 border-green-200 text-green-800{% else %}bg-red-50 border-red-200 text-red-800{% endif %}">
            {{ flash.message }}
        </div>
        {% endif %}

        <div class="grid lg:grid-cols-3 gap-6">
            <section class="lg:col-span-2 space-y-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex flex-wrap justify-between gap-4">
                        <div>
                            <h2 class="text-3xl font-bold text-navy">{{ target.full_name }}</h2>
                            <p class="text-gray-600 mt-1">{{ target.brokerage or 'No brokerage listed' }}</p>
                            <p class="text-sm text-gray-500">{{ target.city or 'N/A' }}{% if target.state %}, {{ target.state }}{% endif %}</p>
                            <p class="text-sm text-gray-500">ZIP {{ target.zip_code or 'Unconfirmed' }} · {{ target.agent_type or 'Production unknown' }}</p>
                        </div>
                        <div class="text-right">
                            <div class="inline-flex items-center justify-center w-14 h-14 rounded-lg text-2xl font-bold
                                {% if target.target_tier == 'A' %}bg-green-100 text-green-800
                                {% elif target.target_tier == 'B' %}bg-blue-100 text-blue-800
                                {% elif target.target_tier == 'C' %}bg-yellow-100 text-yellow-800
                                {% else %}bg-gray-100 text-gray-700{% endif %}">
                                {{ target.target_tier }}
                            </div>
                            <div class="text-sm text-gray-600 mt-1">Score {{ target.target_score }}</div>
                        </div>
                    </div>
                    <div class="grid md:grid-cols-5 gap-3 mt-6">
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Buyer Score</div>
                            <div class="text-2xl font-bold text-navy">{{ target.buyer_score }}</div>
                            <div class="text-xs text-gray-500">{{ target.buyer_units or 0 }} units</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Seller Score</div>
                            <div class="text-2xl font-bold text-navy">{{ target.seller_score }}</div>
                            <div class="text-xs text-gray-500">{{ target.seller_units or 0 }} units</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Total Volume</div>
                            <div class="text-2xl font-bold text-navy">{{ format_money(target.total_volume) }}</div>
                            <div class="text-xs text-gray-500">{{ target.total_units or 0 }} total units</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Loyalty</div>
                            <div class="text-2xl font-bold {% if target.lender_loyalty_gap %}text-red-700{% else %}text-navy{% endif %}">{{ format_percent(target.lender_loyalty_pct) }}</div>
                            <div class="text-xs text-gray-500">{{ target.dominant_lender or target.lender_name or 'No lender listed' }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Bridge</div>
                            <div class="text-2xl font-bold {% if target.bridge_needed %}text-red-700{% else %}text-gray-700{% endif %}">
                                {% if target.bridge_needed %}Needed{% else %}Optional{% endif %}
                            </div>
                            <div class="text-xs text-gray-500">Local workflow only</div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-3">Pre-Call Battle Plan</h3>
                    <pre class="whitespace-pre-wrap text-sm leading-6 bg-gray-50 border rounded-lg p-4 text-gray-800">{{ target.battle_plan }}</pre>
                </div>

                {% if target.call_coach_plan %}
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
                        <h3 class="text-xl font-bold text-navy">Generated Call Coach Plan</h3>
                        <span class="rounded-lg bg-yellow-100 text-yellow-900 px-3 py-1 text-sm font-semibold">Draft only</span>
                    </div>
                    <div class="grid md:grid-cols-3 gap-3 mb-4">
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Primary ZIP</div>
                            <div class="font-bold text-navy">{{ target.call_coach_plan.zip_strategy.primary_zip }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Lender Loyalty</div>
                            <div class="font-bold text-navy">{{ format_percent(target.call_coach_plan.zip_strategy.lender_loyalty_pct) }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Generated</div>
                            <div class="font-bold text-navy">{{ target.call_coach_generated_at.strftime('%m/%d/%Y %I:%M %p') if target.call_coach_generated_at else 'Saved' }}</div>
                        </div>
                    </div>
                    <div class="rounded-lg border bg-gray-50 p-4 text-sm text-gray-800">
                        <div class="font-bold text-navy mb-2">ZIP Strategy</div>
                        <p>{{ target.call_coach_plan.zip_strategy.read }}</p>
                        <div class="font-bold text-navy mt-4 mb-2">Call Openers</div>
                        {% for opener in target.call_coach_plan.call_openers %}
                        <p class="mb-2 last:mb-0">{{ opener }}</p>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex flex-wrap justify-between items-center gap-3 mb-3">
                        <h3 class="text-xl font-bold text-navy">Draft Outreach</h3>
                        <span class="rounded-lg bg-yellow-100 text-yellow-900 px-3 py-1 text-sm font-semibold">Draft only</span>
                    </div>
                    <pre class="whitespace-pre-wrap text-sm leading-6 bg-gray-50 border rounded-lg p-4 text-gray-800">{{ target.draft_outreach }}</pre>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-3">Original RETR Row</h3>
                    {% if target.source_row %}
                    <div class="grid md:grid-cols-2 gap-3 text-sm">
                        {% for key, value in target.source_row.items() %}
                        <div class="border rounded-lg p-3">
                            <div class="font-semibold text-gray-700">{{ key }}</div>
                            <div class="text-gray-600 break-words">{{ value or 'N/A' }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-gray-500">No source row was stored for this target.</p>
                    {% endif %}
                </div>
            </section>

            <aside class="space-y-6">
                <div class="bg-white rounded-lg shadow p-6 border-2 border-gold">
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Mission Control Sub-Agent</div>
                    <h3 class="text-xl font-bold text-navy mt-1">RETR Call Coach</h3>
                    <p class="text-sm text-gray-700 mt-2">Use this station for richer battle plans, first-touch playbooks, mock call practice, and post-call transcript scorecards.</p>
                    <p class="text-xs text-red-700 font-semibold mt-3">Draft-only. No DMs, emails, calls, CRM writes, RETR writes, or ad changes.</p>
                    <a href="/admin/retr-scout/call-coach?target_id={{ target.id }}"
                       class="mt-4 inline-flex w-full justify-center bg-gold text-navy font-bold px-5 py-2 rounded-lg hover:bg-yellow-500">
                        Open Call Coach Station
                    </a>
                    <form method="POST" action="/admin/retr-scout/target/{{ target.id }}/call-coach/generate" class="mt-3">
                        <button type="submit" class="w-full bg-navy text-white font-bold px-5 py-2 rounded-lg hover:bg-blue-900">
                            Generate Draft Plan
                        </button>
                    </form>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-4">Workflow</h3>
                    <form method="POST" action="/admin/retr-scout/target/{{ target.id }}/status" class="space-y-4">
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-1">Status</label>
                            <select name="status" class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">
                                {% for value, label in status_options %}
                                <option value="{{ value }}" {% if target.status == value %}selected{% endif %}>{{ label }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <label class="flex items-center gap-2 text-sm text-gray-700">
                            <input type="checkbox" name="bridge_needed" {% if target.bridge_needed %}checked{% endif %}>
                            Bridge needed
                        </label>
                        <div>
                            <label class="block text-sm font-semibold text-gray-700 mb-1">Notes</label>
                            <textarea name="notes" rows="7" class="w-full px-4 py-2 border rounded-lg focus:border-gold focus:outline-none">{{ target.notes or '' }}</textarea>
                        </div>
                        <button type="submit" class="w-full bg-gold text-navy font-bold px-5 py-2 rounded-lg hover:bg-yellow-500">
                            Save Local Status
                        </button>
                    </form>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-3">Signals</h3>
                    <dl class="space-y-3 text-sm">
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Primary ZIP</dt>
                            <dd class="font-semibold text-right">{{ target.zip_code or 'Unconfirmed' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Agent type</dt>
                            <dd class="font-semibold text-right">{{ target.agent_type or 'Production unknown' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Market lens</dt>
                            <dd class="font-semibold text-right">{{ target.primary_markets or 'N/A' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Lender</dt>
                            <dd class="font-semibold text-right">{{ target.lender_name or 'Not listed' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Dominant lender</dt>
                            <dd class="font-semibold text-right">{{ target.dominant_lender or 'Not listed' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Loyalty percent</dt>
                            <dd class="font-semibold text-right">{{ format_percent(target.lender_loyalty_pct) }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Preferred lender</dt>
                            <dd class="font-semibold">{{ 'Yes' if target.has_preferred_lender else 'No' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Loyalty gap</dt>
                            <dd class="font-semibold {% if target.lender_loyalty_gap %}text-red-700{% else %}text-gray-700{% endif %}">{{ 'Yes' if target.lender_loyalty_gap else 'No' }}</dd>
                        </div>
                        <div class="flex justify-between gap-4">
                            <dt class="text-gray-600">Team leader</dt>
                            <dd class="font-semibold {% if target.team_leader %}text-purple-700{% else %}text-gray-700{% endif %}">{{ 'Yes' if target.team_leader else 'No' }}</dd>
                        </div>
                    </dl>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-3">Contact</h3>
                    <div class="space-y-2 text-sm">
                        <div>
                            <div class="text-gray-500">Email</div>
                            <div class="font-semibold break-words">{{ target.email or 'N/A' }}</div>
                        </div>
                        <div>
                            <div class="text-gray-500">Phone</div>
                            <div class="font-semibold">{{ target.phone or 'N/A' }}</div>
                        </div>
                    </div>
                </div>
            </aside>
        </div>
    </main>
</body>
</html>
'''


RETR_CALL_COACH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RETR Call Coach Sub-Agent - Dr.MortgageUSA</title>
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
        <div class="container mx-auto flex flex-wrap justify-between items-center gap-3">
            <h1 class="text-2xl font-bold">Mission Control <span class="text-gold">RETR Call Coach</span></h1>
            <div class="flex items-center gap-4">
                <a href="/admin/retr-scout" class="hover:text-gold">RETR Scout</a>
                <a href="/admin/retr-scout/zip-rankings" class="hover:text-gold">ZIP Rankings</a>
                <a href="/admin/dashboard" class="hover:text-gold">Lead Dashboard</a>
                <a href="/admin/logout" class="bg-gold text-navy px-4 py-2 rounded-lg hover:bg-yellow-500">Logout</a>
            </div>
        </div>
    </nav>

    <main class="container mx-auto p-6">
        {% if warning %}
        <div class="mb-5 rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3 text-yellow-900">
            {{ warning }}
        </div>
        {% endif %}

        <section class="grid lg:grid-cols-[minmax(0,1fr)_340px] gap-6">
            <div class="space-y-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Sub-Agent Station</div>
                    <h2 class="text-3xl font-bold text-navy mt-1">RETR Call Coach Sub-Agent</h2>
                    <p class="text-gray-700 mt-3 max-w-3xl">
                        This is the Mission Control home for the realtor call coach skill. It turns RETR Scout target data into
                        richer call prep, first-touch drafts, objection handling, mock call scripts, and post-call scorecards.
                    </p>
                    <div class="mt-5 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
                        Draft-only guardrail: this station does not send DMs, texts, emails, calls, CRM writes, RETR writes,
                        Zapier actions, ManyChat actions, or ad changes.
                    </div>
                </div>

                {% if target %}
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy">Loaded Target Context</h3>
                    <div class="grid md:grid-cols-6 gap-3 mt-4">
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Target</div>
                            <div class="font-bold text-navy">{{ target.full_name }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Tier</div>
                            <div class="font-bold text-navy">{{ target.target_tier }} / {{ target.target_score }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">ZIP</div>
                            <div class="font-bold text-navy">{{ target.zip_code or 'Unconfirmed' }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Loyalty</div>
                            <div class="font-bold {% if target.lender_loyalty_gap %}text-red-700{% else %}text-gray-700{% endif %}">{{ format_percent(target.lender_loyalty_pct) }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Lender Gap</div>
                            <div class="font-bold {% if target.lender_loyalty_gap %}text-red-700{% else %}text-gray-700{% endif %}">{{ 'Yes' if target.lender_loyalty_gap else 'No' }}</div>
                        </div>
                        <div class="rounded-lg border p-3">
                            <div class="text-sm text-gray-500">Bridge</div>
                            <div class="font-bold {% if target.bridge_needed %}text-red-700{% else %}text-gray-700{% endif %}">{{ 'Needed' if target.bridge_needed else 'Optional' }}</div>
                        </div>
                    </div>
                    <div class="mt-5 flex flex-wrap gap-3">
                        <a href="/admin/retr-scout/target/{{ target.id }}" class="bg-navy text-white px-4 py-2 rounded-lg hover:bg-blue-900">Back to Target</a>
                        <a href="/admin/retr-scout/zip-rankings" class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">Open ZIP Stack</a>
                        <form method="POST" action="/admin/retr-scout/target/{{ target.id }}/call-coach/generate">
                            <button type="submit" class="bg-gold text-navy font-bold px-4 py-2 rounded-lg hover:bg-yellow-500">Generate Draft Plan</button>
                        </form>
                    </div>
                </div>
                {% endif %}

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-xl font-bold text-navy mb-4">What This Sub-Agent Owns Next</h3>
                    <div class="grid md:grid-cols-2 gap-4">
                        <div class="rounded-lg border p-4">
                            <div class="font-bold text-navy">Pre-Call Battle Plans</div>
                            <p class="text-sm text-gray-700 mt-2">Convert RETR Scout data into approach, talking points, objections, mock script, and first-touch drafts.</p>
                        </div>
                        <div class="rounded-lg border p-4">
                            <div class="font-bold text-navy">ZIP Loyalty Strategy</div>
                            <p class="text-sm text-gray-700 mt-2">Use ZIP rankings to prioritize strategy calls where lender loyalty is weakest and production density is strongest.</p>
                        </div>
                        <div class="rounded-lg border p-4">
                            <div class="font-bold text-navy">Post-Call Scorecards</div>
                            <p class="text-sm text-gray-700 mt-2">Score LO-to-realtor transcripts against the coach rubric and generate action items.</p>
                        </div>
                        <div class="rounded-lg border p-4">
                            <div class="font-bold text-navy">Hermes Handoff</div>
                            <p class="text-sm text-gray-700 mt-2">Use Hermes for draft generation, research prompts, review workflow, and approval audit metadata.</p>
                        </div>
                        <div class="rounded-lg border p-4">
                            <div class="font-bold text-navy">Approval Gate</div>
                            <p class="text-sm text-gray-700 mt-2">Keep every draft local until Dennis approves the next step from Mission Control.</p>
                        </div>
                    </div>
                </div>
            </div>

            <aside class="space-y-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Skill Set</div>
                    <h3 class="text-xl font-bold text-navy mt-1">$retr-call-coach</h3>
                    <p class="text-sm text-gray-700 mt-3">Installed for Codex at:</p>
                    <code class="mt-2 block rounded-lg bg-gray-100 p-3 text-xs text-gray-800 break-words">{{ skill_path }}</code>
                    <p class="text-sm text-gray-700 mt-3">Use this skill when building battle plans, scorecards, call scripts, and Hermes RETR Call Coach tasks.</p>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Mission Control Location</div>
                    <h3 class="text-xl font-bold text-navy mt-1">RETR Scout Side Panel</h3>
                    <p class="text-sm text-gray-700 mt-3">Find this under RETR Scout in the right-side Mission Control Agents panel, labeled RETR Call Coach. ZIP Loyalty Stack sits beside it for market prioritization.</p>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-xs uppercase tracking-wide text-gray-500 font-bold">Status</div>
                    <h3 class="text-xl font-bold text-green-700 mt-1">Spawned for Buildout</h3>
                    <p class="text-sm text-gray-700 mt-3">The station now supports persistent draft plan JSON. The next build step is PDF generation and transcript upload workflows.</p>
                </div>
            </aside>
        </section>
    </main>
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
