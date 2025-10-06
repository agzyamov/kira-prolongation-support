#!/usr/bin/env python3
"""
Get clean Turkey CPI data from OECD API
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_turkey_cpi():
    """Get Turkey CPI data from OECD API"""
    
    print("🔍 Fetching Turkey CPI data from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2025-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        # Find all observations
        observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
        
        # Filter for Turkey monthly CPI data
        turkey_monthly_data = []
        
        for obs in observations:
            obs_key = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsKey')
            if obs_key is None:
                continue
            
            # Extract dimensions
            dimensions = {}
            for value in obs_key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                dim_id = value.get('id')
                dim_value = value.get('value')
                dimensions[dim_id] = dim_value
            
            # Check if this is Turkey monthly CPI data
            if (dimensions.get('REF_AREA') == 'TUR' and 
                dimensions.get('FREQ') == 'M' and  # Monthly
                dimensions.get('MEASURE') == 'CPI'):  # Consumer Price Index
                
                obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                if obs_value is not None:
                    value = float(obs_value.get('value'))
                    unit = dimensions.get('UNIT_MEASURE', 'Unknown')
                    
                    turkey_monthly_data.append({
                        'period': dimensions.get('TIME_PERIOD'),
                        'value': value,
                        'unit': unit,
                        'measure': dimensions.get('MEASURE')
                    })
        
        if turkey_monthly_data:
            # Sort by period
            turkey_monthly_data.sort(key=lambda x: x['period'])
            
            print(f"📊 Found {len(turkey_monthly_data)} monthly CPI data points for Turkey")
            print()
            
            # Display recent data (last 12 months)
            recent_data = turkey_monthly_data[-12:] if len(turkey_monthly_data) >= 12 else turkey_monthly_data
            
            print("📈 Recent Turkey CPI Data (Monthly):")
            print("-" * 60)
            
            for data in recent_data:
                period = data['period']
                value = data['value']
                unit = data['unit']
                
                # Parse period (format: YYYY-MM)
                try:
                    year, month = period.split('-')
                    month_name = datetime(int(year), int(month), 1).strftime('%B')
                    print(f"{month_name} {year}: {value:.2f} {unit}")
                    
                    # Highlight if it's recent data
                    if year == '2024' and int(month) >= 9:
                        print(f"  🎯 Recent data: {value:.2f} {unit}")
                    elif year == '2025':
                        print(f"  🎯 2025 data: {value:.2f} {unit}")
                        
                except ValueError:
                    print(f"{period}: {value:.2f} {unit}")
            
            print()
            print("📈 Summary:")
            if turkey_monthly_data:
                latest = turkey_monthly_data[-1]
                print(f"Latest data: {latest['period']} = {latest['value']:.2f} {latest['unit']}")
                print(f"Data source: OECD SDMX API")
                print(f"Country: Turkey (TUR)")
                print(f"Measure: {latest['measure']}")
                print(f"Frequency: Monthly")
            
            # Check for September 2024
            september_2024 = [d for d in turkey_monthly_data if d['period'] == '2024-09']
            if september_2024:
                print(f"\n🎯 September 2024 CPI: {september_2024[0]['value']:.2f} {september_2024[0]['unit']}")
            else:
                print(f"\n⚠️  September 2024 data not found")
                print(f"   Latest available: {turkey_monthly_data[-1]['period']} = {turkey_monthly_data[-1]['value']:.2f} {turkey_monthly_data[-1]['unit']}")
            
            # Check for 2025 data
            data_2025 = [d for d in turkey_monthly_data if d['period'].startswith('2025')]
            if data_2025:
                print(f"\n📅 2025 data available:")
                for data in data_2025:
                    period = data['period']
                    value = data['value']
                    unit = data['unit']
                    try:
                        year, month = period.split('-')
                        month_name = datetime(int(year), int(month), 1).strftime('%B')
                        print(f"   {month_name} {year}: {value:.2f} {unit}")
                    except ValueError:
                        print(f"   {period}: {value:.2f} {unit}")
            
            return turkey_monthly_data
        else:
            print("❌ No monthly CPI data found for Turkey")
            print("This might indicate:")
            print("- Turkey monthly CPI data is not available in this dataset")
            print("- The data structure has changed")
            print("- The country code or measure is different")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    get_turkey_cpi()
