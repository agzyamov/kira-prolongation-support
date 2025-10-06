#!/usr/bin/env python3
"""
Fetch Turkey TÜFE data from OECD API and parse it
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json

def fetch_oecd_tufe():
    """Fetch Turkey TÜFE data from OECD API"""
    
    print("🔍 Fetching Turkey TÜFE data from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        print(f"📡 Requesting data from: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Success! Response size: {len(response.text):,} bytes")
            print()
            
            # Parse the XML response
            root = ET.fromstring(response.text)
            
            # Find all data points
            data_points = []
            
            # Look for data in the XML structure
            for series in root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Series'):
                # Get series key (should contain Turkey info)
                key = series.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}SeriesKey')
                if key is not None:
                    # Get the country code
                    country_code = None
                    for value in key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                        if value.get('id') == 'LOCATION':
                            country_code = value.get('value')
                            break
                    
                    if country_code == 'TUR':
                        # Get all observations for this series
                        for obs in series.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs'):
                            time_period = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Time')
                            value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                            
                            if time_period is not None and value is not None:
                                data_points.append({
                                    'period': time_period.text,
                                    'value': float(value.get('value')),
                                    'country': country_code
                                })
            
            if data_points:
                print(f"📊 Found {len(data_points)} data points for Turkey")
                print()
                
                # Sort by period
                data_points.sort(key=lambda x: x['period'])
                
                # Display the data
                print("📈 Turkey TÜFE (CPI) Data from OECD:")
                print("-" * 50)
                
                for point in data_points:
                    period = point['period']
                    value = point['value']
                    
                    # Parse period (format: YYYY-MM)
                    try:
                        year, month = period.split('-')
                        month_name = datetime(int(year), int(month), 1).strftime('%B')
                        print(f"{month_name} {year}: {value:.2f}%")
                        
                        # Highlight if it's recent data
                        if year == '2024' and int(month) >= 9:
                            print(f"  🎯 Recent data: {value:.2f}%")
                            
                    except ValueError:
                        print(f"{period}: {value:.2f}%")
                
                print()
                print("📈 Summary:")
                if data_points:
                    latest = data_points[-1]
                    print(f"Latest data: {latest['period']} = {latest['value']:.2f}%")
                    print(f"Data source: OECD SDMX API")
                    print(f"Country: Turkey (TUR)")
                    print(f"Series: Consumer Price Index (CPALTT01)")
                
                # Check if we have September 2024 data
                september_2024 = [p for p in data_points if p['period'] == '2024-09']
                if september_2024:
                    print(f"\n🎯 September 2024 TÜFE: {september_2024[0]['value']:.2f}%")
                else:
                    print(f"\n⚠️  September 2024 data not found in OECD dataset")
                    print(f"   Latest available: {data_points[-1]['period']} = {data_points[-1]['value']:.2f}%")
                
                return data_points
                
            else:
                print("❌ No data points found in the response")
                print("This might indicate:")
                print("- Turkey data is not available in this dataset")
                print("- The series code is incorrect")
                print("- The data structure has changed")
                
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        print("The response might not be valid XML")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    fetch_oecd_tufe()
