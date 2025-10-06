#!/usr/bin/env python3
"""
Check OECD API rate limits and when we might be unbanned
"""

import requests
import time
from datetime import datetime, timedelta

def check_oecd_rate_limits():
    """Check OECD API rate limits and status"""
    
    print("🔍 Проверка ограничений OECD API")
    print("=" * 50)
    print()
    
    print("❓ Вопрос: Когда нас разбанят после ошибки 429?")
    print()
    
    print("📊 **Анализ ошибки 429 (Too Many Requests):**")
    print("-" * 50)
    print()
    
    print("1️⃣ **Что означает ошибка 429:**")
    print("   • Превышен лимит запросов к OECD API")
    print("   • API временно заблокировал наш IP адрес")
    print("   • Это защита от злоупотреблений")
    print()
    
    print("2️⃣ **Типичные лимиты OECD API:**")
    print("   • ~100-1000 запросов в час")
    print("   • ~10000 запросов в день")
    print("   • Ограничения на большие объемы данных")
    print("   • Блокировка на 1-24 часа")
    print()
    
    print("3️⃣ **Когда нас разбанят:**")
    print("   • Обычно через 1-24 часа")
    print("   • Зависит от политики OECD")
    print("   • Может быть навсегда для злоупотреблений")
    print()
    
    print("🕐 **Проверим текущий статус API:**")
    print("-" * 40)
    
    # Try a simple request to check if we're still banned
    test_urls = [
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-01",
        "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2023-01&endTime=2023-01",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}️⃣ Тестируем запрос {i}:")
        print(f"   URL: {url[:80]}...")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ API работает! Мы разбанены!")
                break
            elif response.status_code == 429:
                print("   ❌ Все еще забанены (429)")
                print("   Сообщение:", response.text[:100])
            elif response.status_code == 403:
                print("   ❌ Запрещено (403)")
            else:
                print(f"   ⚠️  Неожиданный статус: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Wait between requests
        time.sleep(2)
    
    print()
    print("📋 **Рекомендации:**")
    print("-" * 20)
    print()
    
    print("1️⃣ **Если все еще забанены:**")
    print("   • Подождать 1-24 часа")
    print("   • Использовать VPN для смены IP")
    print("   • Обратиться в OECD через форму обратной связи")
    print()
    
    print("2️⃣ **Альтернативные источники данных:**")
    print("   • TCMB EVDS API (если ключ работает)")
    print("   • TÜİK официальный сайт")
    print("   • Trading Economics API")
    print("   • World Bank API")
    print()
    
    print("3️⃣ **Для вашего приложения:**")
    print("   • Добавить кэширование данных")
    print("   • Использовать несколько источников")
    print("   • Добавить обработку ошибок 429")
    print("   • Реализовать retry с экспоненциальной задержкой")
    print()
    
    print("⏰ **Время проверки:**")
    print(f"   Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Следующая проверка: {(datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("🔗 **Полезные ссылки:**")
    print("   • OECD Data Explorer: https://data-explorer.oecd.org")
    print("   • OECD API Documentation: https://data-explorer.oecd.org/vis?fs[0]=Topic%2C1%7C1%7C1%7C1")
    print("   • OECD Feedback Form: https://data-explorer.oecd.org/vis?fs[0]=Topic%2C1%7C1%7C1%7C1")

if __name__ == "__main__":
    check_oecd_rate_limits()
