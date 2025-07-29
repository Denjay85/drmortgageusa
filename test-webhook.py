#!/usr/bin/env python3
"""Test Zapier webhook to verify it's working"""
import requests
import json

# Test data matching what the form sends
test_data = {
    'email': 'test@example.com',
    'phone': '555-1234',
    'segment': 'credit',
    'firstName': 'TestUser',
    'timeline': '1-3-months',
    'hurdle': 'credit-score'
}

webhook_url = 'https://hooks.zapier.com/hooks/catch/6074472/uu7c1t0/'

print("Testing Zapier webhook...")
print(f"URL: {webhook_url}")
print(f"Data: {json.dumps(test_data, indent=2)}")

try:
    # Send as form-encoded data (same as browser)
    response = requests.post(webhook_url, data=test_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Webhook test successful!")
    else:
        print("\n✗ Webhook test failed!")
        
except Exception as e:
    print(f"\nError: {str(e)}")