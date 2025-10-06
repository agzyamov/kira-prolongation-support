#!/usr/bin/env python3
"""
Test correct OECD API endpoints for Turkey CPI data
"""

import requests
import json
import pandas as pd
from io import StringIO

def test_oecd_correct():
    """Test correct OECD API endpoints"""
    
    print("🔍 Testing correct OECD API endpoints...")
    print()
    
    # Test different possible endpoints
    test_urls = [
        # Try stats.oecd.org instead
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12",
        
        # Try different format
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12&format=jsondata",
        
        # Try CSV format
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12&format=csv",
        
        # Try different country code
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12&format=jsondata",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"{i}️⃣ Testing: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success!")
                print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
                print(f"   Response length: {len(response.text)}")
                
                # Try to parse the response
                if 'json' in response.headers.get('Content-Type', ''):
                    try:
                        data = response.json()
                        print(f"   📊 JSON keys: {list(data.keys())}")
                    except:
                        print(f"   📄 Raw response: {response.text[:200]}...")
                else:
                    print(f"   📄 Response preview: {response.text[:200]}...")
                    
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_oecd_correct()
