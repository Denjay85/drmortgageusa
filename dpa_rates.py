"""Complete official DPA sheets, refreshed off the visitor request path."""
import copy
import html as html_lib
import json
import logging
import os
from pathlib import Path
import re
import tempfile
import threading
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

LOGGER = logging.getLogger(__name__)
SEED_PATH = Path(__file__).with_name('dpa-rate-snapshot.json')

DPA_RATE_SOURCE = 'https://www.ehousingplus.com/homeownership/florida-housing-finance-corporation/program-highlights/'
DPA_SECTION_SPECS = (
    ('heroes-bond', '2026 HOMETOWN HEROES PROGRAM - BOND', (2, 3, 4)),
    ('heroes-tba', '2026 HOMETOWN HEROES PROGRAM - TBA', (2, 3, 4)),
    ('standard-bond', 'STANDARD BOND', (2, 3, 4)),
    ('standard-tba', 'STANDARD TBA', (2, 3, 4)),
    ('plus-tba', 'PLUS TBA', (2, 3, 4, 5, 6, 7)),
)


def _dpa_cells(document):
    cells = {}
    for cell_id, raw_value in re.findall(
        r'data-cell-id=["\']([A-Z]+\d+)["\'][^>]*>(.*?)</t[dh]>',
        document,
        re.IGNORECASE | re.DOTALL,
    ):
        value = re.sub(r'<br\s*/?\s*>', ' ', raw_value, flags=re.IGNORECASE)
        value = re.sub(r'<[^>]+>', ' ', value)
        cells[cell_id.upper()] = re.sub(r'\s+', ' ', html_lib.unescape(value)).strip()
    return cells


def _dpa_cell(cells, cell_id):
    return cells.get(cell_id.upper(), '')


def _dpa_section_row(cells, expected_title):
    for cell_id, value in cells.items():
        if not cell_id.startswith('A'):
            continue
        if value.upper() == expected_title:
            match = re.search(r'\d+$', cell_id)
            if match:
                return int(match.group(0))
    raise ValueError(f'Official DPA section not found: {expected_title}')


def _dpa_rate(cells, row):
    value = _dpa_cell(cells, f'G{row}')
    match = re.search(r'(?:\d+\.\d+%|n/a)', value, re.IGNORECASE)
    if not match:
        raise ValueError(f'Official DPA rate missing from G{row}')
    return match.group(0).upper()


def sheet_date(snapshot):
    return datetime.strptime(snapshot['asOf'], '%B %d, %Y').date()


def validate_snapshot(snapshot):
    today = datetime.now(ZoneInfo('America/New_York')).date()
    if sheet_date(snapshot) > today:
        raise ValueError('Official DPA sheet is future dated')
    if snapshot.get('source') != DPA_RATE_SOURCE or not snapshot.get('heroesFunding'):
        raise ValueError('Official DPA source/funding missing')
    groups = {group['id']: group for group in snapshot['groups']}
    for group_id, _, offsets in DPA_SECTION_SPECS:
        entries = groups[group_id]['entries']
        if len(entries) != len(offsets):
            raise ValueError(f'Incomplete DPA offerings for {group_id}')
        for entry in entries:
            if not re.fullmatch(r'(?:\d+\.\d+%|N/A)', entry['rate']):
                raise ValueError('Invalid DPA rate')
    return snapshot


def parse_snapshot(document):
    # Work on an independent copy; partial/malformed sheets never enter the cache.
    snapshot = json.loads(SEED_PATH.read_text())['snapshot']
    cells = _dpa_cells(document)
    date_match = re.search(
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
        _dpa_cell(cells, 'A1'),
    )
    if not date_match or not _dpa_cell(cells, 'A2'):
        raise ValueError('Official DPA date/funding missing')
    snapshot['asOf'] = date_match.group(0)
    snapshot['notice'] = snapshot['heroesFunding'] = _dpa_cell(cells, 'A2')
    groups = {group['id']: group for group in snapshot['groups']}
    for group_id, heading, offsets in DPA_SECTION_SPECS:
        group = groups[group_id]
        row = _dpa_section_row(cells, heading)
        for entry, offset in zip(group['entries'], offsets):
            entry['rate'] = _dpa_rate(cells, row + offset)
        fico = _dpa_cell(cells, f'D{row + 2}')
        assistance = _dpa_cell(cells, f'E{row + 2}')
        if not fico or (group_id != 'plus-tba' and not assistance):
            raise ValueError(f'Official DPA eligibility missing: {heading}')
        group['fico'] = f'{fico} minimum program score'
        if group_id != 'plus-tba':
            group['assistance'] = assistance.replace('(Max ', '(max ')
    return validate_snapshot(snapshot)


