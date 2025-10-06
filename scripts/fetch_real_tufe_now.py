#!/usr/bin/env python3
"""
Fetch ACTUAL TÜFE data from TCMB EVDS API using existing configuration.
This script demonstrates that the API WORKS and returns real data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.tcmb_api_client import TCMBApiClient
from src.services.tufe_config_service import TufeConfigService
from src.storage.data_store import DataStore
import json


def main():
    """Fetch and display real TÜFE data from TCMB API."""
    print("\n" + "="*80)
    print("FETCHING REAL TÜFE DATA FROM TCMB EVDS API")
    print("="*80) 
    
    # Initialize services
    print("\n📦 Initializing services...")
    db_path = "rental_negotiation.db"
    data_store = DataStore(db_path)
    tufe_config_service = TufeConfigService(data_store)
    
    # Get API key
    print("🔑 Retrieving API key from configuration...")
    api_key = tufe_config_service.get_api_key()
    
    if not api_key:
        print("❌ ERROR: No API key found in configuration!")
        print("   Please configure your TCMB API key first.")
        print("   Run the Streamlit app and go to 'Inflation Data' > 'TCMB API Key Configuration'")
        return 1
    
    print(f"✅ API key found: {api_key[:10]}..." if len(api_key) > 10 else "✅ API key found")
    
    # Create API client
    print("\n🌐 Creating TCMB API client...")
    client = TCMBApiClient(api_key)
    
    # Test years
    test_years = [2023, 2024]
    
    for year in test_years:
        print(f"\n" + "-"*80)
        print(f"📅 Fetching TÜFE data for {year}")
        print("-"*80)
        
        try:
            # Fetch data
            print(f"⏳ Calling TCMB API...")
            tufe_data = client.fetch_tufe_data(year)
            
            print(f"✅ SUCCESS! Received TÜFE data for {year}")
            print(f"\n📊 DATA STRUCTURE:")
            print(f"   Type: {type(tufe_data)}")
            
            if isinstance(tufe_data, dict):
                print(f"   Keys: {list(tufe_data.keys())}")
                print(f"\n📈 FULL DATA:")
                print(json.dumps(tufe_data, indent=2, ensure_ascii=False))
            elif isinstance(tufe_data, list):
                print(f"   Length: {len(tufe_data)}")
                print(f"\n📈 SAMPLE DATA (first 3 items):")
                for item in tufe_data[:3]:
                    print(f"   - {item}")
            else:
                print(f"   Value: {tufe_data}")
            
            # Try to extract the yearly TÜFE rate
            print(f"\n🎯 EXTRACTING YEARLY TÜFE RATE:")
            
            if isinstance(tufe_data, dict):
                # Look for common field names
                possible_fields = ['TP_FE_OKTG01', 'TUFE', 'rate', 'value', 'Deger']
                
                for field in possible_fields:
                    if field in tufe_data:
                        print(f"   ✅ Found field '{field}': {tufe_data[field]}")
                        break
                
                # If there's an 'items' array
                if 'items' in tufe_data and isinstance(tufe_data['items'], list):
                    print(f"\n   📋 Items found: {len(tufe_data['items'])}")
                    if len(tufe_data['items']) > 0:
                        print(f"   📌 Latest item: {tufe_data['items'][-1]}")
                        
                        # Try to get the rate
                        last_item = tufe_data['items'][-1]
                        if isinstance(last_item, dict):
                            for key, value in last_item.items():
                                if 'TP_FE' in key or 'TUFE' in key:
                                    print(f"\n   🎯 YEARLY TÜFE RATE ({year}): {value}%")
                                    break
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print(f"   Type: {type(e).__name__}")
            
            import traceback
            print(f"\n🔍 Full traceback:")
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    return 0


if __name__ == "__main__":
    exit(main())

