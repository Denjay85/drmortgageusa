#!/usr/bin/env python3
"""
Automated Mortgage Rate Updater
Fetches current mortgage rates from MortgageNewsDaily.com
Runs daily at 10am EST via scheduled deployment
"""

import re
import requests
from datetime import datetime
import pytz

def fetch_mnd_rates():
    """
    Fetch current mortgage rates from MortgageNewsDaily.com
    Returns dict with rate data
    """
    rates = {}
    
    try:
        response = requests.get(
            "https://www.mortgagenewsdaily.com/mortgage-rates",
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )
        
        if response.status_code == 200:
            content = response.text
            
            match = re.search(r'30 Yr\. Fixed.*?(\d+\.\d+)%', content, re.DOTALL)
            if match:
                rates['conv30'] = match.group(1)
                print(f"  30 Yr Fixed: {match.group(1)}%")
            
            match = re.search(r'15 Yr\. Fixed.*?(\d+\.\d+)%', content, re.DOTALL)
            if match:
                rates['conv15'] = match.group(1)
                print(f"  15 Yr Fixed: {match.group(1)}%")
            
            match = re.search(r'30 Yr\. Jumbo.*?(\d+\.\d+)%', content, re.DOTALL)
            if match:
                rates['jumbo30'] = match.group(1)
                print(f"  30 Yr Jumbo: {match.group(1)}%")
            
            match = re.search(r'30 Yr\. FHA.*?(\d+\.\d+)%', content, re.DOTALL)
            if match:
                rates['fha30'] = match.group(1)
                print(f"  30 Yr FHA: {match.group(1)}%")
            
            match = re.search(r'30 Yr\. VA.*?(\d+\.\d+)%', content, re.DOTALL)
            if match:
                rates['va30'] = match.group(1)
                print(f"  30 Yr VA: {match.group(1)}%")
        else:
            print(f"MND returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching from MND: {e}")
    
    return rates


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
    
    if 'conv30' in rates:
        usda_estimate = str(round(float(rates['conv30']) - 0.47, 2))
        pattern = r'("USDA 30-Year":\s*")[\d.]+%(")'
        replacement = rf'\g<1>{usda_estimate}%\2'
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            print(f"  Updated USDA 30-Year: {usda_estimate}% (estimated)")
    
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
    rates = fetch_mnd_rates()
    
    if rates:
        print(f"\nApplying {len(rates)} rates to website...")
        success = update_html_rates(rates)
        
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
