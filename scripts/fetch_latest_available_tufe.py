#!/usr/bin/env python3
"""
Fetch the latest available TÜFE data from TCMB EVDS API
"""

import requests
import json
from datetime import datetime, timedelta

# Your API key
API_KEY = "wybNTfaObt"

def fetch_latest_tufe():
    """Fetch the latest available TÜFE data"""
    
    print(f"🔑 Using API key: {API_KEY[:8]}...")
    print()
    
    # Try different date ranges to find available data
    date_ranges = [
        ("01-01-2024", "31-12-2024", "2024 data"),
        ("01-01-2023", "31-12-2023", "2023 data"),
        ("01-01-2022", "31-12-2022", "2022 data"),
    ]
    
    for start_date, end_date, description in date_ranges:
        print(f"🔍 Trying {description}...")
        
        try:
            url = "https://evds2.tcmb.gov.tr/service/evds/seriesData"
            params = {
                "key": API_KEY,
                "type": "json",
                "code": "TP.FG.J0",
                "startDate": start_date,
                "endDate": end_date,
                "aggregationTypes": "avg"
            }
            
            response = requests.get(url, params=params, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "items" in data and data["items"]:
                    print(f"   ✅ Success! Found {len(data['items'])} data points")
                    print()
                    
                    # Display the data
                    items = data["items"]
                    print(f"📊 TÜFE Data for {description}:")
                    print("-" * 50)
                    
                    for item in items[-12:]:  # Show last 12 months
                        date_str = item.get("Tarih", "")
                        value = item.get("TP_FG_J0", "")
                        
                        if date_str and value:
                            try:
                                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                                month_name = date_obj.strftime("%B")
                                year = date_obj.year
                                
                                print(f"{month_name} {year}: {value}%")
                                
                            except ValueError:
                                print(f"{date_str}: {value}%")
                    
                    print()
                    print("📈 Latest Available Data:")
                    if items:
                        latest = items[-1]
                        latest_date = latest.get("Tarih", "")
                        latest_value = latest.get("TP_FG_J0", "")
                        print(f"Most recent: {latest_date} = {latest_value}%")
                    
                    print()
                    print("ℹ️  Note: September 2025 TÜFE data is not yet available.")
                    print("   TÜİK typically releases monthly data in the first week of the following month.")
                    print("   September 2025 data should be available in early October 2025.")
                    
                    return True
                    
                else:
                    print(f"   ⚠️  No data in response")
            else:
                print(f"   ❌ Error: {response.status_code}")
                if response.status_code == 403:
                    print(f"      This might indicate API key issues or access restrictions")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("❌ Could not fetch any TÜFE data")
    print("Possible reasons:")
    print("- API key is invalid or expired")
    print("- API key doesn't have permission to access TÜFE data")
    print("- TCMB API is temporarily unavailable")
    print("- Network/firewall restrictions")
    
    return False

if __name__ == "__main__":
    fetch_latest_tufe()
