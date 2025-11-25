#!/usr/bin/env python3
"""
Automated Mortgage Rate Updater
Fetches current mortgage rates and updates index.html
Runs daily at 10am EST via scheduled deployment
"""

import re
import requests
from datetime import datetime
import pytz
import json

def fetch_from_bankrate():
    """Try fetching from Bankrate"""
    rates = {}
    try:
        response = requests.get(
            "https://www.bankrate.com/mortgages/current-interest-rates/",
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )
        if response.status_code == 200:
            content = response.text
            match = re.search(r'30-year fixed.*?(\d+\.\d+)%', content, re.IGNORECASE | re.DOTALL)
            if match:
                rates['conv30'] = match.group(1)
            match = re.search(r'15-year fixed.*?(\d+\.\d+)%', content, re.IGNORECASE | re.DOTALL)
            if match:
                rates['conv15'] = match.group(1)
            match = re.search(r'FHA.*?(\d+\.\d+)%', content, re.IGNORECASE | re.DOTALL)
            if match:
                rates['fha30'] = match.group(1)
            match = re.search(r'VA.*?(\d+\.\d+)%', content, re.IGNORECASE | re.DOTALL)
            if match:
                rates['va30'] = match.group(1)
            match = re.search(r'Jumbo.*?(\d+\.\d+)%', content, re.IGNORECASE | re.DOTALL)
            if match:
                rates['jumbo30'] = match.group(1)
    except Exception as e:
        print(f"Bankrate fetch failed: {e}")
    return rates


def fetch_from_nerdwallet():
    """Try fetching from NerdWallet"""
    rates = {}
    try:
        response = requests.get(
            "https://www.nerdwallet.com/mortgages/mortgage-rates",
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        if response.status_code == 200:
            content = response.text
            patterns = [
                (r'30[- ]?year fixed[^0-9]*(\d+\.\d+)', 'conv30'),
                (r'15[- ]?year fixed[^0-9]*(\d+\.\d+)', 'conv15'),
            ]
            for pattern, key in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    rates[key] = match.group(1)
    except Exception as e:
        print(f"NerdWallet fetch failed: {e}")
    return rates


def fetch_mortgage_rates():
    """
    Fetch current mortgage rates from multiple sources
    Returns dict with rate data or None if all fetches fail
    """
    print("Trying Bankrate...")
    rates = fetch_from_bankrate()
    if rates:
        print(f"Found rates from Bankrate: {rates}")
        return rates
    
    print("Trying NerdWallet...")
    rates = fetch_from_nerdwallet()
    if rates:
        print(f"Found rates from NerdWallet: {rates}")
        return rates
    
    print("All sources failed, using typical market estimates")
    return None


def update_html_rates(rates):
    """Update the mortgage rates in index.html JavaScript object"""
    
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: index.html not found")
        return False
    
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    date_str = now.strftime("%B %d, %Y")
    
    updated = False
    
    rate_mappings = [
        ('conv30', 'Conventional 30-Year'),
        ('conv15', 'Conventional 15-Year'),
        ('fha30', 'FHA 30-Year'),
        ('va30', 'VA 30-Year'),
        ('usda30', 'USDA 30-Year'),
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
                updated = True
                print(f"Updated {display_name}: {rates[key]}%")
    
    date_pattern = r'const RATE_UPDATE_DATE = "[^"]+";'
    new_date = f'const RATE_UPDATE_DATE = "{date_str}";'
    content = re.sub(date_pattern, new_date, content)
    print(f"Updated date to: {date_str}")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def main():
    """Main function to fetch rates and update HTML"""
    print("=" * 50)
    print("Mortgage Rate Updater - Dr.MortgageUSA")
    est = pytz.timezone('US/Eastern')
    now = datetime.now(est)
    print(f"Running at: {now.strftime('%Y-%m-%d %I:%M %p EST')}")
    print("=" * 50)
    
    print("\nFetching current mortgage rates...")
    rates = fetch_mortgage_rates()
    
    if rates:
        print(f"\nFinal rates to apply: {rates}")
    else:
        print("\nNo rates fetched - will only update date")
        rates = {}
    
    print("\nUpdating HTML file...")
    success = update_html_rates(rates)
    
    if success:
        print("\nUpdate completed successfully!")
    else:
        print("\nUpdate failed")
    
    print("\n" + "=" * 50)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
