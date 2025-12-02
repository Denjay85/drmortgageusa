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
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template_string

app = Flask(__name__, static_folder='.', static_url_path='')
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

def login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('admin'):
        return redirect(url_for('admin_login'))
    if os.path.exists(path):
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')

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
        military_status = data.get('militaryStatus', data.get('military_status', ''))
        property_type = data.get('propertyType', data.get('property_type', ''))
        investor_loan_type = data.get('investorLoanType', data.get('investor_loan_type', ''))
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO leads (first_name, email, phone, segment, price_range, down_payment, 
                             timeline, credit_score, military_status, property_type, investor_loan_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (first_name, email, phone, segment, price_range, down_payment, 
              timeline, credit_score, military_status, property_type, investor_loan_type))
        
        result = cur.fetchone()
        lead_id = result[0] if result else None
        
        zapier_forwarded = False
        try:
            zapier_response = requests.post(ZAPIER_WEBHOOK_URL, json=data, timeout=10)
            if zapier_response.status_code == 200:
                zapier_forwarded = True
        except Exception as e:
            print(f"Zapier forward failed: {e}")
        
        cur.execute("UPDATE leads SET zapier_forwarded = %s WHERE id = %s", (zapier_forwarded, lead_id))
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
        return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Admin not configured")
    
    if secrets.compare_digest(password, admin_pw):
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    
    return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Invalid password")

@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard showing all leads"""
    conn = get_db_connection()
    cur = conn.cursor()
    
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
    columns = [desc[0] for desc in cur.description] if cur.description else []
    leads = [dict(zip(columns, row)) for row in cur.fetchall()]
    
    cur.execute("SELECT COUNT(*) FROM leads")
    count_result = cur.fetchone()
    total_leads = count_result[0] if count_result else 0
    
    cur.execute("SELECT segment, COUNT(*) FROM leads GROUP BY segment")
    segment_counts = dict(cur.fetchall())
    
    cur.close()
    conn.close()
    
    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE, 
        leads=leads, 
        total_leads=total_leads,
        segment_counts=segment_counts,
        current_segment=segment_filter,
        search_query=search
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
                        </tr>
                    </thead>
                    <tbody>
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
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="8" class="px-4 py-8 text-center text-gray-500">
                                No leads found. Quiz submissions will appear here.
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
