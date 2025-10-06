#!/usr/bin/env python3
"""
Get Turkey TÜFE data for 2023 from OECD API
"""

import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime

def get_turkey_tufe_2023():
    """Get Turkey TÜFE data for 2023"""
    
    print("🔍 Получение данных TÜFE за 2023 год")
    print("=" * 50)
    print()
    
    # Try a single month first to test
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2023-01&endTime=2023-12"
    
    try:
        print("📅 Получение данных за 2023 год...")
        print(f"   Запрос: 2023-01 - 2023-12")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ Успешно получено ({len(response.text):,} байт)")
            
            # Parse XML
            root = ET.fromstring(response.text)
            observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
            
            # Filter for Turkey monthly CPI data with percentage annual (PA) unit
            turkey_2023_data = []
            
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
                
                # Check if this is Turkey monthly CPI data with percentage annual (PA) unit for 2023
                if (dimensions.get('REF_AREA') == 'TUR' and 
                    dimensions.get('FREQ') == 'M' and  # Monthly
                    dimensions.get('MEASURE') == 'CPI' and  # Consumer Price Index
                    dimensions.get('UNIT_MEASURE') == 'PA' and  # Percentage Annual
                    dimensions.get('TIME_PERIOD', '').startswith('2023')):  # 2023 data only
                    
                    obs_value = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
                    if obs_value is not None:
                        value = float(obs_value.get('value'))
                        
                        turkey_2023_data.append({
                            'period': dimensions.get('TIME_PERIOD'),
                            'value': value,
                            'unit': 'PA'
                        })
            
            if turkey_2023_data:
                # Sort by period
                turkey_2023_data.sort(key=lambda x: x['period'])
                
                print(f"   📊 Найдено {len(turkey_2023_data)} точек данных")
                print()
                
                print("📈 Turkey TÜFE (CPI) Data for 2023 - Monthly Annual Percentage:")
                print("=" * 70)
                print()
                
                print("Month        | TÜFE Rate (%) | Period")
                print("-" * 50)
                
                for data in turkey_2023_data:
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
                print("📈 2023 TÜFE Summary:")
                print("-" * 30)
                
                values = [d['value'] for d in turkey_2023_data]
                print(f"Total data points: {len(turkey_2023_data)}")
                print(f"Average TÜFE rate: {sum(values)/len(values):.2f}%")
                print(f"Highest TÜFE rate: {max(values):.2f}%")
                print(f"Lowest TÜFE rate: {min(values):.2f}%")
                print()
                
                # Show September 2023 specifically
                september_2023 = [d for d in turkey_2023_data if d['period'] == '2023-09']
                if september_2023:
                    print(f"🎯 September 2023 TÜFE: {september_2023[0]['value']:.2f}%")
                else:
                    print(f"⚠️  September 2023 data not found")
                
                print()
                print("📊 Key Insights:")
                print("-" * 20)
                
                # Find peak and low months
                max_data = max(turkey_2023_data, key=lambda x: x['value'])
                min_data = min(turkey_2023_data, key=lambda x: x['value'])
                
                print(f"• Peak month: {max_data['period']} = {max_data['value']:.2f}%")
                print(f"• Lowest month: {min_data['period']} = {min_data['value']:.2f}%")
                
                print()
                print("🔗 Data Source: OECD SDMX API")
                print("   URL: https://stats.oecd.org/restsdmx/sdmx.ashx/")
                print("   Dataset: PRICES_CPI")
                print("   Country: Turkey (TUR)")
                print("   Measure: Consumer Price Index (CPI)")
                print("   Unit: Percentage Annual (PA)")
                
                return turkey_2023_data
            else:
                print("   ❌ No 2023 TÜFE data found")
                
        elif response.status_code == 429:
            print(f"   ❌ Снова забанены (429)")
            print(f"   Сообщение: {response.text[:100]}")
            print()
            print("💡 Рекомендации:")
            print("   • Подождать несколько часов")
            print("   • Использовать VPN для смены IP")
            print("   • Обратиться в OECD через форму обратной связи")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    return None

if __name__ == "__main__":
    get_turkey_tufe_2023()
