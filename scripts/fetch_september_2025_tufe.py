#!/usr/bin/env python3
"""
Fetch September 2025 TÜFE data from TCMB EVDS API
"""

import requests
import json
from datetime import datetime

# Your API key
API_KEY = "wybNTfaObt"

def fetch_tufe_data():
    """Fetch TÜFE data for 2025 from TCMB EVDS API"""
    
    # TCMB EVDS API endpoint for TÜFE data
    base_url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
    
    # TÜFE series code (Consumer Price Index)
    series_code = "TP.FG.J0"
    
    # Parameters for 2025 data
    params = {
        "key": API_KEY,
        "type": "json",
        "code": series_code,
        "startDate": "01-01-2025",
        "endDate": "31-12-2025",
        "aggregationTypes": "avg",
        "formulas": "0"
    }
    
    print(f"🔍 Fetching TÜFE data for 2025...")
    print(f"📅 Date range: January 2025 - December 2025")
    print(f"🔑 Using API key: {API_KEY[:8]}...")
    print()
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "items" in data and data["items"]:
            print("✅ Successfully fetched TÜFE data!")
            print()
            
            # Display the data
            items = data["items"]
            print("📊 TÜFE Data for 2025:")
            print("-" * 50)
            
            for item in items:
                date_str = item.get("Tarih", "")
                value = item.get("TP_FG_J0", "")
                
                if date_str and value:
                    # Parse the date (format: DD-MM-YYYY)
                    try:
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                        month_name = date_obj.strftime("%B")
                        year = date_obj.year
                        
                        print(f"{month_name} {year}: {value}%")
                        
                        # Highlight September
                        if date_obj.month == 9:
                            print(f"  🎯 SEPTEMBER 2025 TÜFE: {value}%")
                            
                    except ValueError:
                        print(f"{date_str}: {value}%")
            
            print()
            print("📈 Data Summary:")
            print(f"Total data points: {len(items)}")
            print(f"Data source: TCMB EVDS API")
            print(f"Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            print("❌ No data found in response")
            print("Response:", json.dumps(data, indent=2))
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("This might be due to:")
        print("- Internet connection issues")
        print("- TCMB API server being down")
        print("- Firewall blocking the request")
        print("- API key issues")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print("Response content:", response.text[:500])
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    fetch_tufe_data()
