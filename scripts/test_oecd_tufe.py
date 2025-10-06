#!/usr/bin/env python3
"""
Test OECD SDMX API for Turkey TÜFE (CPI) data
"""

import requests
import json
import pandas as pd
from io import StringIO
from datetime import datetime

def test_oecd_api():
    """Test OECD SDMX API for Turkey CPI data"""
    
    print("🔍 Testing OECD SDMX API for Turkey TÜFE data...")
    print()
    
    # Test different OECD API endpoints for Turkey CPI
    test_urls = [
        # Format 1: Basic CPI data
        "https://sdmx.oecd.org/public/rest/data/OECD.CPI.M.TUR?startPeriod=2020-01&endPeriod=2024-12&format=json",
        
        # Format 2: With more specific parameters
        "https://sdmx.oecd.org/public/rest/data/OECD.CPI.M.TUR?startPeriod=2024-01&endPeriod=2024-12&format=json",
        
        # Format 3: CSV format
        "https://sdmx.oecd.org/public/rest/data/OECD.CPI.M.TUR?startPeriod=2024-01&endPeriod=2024-12&format=csv",
        
        # Format 4: Try different dataset codes
        "https://sdmx.oecd.org/public/rest/data/OECD.PRICES.TUR?startPeriod=2024-01&endPeriod=2024-12&format=json",
        
        # Format 5: Try without version
        "https://sdmx.oecd.org/public/rest/data/OECD.CPI.TUR?startPeriod=2024-01&endPeriod=2024-12&format=json",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"{i}️⃣ Testing URL: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success!")
                
                # Try to parse as JSON first
                try:
                    data = response.json()
                    print(f"   📊 JSON Response keys: {list(data.keys())}")
                    
                    # Look for data in the response
                    if "data" in data:
                        print(f"   📈 Data points: {len(data['data'])}")
                        
                        # Show first few data points
                        if data["data"]:
                            print(f"   📅 Sample data:")
                            for item in data["data"][:3]:
                                print(f"      {item}")
                    
                except json.JSONDecodeError:
                    # Try as CSV
                    try:
                        df = pd.read_csv(StringIO(response.text))
                        print(f"   📊 CSV Response shape: {df.shape}")
                        print(f"   📈 Columns: {list(df.columns)}")
                        
                        if not df.empty:
                            print(f"   📅 Sample data:")
                            print(df.head(3).to_string())
                            
                    except Exception as e:
                        print(f"   ⚠️  Could not parse as CSV: {e}")
                        print(f"   📄 Raw response preview: {response.text[:200]}...")
                
            elif response.status_code == 404:
                print(f"   ❌ Not found - dataset might not exist")
            elif response.status_code == 400:
                print(f"   ❌ Bad request - check parameters")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test 6: Try to get dataset structure
    print("6️⃣ Testing dataset structure...")
    try:
        url = "https://sdmx.oecd.org/public/rest/dataflow/OECD"
        response = requests.get(url, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success! Available datasets:")
            # This would show available datasets
            print(f"   Response length: {len(response.text)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 7: Try alternative Turkey country codes
    print("7️⃣ Testing alternative Turkey country codes...")
    country_codes = ["TUR", "TR", "TURKEY"]
    
    for country in country_codes:
        try:
            url = f"https://sdmx.oecd.org/public/rest/data/OECD.CPI.M.{country}?startPeriod=2024-01&endPeriod=2024-12&format=json"
            response = requests.get(url, timeout=10)
            print(f"   {country}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"      ✅ Success with {country}!")
                data = response.json()
                if "data" in data and data["data"]:
                    print(f"      📊 Found {len(data['data'])} data points")
                    
        except Exception as e:
            print(f"   {country}: ❌ {e}")

if __name__ == "__main__":
    test_oecd_api()
