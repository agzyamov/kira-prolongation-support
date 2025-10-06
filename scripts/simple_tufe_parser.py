#!/usr/bin/env python3
"""
Simple TÜFE data parser and saver
"""

import requests
import xml.etree.ElementTree as ET
import sqlite3
import json
from datetime import datetime
import os

def create_tufe_database():
    """Create a simple TÜFE database"""
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect("data/tufe_data.db")
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tufe_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            period TEXT NOT NULL,
            tufe_rate REAL NOT NULL,
            source TEXT DEFAULT 'OECD SDMX API',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
    """)
    
    conn.commit()
    return conn

def parse_tufe_data():
    """Parse TÜFE data from OECD API"""
    
    print("🔍 Парсинг данных TÜFE из OECD API")
    print("=" * 50)
    print()
    
    # Try to get data from OECD API
    print("🌐 Получение данных из OECD API...")
    
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
                
                return turkey_data
                
            else:
                print("   ❌ Данные не найдены")
                return None
                
        elif response.status_code == 429:
            print(f"   ❌ Забанены (429)")
            print(f"   Сообщение: {response.text[:100]}")
            return None
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return None

def save_tufe_data(turkey_data):
    """Save TÜFE data to database"""
    
    if not turkey_data:
        print("❌ Нет данных для сохранения")
        return False
    
    print("💾 Сохранение в базу данных...")
    
    # Create database
    conn = create_tufe_database()
    cursor = conn.cursor()
    
    saved_count = 0
    for data in turkey_data:
        try:
            # Insert data
            cursor.execute("""
                INSERT OR REPLACE INTO tufe_data (year, month, period, tufe_rate, source)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['year'],
                data['month'],
                data['period'],
                data['value'],
                'OECD SDMX API'
            ))
            saved_count += 1
            
        except Exception as e:
            print(f"      ❌ Ошибка сохранения {data['period']}: {e}")
    
    conn.commit()
    conn.close()
    
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
    print("   Файл: data/tufe_data.db")
    print("   Теперь ваше приложение может использовать эти данные")
    
    return True

def show_saved_data():
    """Show saved TÜFE data"""
    
    print("📊 Просмотр сохраненных данных:")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect("data/tufe_data.db")
        cursor = conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM tufe_data ORDER BY year, month")
        rows = cursor.fetchall()
        
        if rows:
            print(f"Найдено {len(rows)} записей:")
            print()
            print("Year | Month | Period   | TÜFE Rate | Source")
            print("-" * 50)
            
            for row in rows:
                year, month, period, tufe_rate, source, created_at = row[1:7]
                month_name = datetime(year, month, 1).strftime('%b')
                print(f"{year:4} | {month:5} | {period:8} | {tufe_rate:8.2f}% | {source}")
        else:
            print("Нет сохраненных данных")
        
        conn.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    """Main function"""
    
    print("🔍 TÜFE Data Parser and Saver")
    print("=" * 40)
    print()
    
    # Check if we already have data
    if os.path.exists("data/tufe_data.db"):
        print("📊 База данных уже существует")
        show_saved_data()
        print()
        
        choice = input("Хотите обновить данные? (y/n): ").lower()
        if choice != 'y':
            print("Отменено")
            return
    
    # Parse data
    turkey_data = parse_tufe_data()
    
    if turkey_data:
        # Save data
        save_tufe_data(turkey_data)
        
        # Show saved data
        print()
        show_saved_data()
    else:
        print("❌ Не удалось получить данные")
        print()
        print("🔧 Альтернативные варианты:")
        print("-" * 30)
        print("1. Ручной ввод данных через приложение")
        print("2. Использование TCMB API (если ключ работает)")
        print("3. Веб-скрапинг с официальных сайтов")
        print("4. Использование готовых CSV файлов")

if __name__ == "__main__":
    main()
