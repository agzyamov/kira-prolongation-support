#!/usr/bin/env python3
"""
Get CURRENT (October 2025) TÜFE data from TCMB EVDS API.
"""

import requests
import json
from datetime import datetime

# You need to provide your actual TCMB API key here
# Get it from: https://evds2.tcmb.gov.tr/
API_KEY = input("Enter your TCMB API key (or press Enter to skip): ").strip()

if not API_KEY:
    print("\n❌ No API key provided. Cannot fetch real-time data.")
    print("\n💡 To get current TÜFE data:")
    print("   1. Get API key from: https://evds2.tcmb.gov.tr/")
    print("   2. Run this script again with your key")
    exit(1)

print(f"\n✅ Using API key: {API_KEY[:10]}...")

# Fetch data for 2025
year = 2025
base_url = "https://evds2.tcmb.gov.tr/service/evds/"
url = f"{base_url}series=TP.FE.OKTG01&startDate=01-01-{year}&endDate=31-12-{year}&type=json&key={API_KEY}"

print(f"\n📡 Fetching TÜFE data for {year} from TCMB EVDS API...")
print(f"   URL: {url.replace(API_KEY, 'XXX')}")

try:
    response = requests.get(url, timeout=15)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ SUCCESS! Received data for {year}")
        print(f"\n📊 Full API Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if 'items' in data and len(data['items']) > 0:
            print(f"\n📈 TÜFE Rates for {year}:")
            for item in data['items']:
                date = item.get('Tarih', 'N/A')
                rate = item.get('TP_FE_OKTG01', 'N/A')
                print(f"   {date}: {rate}%")
            
            # Find September 2025
            september_data = [item for item in data['items'] if '09-2025' in item.get('Tarih', '')]
            
            if september_data:
                print(f"\n🎯 SEPTEMBER 2025 TÜFE RATE: {september_data[0]['TP_FE_OKTG01']}%")
            else:
                print(f"\n⚠️ September 2025 data not yet available")
                print(f"   Latest available: {data['items'][-1]['Tarih']}: {data['items'][-1]['TP_FE_OKTG01']}%")
        else:
            print(f"\n⚠️ No data items found in response")
    
    elif response.status_code == 403:
        print(f"\n❌ ERROR 403: Invalid or expired API key")
        print(f"   Please check your API key at: https://evds2.tcmb.gov.tr/")
    
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"   Response: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

