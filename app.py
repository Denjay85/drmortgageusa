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
import requests
import psycopg2
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, send_file, session, redirect, url_for, render_template_string
from flask_compress import Compress
import mimetypes

app = Flask(__name__, static_folder=None)

# Enable gzip compression for all responses
Compress(app)
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'application/javascript', 'application/json']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/6074472/uu7c1t0/"


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
    """Create leads table if it doesn't exist"""
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
    return send_file(os.path.join(os.getcwd(), 'index.html'),
                     mimetype='text/html')



@app.route('/robots.txt')
def serve_robots():
    return send_file(os.path.join(os.getcwd(), 'robots.txt'), mimetype='text/plain')

@app.route('/sitemap.xml')
def serve_sitemap():
    return send_file(os.path.join(os.getcwd(), 'sitemap.xml'), mimetype='application/xml')

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('admin'):
        return redirect(url_for('admin_login'))
    try:
        abs_path = os.path.join(os.getcwd(), path)
        if os.path.isfile(abs_path):
            mimetype, _ = mimetypes.guess_type(abs_path)
            if not mimetype:
                mimetype = 'application/octet-stream'
            return send_file(abs_path, mimetype=mimetype, conditional=True)
    except Exception as e:
        app.logger.error(f'Error serving {path}: {e}')
    return send_file(os.path.join(os.getcwd(), 'index.html'),
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

        cur.execute("UPDATE leads SET zapier_forwarded = %s WHERE id = %s",
                    (zapier_forwarded, lead_id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "lead_id": lead_id})

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


_rate_thread = threading.Thread(target=_rate_update_scheduler, daemon=True)
_rate_thread.start()
print("[Auto-Updater] Started - 2hr weekdays, 6hr weekends, market hours only")


# --- Blog Routes ---
@app.route('/blog')
@app.route('/blog/')
def blog_index():
    return send_from_directory('blog_posts', 'index.html')


@app.route('/blog/<slug>')
def blog_post(slug):
    filename = f"{slug}.html"
    filepath = os.path.join('blog_posts', filename)
    if os.path.exists(filepath):
        return send_from_directory('blog_posts', filename)
    return send_from_directory('.', 'index.html'), 404


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
        return send_file(os.path.join(os.getcwd(), '404.html'),
                         mimetype='text/html'), 404
    except Exception:
        return '<h1>404 - Page Not Found</h1>', 404


@app.errorhandler(500)
def server_error(e):
    try:
        return send_file(os.path.join(os.getcwd(), '404.html'),
                         mimetype='text/html'), 500
    except Exception:
        return '<h1>500 - Server Error</h1>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# deploy v3 static-folder-fix all-sendfile
