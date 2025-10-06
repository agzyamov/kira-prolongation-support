#!/usr/bin/env python3
"""
Parse TÜFE data from OECD API once and save to database
"""

import requests
import xml.etree.ElementTree as ET
import sqlite3
import time
from datetime import datetime
import sys
import os

# Add src to path to import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storage.data_store import DataStore
from models.inflation_data import InflationData

def parse_and_save_tufe_data():
    """Parse TÜFE data once and save to database"""
    
    print("🔍 Парсинг и сохранение данных TÜFE в базу данных")
    print("=" * 60)
    print()
    
    # Initialize database
    db_path = "data/rental_negotiation.db"
    data_store = DataStore(db_path)
    
    print("📊 Подключение к базе данных...")
    print(f"   Путь: {db_path}")
    
    # Check if we already have TÜFE data
    existing_data = data_store.get_inflation_data()
    if existing_data:
        print(f"   ✅ Найдено {len(existing_data)} существующих записей")
        
        # Show existing data
        print("   📈 Существующие данные:")
        for data in existing_data[-5:]:  # Show last 5
            print(f"      {data.year}: {data.tufe_rate}%")
    else:
        print("   📝 База данных пуста")
    
    print()
    
    # Try to get data from OECD API
    print("🌐 Попытка получения данных из OECD API...")
    
    # Use a smaller date range to avoid rate limiting
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2020-01&endTime=2023-12"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ Успешно получено ({len(response.text):,} байт)")
            
            # Parse XML
            root = ET.fromstring(response.text)
            observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
            
            # Filter for Turkey monthly CPI data with percentage annual (PA) unit
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
                        period = dimensions.get('TIME_PERIOD')
                        
                        # Parse period (format: YYYY-MM)
                        try:
                            year, month = period.split('-')
                            year = int(year)
                            month = int(month)
                            
                            turkey_data.append({
                                'year': year,
                                'month': month,
                                'period': period,
                                'value': value
                            })
                        except ValueError:
                            continue
            
            if turkey_data:
                # Sort by year and month
                turkey_data.sort(key=lambda x: (x['year'], x['month']))
                
                print(f"   📊 Найдено {len(turkey_data)} точек данных")
                print()
                
                # Show sample data
                print("   📈 Пример данных:")
                for data in turkey_data[:5]:
                    month_name = datetime(data['year'], data['month'], 1).strftime('%B')
                    print(f"      {month_name} {data['year']}: {data['value']:.2f}%")
                
                if len(turkey_data) > 5:
                    print(f"      ... и еще {len(turkey_data) - 5} записей")
                
                print()
                
                # Save to database
                print("💾 Сохранение в базу данных...")
                
                saved_count = 0
                for data in turkey_data:
                    try:
                        # Create InflationData object
                        inflation_data = InflationData(
                            year=data['year'],
                            tufe_rate=data['value'],
                            source="OECD SDMX API",
                            notes=f"Parsed from OECD API on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                        
                        # Save to database
                        data_store.save_inflation_data(inflation_data)
                        saved_count += 1
                        
                    except Exception as e:
                        print(f"      ❌ Ошибка сохранения {data['period']}: {e}")
                
                print(f"   ✅ Сохранено {saved_count} записей")
                print()
                
                # Show summary
                print("📊 Сводка сохраненных данных:")
                print("-" * 40)
                
                years = set(d['year'] for d in turkey_data)
                for year in sorted(years):
                    year_data = [d for d in turkey_data if d['year'] == year]
                    values = [d['value'] for d in year_data]
                    avg_value = sum(values) / len(values)
                    print(f"   {year}: {len(year_data)} месяцев, среднее: {avg_value:.2f}%")
                
                print()
                print("🎯 Данные успешно сохранены в базу данных!")
                print("   Теперь ваше приложение может использовать эти данные")
                print("   без необходимости обращаться к OECD API")
                
                return True
                
            else:
                print("   ❌ Данные не найдены")
                
        elif response.status_code == 429:
            print(f"   ❌ Забанены (429)")
            print(f"   Сообщение: {response.text[:100]}")
            print()
            print("💡 Рекомендации:")
            print("   • Подождать несколько часов")
            print("   • Использовать VPN для смены IP")
            print("   • Использовать альтернативные источники")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            print(f"   Ответ: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print()
    print("🔧 Альтернативные варианты:")
    print("-" * 30)
    print("1. Ручной ввод данных через приложение")
    print("2. Использование TCMB API (если ключ работает)")
    print("3. Веб-скрапинг с официальных сайтов")
    print("4. Использование готовых CSV файлов")
    
    return False

if __name__ == "__main__":
    parse_and_save_tufe_data()
