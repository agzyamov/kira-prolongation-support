#!/usr/bin/env python3
"""
Get ALL Turkey TÜFE (CPI) data for 2024 from OECD API
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def get_turkey_tufe_2024_all():
    """Get ALL Turkey TÜFE (CPI) data for 2024 from OECD API"""
    
    print("🔍 Fetching ALL Turkey TÜFE (CPI) data for 2024 from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data - 2024 only
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        # Find all observations
        observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
        
        # Filter for Turkey monthly CPI data for 2024 (all units)
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
            
            # Check if this is Turkey monthly CPI data for 2024
            if (dimensions.get('REF_AREA') == 'TUR' and 
                dimensions.get('FREQ') == 'M' and  # Monthly
                dimensions.get('MEASURE') == 'CPI' and  # Consumer Price Index
                dimensions.get('TIME_PERIOD', '').startswith('2024')):  # 2024 data only
                
                obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                if obs_value is not None:
                    value = float(obs_value.get('value'))
                    unit = dimensions.get('UNIT_MEASURE', 'Unknown')
                    
                    turkey_2024_data.append({
                        'period': dimensions.get('TIME_PERIOD'),
                        'value': value,
                        'unit': unit
                    })
        
        if turkey_2024_data:
            # Sort by period
            turkey_2024_data.sort(key=lambda x: x['period'])
            
            print(f"📊 Found {len(turkey_2024_data)} monthly TÜFE data points for Turkey in 2024")
            print()
            
            # Group by month and unit
            monthly_data = {}
            for data in turkey_2024_data:
                period = data['period']
                value = data['value']
                unit = data['unit']
                
                # Parse period (format: YYYY-MM)
                try:
                    year, month = period.split('-')
                    month_name = datetime(int(year), int(month), 1).strftime('%B')
                    
                    if month not in monthly_data:
                        monthly_data[month] = {}
                    if unit not in monthly_data[month]:
                        monthly_data[month][unit] = []
                    
                    monthly_data[month][unit].append({
                        'month_name': month_name,
                        'value': value,
                        'period': period
                    })
                    
                except ValueError:
                    continue
            
            print("📈 Turkey TÜFE (CPI) Data for 2024:")
            print("=" * 80)
            
            # Display data by month
            for month in sorted(monthly_data.keys()):
                month_data = monthly_data[month]
                month_name = list(month_data.values())[0][0]['month_name']
                
                print(f"\n{month_name} 2024:")
                print("-" * 40)
                
                for unit, data_list in month_data.items():
                    if data_list:
                        # Take the first value for each unit (they should be the same)
                        value = data_list[0]['value']
                        period = data_list[0]['period']
                        
                        # Explain what each unit means
                        unit_explanation = {
                            'PA': 'Percentage Annual (year-over-year inflation)',
                            'PC': 'Percentage Change (month-over-month)',
                            'IX': 'Index (base year = 100)',
                            'PD': 'Percentage Difference',
                            '10P3EXP_CNSMR': 'Consumer Expenditure (10P3)'
                        }
                        
                        explanation = unit_explanation.get(unit, f'Unit: {unit}')
                        print(f"  {unit:15} | {value:8.2f} | {explanation}")
            
            print()
            print("📈 2024 Summary:")
            print(f"Total data points: {len(turkey_2024_data)}")
            print(f"Data source: OECD SDMX API")
            print(f"Country: Turkey (TUR)")
            print(f"Measure: Consumer Price Index (CPI)")
            print(f"Year: 2024")
            
            # Show the main TÜFE rates (PA - Percentage Annual)
            pa_data = [d for d in turkey_2024_data if d['unit'] == 'PA']
            if pa_data:
                print(f"\n🎯 Main TÜFE Rates (Percentage Annual - PA):")
                print("-" * 50)
                for data in pa_data:
                    period = data['period']
                    value = data['value']
                    try:
                        year, month = period.split('-')
                        month_name = datetime(int(year), int(month), 1).strftime('%B')
                        print(f"{month_name} 2024: {value:.2f}%")
                    except ValueError:
                        print(f"{period}: {value:.2f}%")
                
                # Calculate statistics for PA data
                pa_values = [d['value'] for d in pa_data]
                print(f"\n📊 2024 TÜFE Statistics (PA):")
                print(f"Average: {sum(pa_values)/len(pa_values):.2f}%")
                print(f"Highest: {max(pa_values):.2f}%")
                print(f"Lowest: {min(pa_values):.2f}%")
                print(f"Data points: {len(pa_values)}")
            
            # Show September 2024 specifically
            september_2024 = [d for d in turkey_2024_data if d['period'] == '2024-09']
            if september_2024:
                print(f"\n🎯 September 2024 TÜFE Data:")
                print("-" * 40)
                for data in september_2024:
                    unit = data['unit']
                    value = data['value']
                    unit_explanation = {
                        'PA': 'Percentage Annual (year-over-year inflation)',
                        'PC': 'Percentage Change (month-over-month)',
                        'IX': 'Index (base year = 100)',
                        'PD': 'Percentage Difference',
                        '10P3EXP_CNSMR': 'Consumer Expenditure (10P3)'
                    }
                    explanation = unit_explanation.get(unit, f'Unit: {unit}')
                    print(f"  {unit:15} | {value:8.2f} | {explanation}")
            else:
                print(f"\n⚠️  September 2024 data not found in this dataset")
            
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
    get_turkey_tufe_2024_all()
