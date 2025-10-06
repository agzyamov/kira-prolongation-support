#!/usr/bin/env python3
"""
Test TCMB API key with different approaches
"""

import requests
import json
from datetime import datetime

# Your API key
API_KEY = "wybNTfaObt"

def test_api_key():
    """Test the API key with different endpoints and series codes"""
    
    print(f"🔑 Testing API key: {API_KEY[:8]}...")
    print()
    
    # Test 1: Basic connectivity
    print("1️⃣ Testing basic connectivity...")
    try:
        response = requests.get("https://evds2.tcmb.gov.tr/", timeout=10)
        print(f"   ✅ TCMB website accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ TCMB website not accessible: {e}")
    
    # Test 2: API key validation endpoint
    print("\n2️⃣ Testing API key validation...")
    try:
        # Try to get available series
        url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
        params = {
            "key": API_KEY,
            "type": "json",
            "code": "TP.FG.J0",  # TÜFE series
            "startDate": "01-01-2024",
            "endDate": "31-12-2024",
            "aggregationTypes": "avg"
        }
        
        response = requests.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API key works! Response keys: {list(data.keys())}")
            if "items" in data:
                print(f"   📊 Found {len(data['items'])} data points")
        else:
            print(f"   ❌ API error: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Try different series codes
    print("\n3️⃣ Testing different TÜFE series codes...")
    series_codes = [
        "TP.FG.J0",    # Consumer Price Index
        "TP.FG.J1",    # Alternative TÜFE code
        "TP.FG.J2",    # Another alternative
        "TP.FG.J3",    # Another alternative
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
            
            response = requests.get(url, params=params, timeout=10)
            print(f"   {code}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "items" in data and data["items"]:
                    print(f"      ✅ Found data: {len(data['items'])} points")
                else:
                    print(f"      ⚠️  No data in response")
            else:
                print(f"      ❌ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   {code}: ❌ {e}")
    
    # Test 4: Try to get series list
    print("\n4️⃣ Testing series list endpoint...")
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response structure: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"   Error response: {response.text[:300]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_key()
