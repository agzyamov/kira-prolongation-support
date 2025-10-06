#!/usr/bin/env python3
"""
Test script to validate ACTUAL TÜFE data retrieval from sources.
This script attempts to retrieve real inflation data, not just test connectivity.
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re


def test_tcmb_evds_with_key(api_key=None):
    """Test TCMB EVDS API with an actual API key to retrieve TÜFE data."""
    print("\n" + "="*80)
    print("Testing TCMB EVDS API - ACTUAL DATA RETRIEVAL")
    print("="*80)
    
    if not api_key:
        print("\n⚠️ No API key provided. Testing with public endpoints...")
        api_key = "test_key"
    else:
        print(f"\n✅ Using provided API key: {api_key[:10]}...")
    
    # TCMB EVDS API endpoint for TÜFE (CPI) data
    # Series: TP.FE.OKTG01 = TÜFE Yıllık Değişim (Annual CPI Change)
    base_url = "https://evds2.tcmb.gov.tr/service/evds/"
    
    # Try different endpoint formats
    endpoints = [
        {
            'name': 'JSON format with key',
            'url': f"{base_url}series=TP.FE.OKTG01&startDate=01-01-2023&endDate=31-12-2023&type=json&key={api_key}"
        },
        {
            'name': 'XML format with key',
            'url': f"{base_url}series=TP.FE.OKTG01&startDate=01-01-2023&endDate=31-12-2023&type=xml&key={api_key}"
        },
        {
            'name': 'Alternative format',
            'url': f"https://evds2.tcmb.gov.tr/service/evds/TP.FE.OKTG01/01-01-2023/31-12-2023/?type=json&key={api_key}"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url'].replace(api_key, 'XXX')}")
        
        try:
            response = requests.get(endpoint['url'], timeout=10)
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   📦 Content-Type: {response.headers.get('Content-Type')}")
                
                # Try to parse JSON
                try:
                    data = response.json()
                    print(f"   ✅ Valid JSON received!")
                    print(f"   📊 Response structure:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                    
                    # Look for TÜFE data
                    if isinstance(data, dict):
                        if 'items' in data and len(data['items']) > 0:
                            print(f"   ✅ FOUND TÜFE DATA!")
                            print(f"   📈 Data points: {len(data['items'])}")
                            print(f"   📅 Sample data: {data['items'][0]}")
                            return True
                        elif 'Tarih' in str(data) or 'TP_FE_OKTG01' in str(data):
                            print(f"   ✅ FOUND TÜFE DATA!")
                            return True
                    
                    print(f"   ⚠️ JSON received but no TÜFE data found")
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️ Response is not JSON")
                    print(f"   📄 Response preview: {response.text[:500]}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:300]}")
                
        except requests.RequestException as e:
            print(f"   ❌ Connection error: {e}")
    
    return False


def test_tcmb_website_scraping():
    """Test web scraping TÜFE data from TCMB website."""
    print("\n" + "="*80)
    print("Testing TCMB Website - WEB SCRAPING")
    print("="*80)
    
    # TCMB inflation data page
    url = "https://www.tcmb.gov.tr/wps/wcm/connect/tr/tcmb+tr/main+menu/istatistikler/enflasyon+verileri/"
    
    print(f"\n📍 URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for TÜFE data in tables
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            # Look for specific TÜFE keywords
            text = soup.get_text()
            tufe_pattern = r'TÜFE.*?(\d+[.,]\d+)'
            matches = re.findall(tufe_pattern, text, re.IGNORECASE)
            
            if matches:
                print(f"✅ FOUND TÜFE DATA via scraping!")
                print(f"   📈 Sample values found: {matches[:5]}")
                return True
            else:
                print(f"⚠️ Page loaded but no TÜFE data patterns found")
                
                # Look for any percentage values
                percent_pattern = r'(\d+[.,]\d+)\s*%'
                percent_matches = re.findall(percent_pattern, text)
                if percent_matches:
                    print(f"   📊 Percentage values found: {percent_matches[:5]}")
                    print(f"   ℹ️ TÜFE data may be available but pattern needs refinement")
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False


def test_tuik_website_scraping():
    """Test web scraping TÜFE data from TÜİK website."""
    print("\n" + "="*80)
    print("Testing TÜİK Website - WEB SCRAPING")
    print("="*80)
    
    # TÜİK CPI bulletin URL (December 2023 example)
    url = "https://data.tuik.gov.tr/Bulten/Index?p=Tuketici-Fiyat-Endeksi-Aralik-2023-49656"
    
    print(f"\n📍 URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for inflation rate in the bulletin
            text = soup.get_text()
            
            # Pattern for yearly inflation rate
            patterns = [
                r'[Yy]ıllık.*?%\s*(\d+[.,]\d+)',
                r'annual.*?(\d+[.,]\d+)\s*%',
                r'TÜFE.*?(\d+[.,]\d+)',
                r'(\d+[.,]\d+)\s*%.*?yıllık'
            ]
            
            found_data = False
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"✅ FOUND TÜFE DATA via pattern: {pattern}")
                    print(f"   📈 Values: {matches[:5]}")
                    found_data = True
                    break
            
            if found_data:
                return True
            else:
                print(f"⚠️ Page loaded but no TÜFE data patterns found")
                
                # Show sample text
                sentences = [s.strip() for s in text.split('.') if 'tüfe' in s.lower() or 'enflasyon' in s.lower()]
                if sentences:
                    print(f"   📄 Sample sentences with keywords:")
                    for sent in sentences[:3]:
                        print(f"      - {sent[:100]}...")
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False


def main():
    """Run comprehensive TÜFE data retrieval tests."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TÜFE DATA RETRIEVAL TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Goal: Verify that we can actually retrieve TÜFE data (not just test connectivity)")
    
    results = {
        'tcmb_api': False,
        'tcmb_scraping': False,
        'tuik_scraping': False
    }
    
    # Test 1: TCMB EVDS API
    print("\n" + "-"*80)
    print("TEST 1: TCMB EVDS API")
    print("-"*80)
    print("⚠️ NOTE: You need a valid API key from https://evds2.tcmb.gov.tr/")
    print("         Without it, this test will fail (expected behavior)")
    
    # Check if user has API key in environment
    import os
    api_key = os.getenv('TCMB_API_KEY')
    
    if api_key:
        print(f"✅ Found API key in environment variable TCMB_API_KEY")
        results['tcmb_api'] = test_tcmb_evds_with_key(api_key)
    else:
        print("ℹ️ No API key found. Set TCMB_API_KEY environment variable to test.")
        print("   Example: export TCMB_API_KEY='your-key-here'")
        results['tcmb_api'] = test_tcmb_evds_with_key()
    
    # Test 2: TCMB Website Scraping
    print("\n" + "-"*80)
    print("TEST 2: TCMB Website Scraping")
    print("-"*80)
    results['tcmb_scraping'] = test_tcmb_website_scraping()
    
    # Test 3: TÜİK Website Scraping
    print("\n" + "-"*80)
    print("TEST 3: TÜİK Website Scraping")
    print("-"*80)
    results['tuik_scraping'] = test_tuik_website_scraping()
    
    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS - CAN WE GET ACTUAL TÜFE DATA?")
    print("="*80)
    
    print("\n📊 Test Results:")
    print(f"   {'✅' if results['tcmb_api'] else '❌'} TCMB EVDS API: {'SUCCESS' if results['tcmb_api'] else 'FAILED (needs valid API key)'}")
    print(f"   {'✅' if results['tcmb_scraping'] else '❌'} TCMB Web Scraping: {'SUCCESS' if results['tcmb_scraping'] else 'FAILED'}")
    print(f"   {'✅' if results['tuik_scraping'] else '❌'} TÜİK Web Scraping: {'SUCCESS' if results['tuik_scraping'] else 'FAILED'}")
    
    working_sources = sum(results.values())
    print(f"\n📈 Working Sources: {working_sources}/3")
    
    print("\n💡 RECOMMENDATIONS:")
    if results['tcmb_api']:
        print("   ✅ TCMB EVDS API works - USE THIS as primary source")
    else:
        print("   ⚠️ TCMB EVDS API needs valid key - Get one from https://evds2.tcmb.gov.tr/")
    
    if results['tcmb_scraping']:
        print("   ✅ TCMB web scraping works - Can use as fallback")
    else:
        print("   ⚠️ TCMB web scraping failed - May need pattern refinement")
    
    if results['tuik_scraping']:
        print("   ✅ TÜİK web scraping works - Can use as additional fallback")
    else:
        print("   ⚠️ TÜİK web scraping failed - May need pattern refinement")
    
    if not any(results.values()):
        print("\n❌ CRITICAL: No working data sources found!")
        print("   Action: Get TCMB API key or refine web scraping patterns")
        return 1
    else:
        print("\n✅ At least one data source is working!")
        return 0


if __name__ == "__main__":
    exit(main())

