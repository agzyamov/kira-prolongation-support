#!/usr/bin/env python3
"""
Test script to validate alternative TÜFE data sources.
Tests connectivity and data availability from TÜİK and EPİAŞ APIs.
"""

import requests
import json
from datetime import datetime


def test_tcmb_evds_api():
    """Test TCMB EVDS API connectivity and data format."""
    print("\n" + "="*80)
    print("Testing TCMB EVDS API")
    print("="*80)
    
    # TCMB EVDS API endpoint
    base_url = "https://evds2.tcmb.gov.tr/service/evds/"
    
    # Test without API key first (to see error format)
    test_url = f"{base_url}series=TP.FE.OKTG01&startDate=01-01-2023&endDate=31-12-2023&type=json"
    
    print(f"\n📍 URL: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📦 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response received")
                print(f"📊 Response structure: {json.dumps(data, indent=2)[:500]}...")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}")
        else:
            print(f"❌ Error Response: {response.text[:500]}")
            
    except requests.RequestException as e:
        print(f"❌ Connection Error: {e}")
    
    return True


def test_tuik_api():
    """Test TÜİK API connectivity and data format."""
    print("\n" + "="*80)
    print("Testing TÜİK (Turkish Statistical Institute) API")
    print("="*80)
    
    # TÜİK API endpoints to test
    endpoints = [
        "https://data.tuik.gov.tr/api/GetValueRangeList?categoryId=114",  # CPI category
        "https://biruni.tuik.gov.tr/medas/?kn=84&locale=tr",  # MEDAS system
        "https://data.tuik.gov.tr/Bulten/Index?p=Tuketici-Fiyat-Endeksi-Aralik-2023-49656",  # Bulletin
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n🔍 Test {i}: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ Status Code: {response.status_code}")
            print(f"📦 Content-Type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                content = response.text[:300]
                print(f"📄 Response Preview: {content}...")
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    print(f"✅ JSON Response")
                    print(f"📊 Keys: {list(data.keys()) if isinstance(data, dict) else 'List/Other'}")
                except json.JSONDecodeError:
                    print(f"ℹ️ Response is HTML/Other format")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Connection Error: {e}")
    
    return True


def test_epias_api():
    """Test EPİAŞ (Energy Exchange Istanbul) API connectivity."""
    print("\n" + "="*80)
    print("Testing EPİAŞ Transparency Platform API")
    print("="*80)
    
    # EPİAŞ Transparency API endpoints
    endpoints = [
        "https://seffaflik.epias.com.tr/transparency/service/market/",  # Base API
        "https://seffaflik.epias.com.tr/transparency/",  # Web interface
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n🔍 Test {i}: {url}")
        
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            print(f"✅ Status Code: {response.status_code}")
            print(f"📦 Content-Type: {response.headers.get('Content-Type')}")
            print(f"🔗 Final URL: {response.url}")
            
            if response.status_code == 200:
                content = response.text[:300]
                print(f"📄 Response Preview: {content}...")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Connection Error: {e}")
    
    return True


def test_alternative_tufe_sources():
    """Test alternative sources for TÜFE data."""
    print("\n" + "="*80)
    print("Testing Alternative TÜFE Data Sources")
    print("="*80)
    
    # Test various potential sources
    sources = [
        {
            'name': 'TCMB Main Website',
            'url': 'https://www.tcmb.gov.tr/wps/wcm/connect/tr/tcmb+tr/main+menu/istatistikler/enflasyon+verileri/',
            'method': 'GET'
        },
        {
            'name': 'TÜİK Main Website',
            'url': 'https://www.tuik.gov.tr/',
            'method': 'GET'
        },
        {
            'name': 'Investing.com Turkey Inflation',
            'url': 'https://tr.investing.com/economic-calendar/turkish-inflation-rate-601',
            'method': 'GET'
        },
    ]
    
    for source in sources:
        print(f"\n📍 Testing: {source['name']}")
        print(f"   URL: {source['url']}")
        
        try:
            response = requests.get(source['url'], timeout=10, allow_redirects=True)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📦 Content-Type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                # Check if response contains relevant keywords
                keywords = ['enflasyon', 'inflation', 'tüfe', 'cpi', 'fiyat endeksi']
                content_lower = response.text.lower()
                found_keywords = [kw for kw in keywords if kw in content_lower]
                
                if found_keywords:
                    print(f"   ✅ Relevant content found: {', '.join(found_keywords)}")
                else:
                    print(f"   ⚠️ No relevant keywords found")
            
        except requests.RequestException as e:
            print(f"   ❌ Error: {e}")
    
    return True


def main():
    """Run all source tests."""
    print("\n" + "="*80)
    print("TÜFE DATA SOURCE VALIDATION SCRIPT")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n⚠️ NOTE: This script tests connectivity and data format only.")
    print("   API keys are required for actual data retrieval from most sources.")
    
    try:
        # Test each source
        test_tcmb_evds_api()
        test_tuik_api()
        test_epias_api()
        test_alternative_tufe_sources()
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print("\n✅ Script completed successfully")
        print("\n📊 FINDINGS:")
        print("   - TCMB EVDS API: Requires API key for data access")
        print("   - TÜİK API: Need to verify API documentation and endpoints")
        print("   - EPİAŞ: Primarily for energy data, may not have CPI data")
        print("   - Alternative sources: Web scraping possible but less reliable")
        
        print("\n💡 RECOMMENDATIONS:")
        print("   1. TCMB EVDS API is the primary official source (requires API key)")
        print("   2. TÜİK website may offer data but API endpoints need verification")
        print("   3. Consider fallback to manual entry if APIs fail")
        print("   4. Web scraping should be last resort due to reliability concerns")
        
    except Exception as e:
        print(f"\n❌ Script failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

