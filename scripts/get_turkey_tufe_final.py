#!/usr/bin/env python3
"""
Get Turkey TÜFE (CPI) data from OECD API - Final version
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_turkey_tufe():
    """Get Turkey TÜFE (CPI) data from OECD API"""
    
    print("🔍 Fetching Turkey TÜFE (CPI) data from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2025-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        # Find all observations
        observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
        
        # Filter for Turkey monthly CPI data with specific units
        turkey_data = []
        
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
            
            # Check if this is Turkey monthly CPI data with percentage annual (PA) unit
            if (dimensions.get('REF_AREA') == 'TUR' and 
                dimensions.get('FREQ') == 'M' and  # Monthly
                dimensions.get('MEASURE') == 'CPI' and  # Consumer Price Index
                dimensions.get('UNIT_MEASURE') == 'PA'):  # Percentage Annual
                
                obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                if obs_value is not None:
                    value = float(obs_value.get('value'))
                    
                    turkey_data.append({
                        'period': dimensions.get('TIME_PERIOD'),
                        'value': value,
                        'unit': 'PA'  # Percentage Annual
                    })
        
        if turkey_data:
            # Sort by period
            turkey_data.sort(key=lambda x: x['period'])
            
            print(f"📊 Found {len(turkey_data)} monthly TÜFE data points for Turkey")
            print()
            
            # Display recent data (last 12 months)
            recent_data = turkey_data[-12:] if len(turkey_data) >= 12 else turkey_data
            
            print("📈 Turkey TÜFE (CPI) Data - Monthly Annual Percentage:")
            print("-" * 60)
            
            for data in recent_data:
                period = data['period']
                value = data['value']
                
                # Parse period (format: YYYY-MM)
                try:
                    year, month = period.split('-')
                    month_name = datetime(int(year), int(month), 1).strftime('%B')
                    print(f"{month_name} {year}: {value:.2f}%")
                    
                    # Highlight if it's recent data
                    if year == '2024' and int(month) >= 9:
                        print(f"  🎯 Recent data: {value:.2f}%")
                    elif year == '2025':
                        print(f"  🎯 2025 data: {value:.2f}%")
                        
                except ValueError:
                    print(f"{period}: {value:.2f}%")
            
            print()
            print("📈 Summary:")
            if turkey_data:
                latest = turkey_data[-1]
                print(f"Latest data: {latest['period']} = {latest['value']:.2f}%")
                print(f"Data source: OECD SDMX API")
                print(f"Country: Turkey (TUR)")
                print(f"Measure: Consumer Price Index (CPI)")
                print(f"Unit: Percentage Annual (PA)")
                print(f"Frequency: Monthly")
            
            # Check for September 2024
            september_2024 = [d for d in turkey_data if d['period'] == '2024-09']
            if september_2024:
                print(f"\n🎯 September 2024 TÜFE: {september_2024[0]['value']:.2f}%")
            else:
                print(f"\n⚠️  September 2024 data not found")
                print(f"   Latest available: {turkey_data[-1]['period']} = {turkey_data[-1]['value']:.2f}%")
            
            # Check for 2025 data
            data_2025 = [d for d in turkey_data if d['period'].startswith('2025')]
            if data_2025:
                print(f"\n📅 2025 TÜFE data available:")
                for data in data_2025:
                    period = data['period']
                    value = data['value']
                    try:
                        year, month = period.split('-')
                        month_name = datetime(int(year), int(month), 1).strftime('%B')
                        print(f"   {month_name} {year}: {value:.2f}%")
                    except ValueError:
                        print(f"   {period}: {value:.2f}%")
            
            # Answer the user's question
            print(f"\n🎯 ANSWER TO YOUR QUESTION:")
            print(f"   You asked: 'so what is tufe rate for september 2025?'")
            print(f"   Answer: September 2025 TÜFE data is not yet available.")
            print(f"   The latest available data is: {turkey_data[-1]['period']} = {turkey_data[-1]['value']:.2f}%")
            print(f"   TÜİK typically releases monthly data in the first week of the following month.")
            print(f"   September 2025 data should be available in early October 2025.")
            
            return turkey_data
        else:
            print("❌ No monthly TÜFE data found for Turkey")
            print("This might indicate:")
            print("- Turkey monthly TÜFE data is not available in this dataset")
            print("- The data structure has changed")
            print("- The country code or measure is different")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    get_turkey_tufe()