class DpaRateCache:
    """Serve promptly, refresh once per worker, retain complete last-known-good data."""
    def __init__(self, cache_path=None):
        self.path = Path(cache_path or os.environ.get(
            'DPA_RATE_CACHE_PATH', '/tmp/drmortgageusa-dpa-rates.json'))
        self.lock = threading.Lock()
        self.record = json.loads(SEED_PATH.read_text())
        validate_snapshot(self.record['snapshot'])
        try:
            saved = json.loads(self.path.read_text())
            validate_snapshot(saved['snapshot'])
            datetime.fromisoformat(saved['syncedAt'])
            if (sheet_date(saved['snapshot']), saved['syncedAt']) > (
                    sheet_date(self.record['snapshot']), self.record['syncedAt']):
                self.record = saved
        except (OSError, ValueError, KeyError, TypeError):
            pass
        self.refreshing = False
        self.last_success = None
        self.next_attempt = 0.0
        self.error = None

    def refresh(self):
        """Executed in a background thread; never tie up a Gunicorn request."""
        error = None
        try:
            for attempt in range(2):
                try:
                    response = requests.get(DPA_RATE_SOURCE, timeout=(8, 45),
                                            headers={'User-Agent': 'DRMortgageUSA/2026'})
                    response.raise_for_status()
                    snapshot = parse_snapshot(response.text)
                    with self.lock:
                        if sheet_date(snapshot) < sheet_date(self.record['snapshot']):
                            raise ValueError('Official DPA sheet regressed; retaining newer verified sheet')
                    record = {'snapshot': snapshot, 'syncedAt': datetime.now(timezone.utc).isoformat()}
                    # Atomic persistence survives worker restarts. Failure to persist
                    # does not discard a successfully verified in-memory sheet.
                    try:
                        self.path.parent.mkdir(parents=True, exist_ok=True)
                        with tempfile.NamedTemporaryFile(mode='w', dir=self.path.parent,
                                                         delete=False, prefix='.dpa-') as handle:
                            temporary = Path(handle.name)
                            json.dump(record, handle)
                        try:
                            os.replace(temporary, self.path)
                        finally:
                            temporary.unlink(missing_ok=True)
                    except OSError as exc:
                        LOGGER.warning('Could not persist DPA sheet: %s', exc)
                    with self.lock:
                        self.record = record
                        self.last_success = time.monotonic()
                    return
                except requests.RequestException as exc:
                    if attempt == 1:
                        raise
                    time.sleep(2)
        except Exception as exc:
            error = str(exc)
            LOGGER.warning('DPA source refresh deferred; retaining verified sheet: %s', exc)
        finally:
            with self.lock:
                self.error = error
                self.next_attempt = time.monotonic() + (60 if error else 300)
                self.refreshing = False

    def payload(self, force=False):
        with self.lock:
            now = time.monotonic()
            refresh_due = now >= self.next_attempt or (force and self.error is None
                and self.last_success is not None and now - self.last_success >= 60)
            if not self.refreshing and refresh_due:
                self.refreshing = True
                threading.Thread(target=self.refresh, daemon=True, name='dpa-source-refresh').start()
            record = copy.deepcopy(self.record)
            age = (datetime.now(ZoneInfo('America/New_York')).date() - sheet_date(record['snapshot'])).days
            stale = age > 4
            live = (not stale and self.error is None and self.last_success is not None
                    and now - self.last_success < 900)
            return {**record, 'live': live, 'stale': stale, 'refreshing': self.refreshing,
                    'status': 'verified' if live else ('stale' if stale else 'last_verified')}
