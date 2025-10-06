#!/usr/bin/env python3
"""
Get Turkey TÜFE data for 2024 from OECD API - Conservative approach
"""

import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

def get_turkey_tufe_2024_conservative():
    """Get Turkey TÜFE data for 2024 with conservative approach"""
    
    print("🔍 Получение данных TÜFE за 2024 год (консервативный подход)")
    print("=" * 70)
    print()
    
    # Use smaller date ranges to avoid rate limiting
    date_ranges = [
        ("2024-01", "2024-03", "Q1 2024"),
        ("2024-04", "2024-06", "Q2 2024"),
        ("2024-07", "2024-09", "Q3 2024"),
        ("2024-10", "2024-12", "Q4 2024"),
    ]
    
    all_turkey_data = []
    
    for start_date, end_date, quarter_name in date_ranges:
        print(f"📅 Получение данных за {quarter_name}...")
        
        # OECD API endpoint for Turkey CPI data
        url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime={start_date}&endTime={end_date}"
        
        try:
            print(f"   Запрос: {start_date} - {end_date}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Успешно получено ({len(response.text):,} байт)")
                
                # Parse XML
                root = ET.fromstring(response.text)
                observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
                
                # Filter for Turkey monthly CPI data with percentage annual (PA) unit
                quarter_data = []
                
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
                            
                            quarter_data.append({
                                'period': dimensions.get('TIME_PERIOD'),
                                'value': value,
                                'unit': 'PA'
                            })
                
                if quarter_data:
                    print(f"   📊 Найдено {len(quarter_data)} точек данных")
                    all_turkey_data.extend(quarter_data)
                else:
                    print(f"   ⚠️  Данные не найдены")
                
            elif response.status_code == 429:
                print(f"   ❌ Снова забанены (429)")
                print(f"   Сообщение: {response.text[:100]}")
                break
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                print(f"   Ответ: {response.text[:100]}")
            
            # Wait between requests to avoid rate limiting
            print(f"   ⏳ Ожидание 3 секунды...")
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print()
    
    if all_turkey_data:
        # Sort by period
        all_turkey_data.sort(key=lambda x: x['period'])
        
        print("📈 Turkey TÜFE (CPI) Data for 2024 - Monthly Annual Percentage:")
        print("=" * 70)
        print()
        
        print("Month        | TÜFE Rate (%) | Period")
        print("-" * 50)
        
        for data in all_turkey_data:
            period = data['period']
            value = data['value']
            
            # Parse period (format: YYYY-MM)
            try:
                year, month = period.split('-')
                month_name = datetime(int(year), int(month), 1).strftime('%B')
                print(f"{month_name:12} | {value:11.2f}% | {period}")
            except ValueError:
                print(f"{period:12} | {value:11.2f}% | {period}")
        
        print()
        print("📈 2024 TÜFE Summary:")
        print("-" * 30)
        
        values = [d['value'] for d in all_turkey_data]
        print(f"Total data points: {len(all_turkey_data)}")
        print(f"Average TÜFE rate: {sum(values)/len(values):.2f}%")
        print(f"Highest TÜFE rate: {max(values):.2f}%")
        print(f"Lowest TÜFE rate: {min(values):.2f}%")
        print()
        
        # Show September 2024 specifically
        september_2024 = [d for d in all_turkey_data if d['period'] == '2024-09']
        if september_2024:
            print(f"🎯 September 2024 TÜFE: {september_2024[0]['value']:.2f}%")
        else:
            print(f"⚠️  September 2024 data not found")
        
        print()
        print("📊 Key Insights:")
        print("-" * 20)
        
        # Find peak and low months
        max_data = max(all_turkey_data, key=lambda x: x['value'])
        min_data = min(all_turkey_data, key=lambda x: x['value'])
        
        print(f"• Peak month: {max_data['period']} = {max_data['value']:.2f}%")
        print(f"• Lowest month: {min_data['period']} = {min_data['value']:.2f}%")
        
        # Check for data consistency
        unique_values = set(d['value'] for d in all_turkey_data)
        if len(unique_values) < len(all_turkey_data) * 0.5:
            print("• ⚠️  Warning: Many identical values detected")
            print("  This might indicate data quality issues")
        
        print()
        print("🔗 Data Source: OECD SDMX API")
        print("   URL: https://stats.oecd.org/restsdmx/sdmx.ashx/")
        print("   Dataset: PRICES_CPI")
        print("   Country: Turkey (TUR)")
        print("   Measure: Consumer Price Index (CPI)")
        print("   Unit: Percentage Annual (PA)")
        
        return all_turkey_data
    else:
        print("❌ No 2024 TÜFE data found")
        print("This might indicate:")
        print("- Turkey 2024 TÜFE data is not available in this dataset")
        print("- The data structure has changed")
        print("- We're still rate limited")
        
        return None

if __name__ == "__main__":
    get_turkey_tufe_2024_conservative()
