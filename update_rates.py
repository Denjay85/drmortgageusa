#!/usr/bin/env python3
"""
Automated Mortgage Rate Updater
Fetches current mortgage rates from MortgageNewsDaily.com
Runs daily at 10am EST via scheduled deployment
"""

import re
import requests
from datetime import datetime, timezone
import pytz


MND_URL = "https://www.mortgagenewsdaily.com/mortgage-rates"
MND_PRODUCT_ROWS = {
    'conv30': ('/mortgage-rates/30-year-fixed', '30 Yr. Fixed'),
    'conv15': ('/mortgage-rates/15-year-fixed', '15 Yr. Fixed'),
    'jumbo30': ('/mortgage-rates/30-year-jumbo', '30 Yr. Jumbo'),
    'fha30': ('/mortgage-rates/30-year-fha', '30 Yr. FHA'),
    'va30': ('/mortgage-rates/30-year-va', '30 Yr. VA'),
}


def parse_mnd_snapshot(document):
    """Parse only the dated Mortgage News Daily daily-index table."""
    header = re.search(
        r'<div[^>]+class=["\'][^"\']*last-updated[^"\']*["\'][^>]*>'
        r'\s*as\s+of\s+(\d{1,2}/\d{1,2}/\d{2,4})\s*</div>\s*'
        r'<a[^>]+href=["\']/mortgage-rates/mnd["\'][^>]*>'
        r'\s*Mortgage News Daily\s*</a>',
        document,
        re.IGNORECASE,
    )
    if not header:
        raise ValueError('MND daily-index table was not found')

    next_survey = re.search(
        r'<a[^>]+href=["\']/mortgage-rates/(?:freddie-mac|mba)["\']',
        document[header.end():],
        re.IGNORECASE,
    )
    block_end = (
        header.end() + next_survey.start()
        if next_survey
        else min(len(document), header.end() + 30000)
    )
    daily_table = document[header.end():block_end]

    rates = {}
    for key, (path, label) in MND_PRODUCT_ROWS.items():
        row = re.search(
            rf'<a[^>]+href=["\']{re.escape(path)}["\'][^>]*>'
            rf'\s*{re.escape(label)}\s*</a>\s*</td>\s*'
            r'<td[^>]+class=["\'][^"\']*\brate\b[^"\']*["\'][^>]*>'
            r'\s*(\d{1,2}\.\d{1,3})%\s*</td>',
            daily_table,
            re.IGNORECASE,
        )
        if not row:
            raise ValueError(f'MND daily-index row missing for {label}')
        value = float(row.group(1))
        if not 2.0 <= value <= 15.0:
            raise ValueError(f'MND returned an implausible value for {label}')
        rates[key] = f'{value:.2f}'

    raw_date = header.group(1)
    date_format = '%m/%d/%Y' if len(raw_date.rsplit('/', 1)[-1]) == 4 else '%m/%d/%y'
    as_of_date = datetime.strptime(raw_date, date_format).date()
    return {
        'rates': rates,
        'as_of': as_of_date.isoformat(),
        'source': 'Mortgage News Daily',
        'source_url': MND_URL,
    }


def snapshot_is_fresh(snapshot, now=None, max_age_days=4):
    """Allow weekends and holiday gaps, but reject old or future snapshots."""
    if not snapshot or not snapshot.get('as_of'):
        return False
    today = (now or datetime.now(timezone.utc)).date()
    as_of = datetime.strptime(snapshot['as_of'], '%Y-%m-%d').date()
    age = (today - as_of).days
    return -1 <= age <= max_age_days


def fetch_mnd_snapshot():
    """Fetch the current dated daily index directly from MND."""
    response = requests.get(
        MND_URL,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    )
    response.raise_for_status()
    snapshot = parse_mnd_snapshot(response.text)
    if not snapshot_is_fresh(snapshot):
        raise ValueError(f"MND daily index is stale: {snapshot['as_of']}")
    return snapshot


def fetch_mnd_rates():
    """
    Fetch current mortgage rates from MortgageNewsDaily.com
    Returns dict with rate data
    """
    try:
        snapshot = fetch_mnd_snapshot()
        for key, value in snapshot['rates'].items():
            print(f"  {key}: {value}%")
        return snapshot
    except Exception as e:
        print(f"Error fetching from MND: {e}")

    return {}


def update_html_rates(snapshot):
    """Update the mortgage rates in index.html JavaScript object"""
    rates = snapshot.get('rates', snapshot)
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found")
        return False
    
    as_of = snapshot.get('as_of')
    if as_of:
        date_str = datetime.strptime(as_of, '%Y-%m-%d').strftime('%B %-d, %Y')
    else:
        est = pytz.timezone('US/Eastern')
        date_str = datetime.now(est).strftime("%B %-d, %Y")
    
    updated_count = 0
    
    rate_mappings = [
        ('conv30', 'Conventional 30-Year'),
        ('conv15', 'Conventional 15-Year'),
        ('fha30', 'FHA 30-Year'),
        ('va30', 'VA 30-Year'),
        ('jumbo30', 'Jumbo 30-Year'),
    ]
    
    for key, display_name in rate_mappings:
        if key in rates:
            escaped_name = re.escape(display_name)
            pattern = rf'("{escaped_name}":\s*")[\d.]+%(")'
            replacement = rf'\g<1>{rates[key]}%\2'
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                updated_count += 1
                print(f"  Updated {display_name}: {rates[key]}%")
    
    date_pattern = r'const RATE_UPDATE_DATE = "[^"]+";'
    new_date = f'const RATE_UPDATE_DATE = "{date_str}";'
    content = re.sub(date_pattern, new_date, content)
    print(f"  Updated date: {date_str}")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nTotal rates updated: {updated_count}")
    return updated_count > 0


def main():
    """Main function to fetch rates and update HTML"""
    print("=" * 55)
    print("  Mortgage Rate Updater - Dr.MortgageUSA")
    print("  Source: MortgageNewsDaily.com")
    print("=" * 55)
    
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    print(f"\nRunning at: {now.strftime('%Y-%m-%d %I:%M %p EST')}")
    
    print("\nFetching rates from MortgageNewsDaily.com...")
    snapshot = fetch_mnd_rates()
    
    if snapshot:
        print(f"\nApplying {len(snapshot['rates'])} rates to website...")
        success = update_html_rates(snapshot)
        
        if success:
            print("\n" + "=" * 55)
            print("  SUCCESS: Rates updated from MortgageNewsDaily!")
            print("=" * 55)
        else:
            print("\nWarning: No rates were updated in HTML")
    else:
        print("\nERROR: Could not fetch rates from MortgageNewsDaily")
        print("Website rates unchanged.")
    
    return 0


if __name__ == "__main__":
    exit(main())
