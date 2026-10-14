"""Same-origin bridge to Dennis's existing guide-backed answer engine.

The interface is built and hosted by drmortgageusa.com. Only the public answer
API is bridged; this is not an open proxy. Main-site login cookies, bearer
headers, visitor IP addresses and arbitrary upstream URLs are never forwarded.
"""
import re
from urllib.parse import urlsplit

import requests
from flask import Blueprint, current_app, jsonify, request

blueprint = Blueprint('ask_mortgage', __name__)
ENGINE_ORIGIN = 'https://ask-dr-mortgage.denjay85.chatgpt.site'
COOKIE_NAME = 'dm_conversation'
COOKIE_PATH = '/api/ask-dr-mortgage'
ALLOWED_METHODS = {
    'library': {'GET'},
    'search': {'GET'},
    'conversation': {'GET', 'POST', 'DELETE'},
    'ask': {'POST'},
    'feedback': {'POST'},
    'events': {'POST'},
}
PUBLIC_ORIGINS = {'https://drmortgageusa.com', 'https://www.drmortgageusa.com'}


def _error(message, status):
    response = jsonify(error=message)
    response.status_code = status
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


def _same_origin_write():
    origin = request.headers.get('Origin', '')
    if origin in PUBLIC_ORIGINS:
        return True
    # Local QA only. Never accept arbitrary request-host origins in production.
    if current_app.testing or current_app.config.get('PREVIEW_MODE'):
        parts = urlsplit(origin)
        return parts.scheme in {'http', 'https'} and parts.hostname in {'localhost', '127.0.0.1'}
    return False


@blueprint.route('/api/ask-dr-mortgage/<endpoint>', methods=['GET', 'POST', 'DELETE'])
def engine_api(endpoint):
    methods = ALLOWED_METHODS.get(endpoint)
    if methods is None:
        return _error('This answer-service endpoint is not available.', 404)
    if request.method not in methods:
        return _error('This method is not supported.', 405)
    if request.method in {'POST', 'DELETE'} and not _same_origin_write():
        return _error('Please submit this request from DR. Mortgage USA.', 403)
    if (request.content_length is not None and request.content_length > 65536) or len(request.get_data(cache=True)) > 65536:
        return _error('Please shorten your question or conversation.', 413)

    payload = None
    if request.method == 'POST' and endpoint != 'conversation':
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error('Please send a valid question request.', 400)
        if endpoint == 'ask':
            question = payload.get('question')
            if not isinstance(question, str) or not question.strip() or len(question) > 1200:
                return _error('Please enter a question of 1 to 1,200 characters.', 400)
            history = payload.get('history', [])
            if not isinstance(history, list) or len(history) > 5:
                return _error('Please start a new conversation and try again.', 400)

    params = None
    if endpoint == 'search':
        query = request.args.get('q', '')
        if len(query) > 1200:
            return _error('Please shorten your search.', 400)
        params = {'q': query}
    # Do not pass arbitrary queries, headers, session or authentication cookies.
    cookie = request.cookies.get(COOKIE_NAME, '')
    cookies = {}
    if cookie and re.fullmatch(r'[A-Za-z0-9_.=-]{1,1024}', cookie):
        cookies[COOKIE_NAME] = cookie
    try:
        upstream = requests.request(
            request.method, ENGINE_ORIGIN + '/api/' + endpoint,
            json=payload, params=params, cookies=cookies,
            headers={'Accept': 'application/json', 'Origin': ENGINE_ORIGIN,
                     'User-Agent': 'DRMortgageUSA-AnswerBridge/1.0'},
            timeout=(5, 20 if endpoint == 'ask' else 15),
            allow_redirects=False,
        )
        # Never send raw upstream HTML, redirects, infrastructure headers or
        # exception text to the browser. Only the documented JSON API survives.
        if not 200 <= upstream.status_code < 500 or 300 <= upstream.status_code < 400:
            return _error('The answer service is temporarily unavailable. Please try again.', 502)
        if not upstream.headers.get('Content-Type', '').lower().startswith('application/json'):
            return _error('The answer service returned an unexpected response. Please try again.', 502)
        data = upstream.json()
        response = jsonify(data)
        response.status_code = upstream.status_code
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # The only cookie that can cross this boundary belongs to this tool.
        for item in upstream.cookies:
            if item.name == COOKIE_NAME:
                if item.value:
                    response.set_cookie(COOKIE_NAME, item.value, max_age=7 * 86400,
                                        path=COOKIE_PATH, secure=True,
                                        httponly=True, samesite='Lax')
                else:
                    response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH,
                                           secure=True, httponly=True, samesite='Lax')
        if request.method == 'DELETE' and endpoint == 'conversation' and upstream.ok:
            response.delete_cookie(COOKIE_NAME, path=COOKIE_PATH,
                                   secure=True, httponly=True, samesite='Lax')
        return response
    except (requests.RequestException, ValueError):
        # No private question, cookie or upstream error details in logs.
        current_app.logger.warning('Ask Dr. Mortgage answer service unavailable (%s)', endpoint)
        return _error('The answer service is temporarily unavailable. Please try again.', 502)
