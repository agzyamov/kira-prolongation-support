#!/usr/bin/env python3
"""
Get Turkey TÜFE (CPI) data for 2024 from OECD API
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_turkey_tufe_2024():
    """Get Turkey TÜFE (CPI) data for 2024 from OECD API"""
    
    print("🔍 Fetching Turkey TÜFE (CPI) data for 2024 from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data - 2024 only
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        # Find all observations
        observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
        
        # Filter for Turkey monthly CPI data with percentage annual (PA) unit
        turkey_2024_data = []
        
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
            
            # Check if this is Turkey monthly CPI data with percentage annual (PA) unit for 2024
            if (dimensions.get('REF_AREA') == 'TUR' and 
                dimensions.get('FREQ') == 'M' and  # Monthly
                dimensions.get('MEASURE') == 'CPI' and  # Consumer Price Index
                dimensions.get('UNIT_MEASURE') == 'PA' and  # Percentage Annual
                dimensions.get('TIME_PERIOD', '').startswith('2024')):  # 2024 data only
                
                obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                if obs_value is not None:
                    value = float(obs_value.get('value'))
                    
                    turkey_2024_data.append({
                        'period': dimensions.get('TIME_PERIOD'),
                        'value': value,
                        'unit': 'PA'  # Percentage Annual
                    })
        
        if turkey_2024_data:
            # Sort by period
            turkey_2024_data.sort(key=lambda x: x['period'])
            
            print(f"📊 Found {len(turkey_2024_data)} monthly TÜFE data points for Turkey in 2024")
            print()
            
            print("📈 Turkey TÜFE (CPI) Data for 2024 - Monthly Annual Percentage:")
            print("=" * 70)
            
            # Group by month to show the main TÜFE rate for each month
            monthly_data = {}
            for data in turkey_2024_data:
                period = data['period']
                value = data['value']
                
                # Parse period (format: YYYY-MM)
                try:
                    year, month = period.split('-')
                    month_name = datetime(int(year), int(month), 1).strftime('%B')
                    
                    # Store the main TÜFE rate for each month (we'll take the most common/reasonable value)
                    if month not in monthly_data:
                        monthly_data[month] = []
                    monthly_data[month].append({
                        'month_name': month_name,
                        'value': value,
                        'period': period
                    })
                    
                except ValueError:
                    continue
            
            # Display the main TÜFE rate for each month of 2024
            print("Month        | TÜFE Rate (%) | Period")
            print("-" * 50)
            
            for month in sorted(monthly_data.keys()):
                month_data = monthly_data[month]
                # Take the median value as the main TÜFE rate for the month
                values = [d['value'] for d in month_data]
                values.sort()
                median_value = values[len(values)//2] if values else 0
                
                month_name = month_data[0]['month_name']
                period = month_data[0]['period']
                
                print(f"{month_name:12} | {median_value:11.2f}% | {period}")
            
            print()
            print("📈 2024 Summary:")
            if turkey_2024_data:
                # Calculate statistics
                values = [d['value'] for d in turkey_2024_data]
                values.sort()
                
                print(f"Total data points: {len(turkey_2024_data)}")
                print(f"Average TÜFE rate: {sum(values)/len(values):.2f}%")
                print(f"Highest TÜFE rate: {max(values):.2f}%")
                print(f"Lowest TÜFE rate: {min(values):.2f}%")
                print(f"Data source: OECD SDMX API")
                print(f"Country: Turkey (TUR)")
                print(f"Measure: Consumer Price Index (CPI)")
                print(f"Unit: Percentage Annual (PA)")
                print(f"Year: 2024")
            
            # Show September 2024 specifically
            september_2024 = [d for d in turkey_2024_data if d['period'] == '2024-09']
            if september_2024:
                print(f"\n🎯 September 2024 TÜFE: {september_2024[0]['value']:.2f}%")
            else:
                print(f"\n⚠️  September 2024 data not found in this dataset")
            
            # Show all 2024 data points for reference
            print(f"\n📅 All 2024 TÜFE data points:")
            print("-" * 50)
            for data in turkey_2024_data:
                period = data['period']
                value = data['value']
                try:
                    year, month = period.split('-')
                    month_name = datetime(int(year), int(month), 1).strftime('%B')
                    print(f"{month_name} {year}: {value:.2f}%")
                except ValueError:
                    print(f"{period}: {value:.2f}%")
            
            return turkey_2024_data
        else:
            print("❌ No 2024 TÜFE data found for Turkey")
            print("This might indicate:")
            print("- Turkey 2024 TÜFE data is not available in this dataset")
            print("- The data structure has changed")
            print("- The country code or measure is different")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    get_turkey_tufe_2024()
