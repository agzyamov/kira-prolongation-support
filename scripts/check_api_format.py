#!/usr/bin/env python3
"""
Check TCMB EVDS API format and try different approaches
"""

import requests
import json
from datetime import datetime

# Your API key
API_KEY = "wybNTfaObt"

def test_different_formats():
    """Test different API formats and endpoints"""
    
    print(f"🔑 Testing API key: {API_KEY[:8]}...")
    print()
    
    # Test 1: Check if the API key format is correct
    print("1️⃣ Testing API key format...")
    print(f"   Key length: {len(API_KEY)}")
    print(f"   Key format: {API_KEY}")
    print(f"   Expected: Usually 8-20 characters, alphanumeric")
    print()
    
    # Test 2: Try different base URLs
    print("2️⃣ Testing different base URLs...")
    base_urls = [
        "https://evds2.tcmb.gov.tr/service/evds/seriesData",
        "https://evds2.tcmb.gov.tr/service/evds/seriesData/",
        "https://evds2.tcmb.gov.tr/service/evds/",
        "https://evds2.tcmb.gov.tr/service/evds/seriesData.json",
    ]
    
    for url in base_urls:
        try:
            params = {
                "key": API_KEY,
                "type": "json",
                "code": "TP.FG.J0",
                "startDate": "01-01-2024",
                "endDate": "31-12-2024"
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   {url}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Success!")
                data = response.json()
                print(f"      Response keys: {list(data.keys())}")
                if "items" in data:
                    print(f"      Items count: {len(data['items'])}")
            elif response.status_code == 403:
                print(f"      ❌ Forbidden - API key issue")
            else:
                print(f"      ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   {url}: ❌ {e}")
    
    print()
    
    # Test 3: Try different parameter formats
    print("3️⃣ Testing different parameter formats...")
    
    # Format 1: Standard format
    print("   Format 1: Standard parameters")
    try:
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",
            "startDate": "01-01-2024",
            "endDate": "31-12-2024"
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
    except Exception as e:
        print(f"      Error: {e}")
    
    # Format 2: With aggregationTypes
    print("   Format 2: With aggregationTypes")
    try:
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",
            "startDate": "01-01-2024",
            "endDate": "31-12-2024",
            "aggregationTypes": "avg"
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
    except Exception as e:
        print(f"      Error: {e}")
    
    # Format 3: With formulas
    print("   Format 3: With formulas")
    try:
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",
            "startDate": "01-01-2024",
            "endDate": "31-12-2024",
            "formulas": "0"
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"      Status: {response.status_code}")
        
    except Exception as e:
        print(f"      Error: {e}")
    
    # Format 4: Different series codes
    print("   Format 4: Different series codes")
    series_codes = [
        "TP.FG.J0",    # Consumer Price Index
        "TP.FG.J1",    # Alternative
        "TP.FG.J2",    # Alternative
        "TP.FG.J3",    # Alternative
        "TP.FG.J4",    # Alternative
    ]
    
    for code in series_codes:
        try:
            url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
            params = {
                "key": API_KEY,
                "type": "json",
                "code": code,
                "startDate": "01-01-2024",
                "endDate": "31-12-2024"
            }
            
            response = requests.get(url, params=params, timeout=5)
            print(f"      {code}: {response.status_code}")
            
        except Exception as e:
            print(f"      {code}: ❌ {e}")
    
    print()
    
    # Test 4: Check if we need authentication headers
    print("4️⃣ Testing with different headers...")
    try:
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",
            "startDate": "01-01-2024",
            "endDate": "31-12-2024"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"   With headers: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Success with headers!")
        elif response.status_code == 403:
            print(f"      ❌ Still forbidden with headers")
        else:
            print(f"      ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 5: Check the actual error response
    print("5️⃣ Analyzing error response...")
    try:
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",
            "startDate": "01-01-2024",
            "endDate": "31-12-2024"
        }
        
        response = requests.get(url, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        print(f"   Response length: {len(response.text)}")
        
        if response.status_code == 403:
            print(f"   Error content preview: {response.text[:200]}...")
            
            # Check if it's an HTML error page
            if "html" in response.headers.get('Content-Type', '').lower():
                print(f"   ❌ This is an HTML error page, not a JSON API response")
                print(f"   This suggests the API key is invalid or the endpoint is wrong")
            else:
                print(f"   Response might be JSON: {response.text[:100]}...")
                
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_different_formats()
