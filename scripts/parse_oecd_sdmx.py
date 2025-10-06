#!/usr/bin/env python3
"""
Parse OECD SDMX XML data for Turkey CPI
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_oecd_sdmx():
    """Parse OECD SDMX data for Turkey"""
    
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        print("🔍 Parsing OECD SDMX data for Turkey...")
        print()
        
        # Find all observations
        observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
        print(f"📊 Found {len(observations)} total observations")
        
        # Filter for Turkey data
        turkey_data = []
        
        for obs in observations:
            # Get the observation key
            obs_key = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsKey')
            if obs_key is None:
                continue
            
            # Extract dimensions from the key
            dimensions = {}
            for value in obs_key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                dim_id = value.get('id')
                dim_value = value.get('value')
                dimensions[dim_id] = dim_value
            
            # Check if this is Turkey data
            if dimensions.get('REF_AREA') == 'TUR':
                # Get the observation value
                obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                if obs_value is not None:
                    value = float(obs_value.get('value'))
                    
                    turkey_data.append({
                        'period': dimensions.get('TIME_PERIOD'),
                        'value': value,
                        'frequency': dimensions.get('FREQ'),
                        'measure': dimensions.get('MEASURE'),
                        'unit': dimensions.get('UNIT_MEASURE')
                    })
        
        print(f"🇹🇷 Found {len(turkey_data)} observations for Turkey")
        print()
        
        if turkey_data:
            # Sort by period
            turkey_data.sort(key=lambda x: x['period'])
            
            print("📈 Turkey TÜFE (CPI) Data from OECD:")
            print("-" * 60)
            
            for data in turkey_data:
                period = data['period']
                value = data['value']
                unit = data['unit']
                
                # Parse period (format: YYYY-MM)
                try:
                    if '-' in period:
                        year, month = period.split('-')
                        month_name = datetime(int(year), int(month), 1).strftime('%B')
                        print(f"{month_name} {year}: {value:.2f} {unit}")
                        
                        # Highlight recent data
                        if year == '2024' and int(month) >= 9:
                            print(f"  🎯 Recent data: {value:.2f} {unit}")
                    else:
                        print(f"{period}: {value:.2f} {unit}")
                        
                except ValueError:
                    print(f"{period}: {value:.2f} {unit}")
            
            print()
            print("📈 Summary:")
            if turkey_data:
                latest = turkey_data[-1]
                print(f"Latest data: {latest['period']} = {latest['value']:.2f} {latest['unit']}")
                print(f"Data source: OECD SDMX API")
                print(f"Country: Turkey (TUR)")
                print(f"Measure: {latest['measure']}")
                print(f"Frequency: {latest['frequency']}")
            
            # Check for September 2024
            september_2024 = [d for d in turkey_data if d['period'] == '2024-09']
            if september_2024:
                print(f"\n🎯 September 2024 TÜFE: {september_2024[0]['value']:.2f} {september_2024[0]['unit']}")
            else:
                print(f"\n⚠️  September 2024 data not found")
                print(f"   Latest available: {turkey_data[-1]['period']} = {turkey_data[-1]['value']:.2f} {turkey_data[-1]['unit']}")
            
            return turkey_data
        else:
            print("❌ No Turkey data found")
            print("This might indicate:")
            print("- Turkey is not included in this dataset")
            print("- The country code is different")
            print("- The data structure has changed")
            
            # Let's see what countries are available
            print("\n🔍 Checking available countries...")
            countries = set()
            for obs in observations[:100]:  # Check first 100 observations
                obs_key = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsKey')
                if obs_key is not None:
                    for value in obs_key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                        if value.get('id') == 'REF_AREA':
                            countries.add(value.get('value'))
            
            print(f"Available countries (sample): {sorted(list(countries))[:20]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    parse_oecd_sdmx()
