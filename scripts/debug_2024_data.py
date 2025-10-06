#!/usr/bin/env python3
"""
Debug 2024 data from OECD API
"""

import requests
import xml.etree.ElementTree as ET

def debug_2024_data():
    """Debug 2024 data from OECD API"""
    
    print("🔍 Debugging 2024 data from OECD API...")
    print()
    
    # OECD API endpoint for Turkey CPI data - 2024 only
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        print(f"📡 Requesting: {url}")
        response = requests.get(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        print(f"Response length: {len(response.text):,} bytes")
        print()
        
        if response.status_code == 200:
            print("✅ Success! Parsing XML...")
            
            # Try to parse the XML
            try:
                root = ET.fromstring(response.text)
                print(f"Root element: {root.tag}")
                print(f"Root attributes: {root.attrib}")
                
                # Find all observations
                observations = root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs')
                print(f"Found {len(observations)} observations")
                
                # Check for Turkey 2024 data
                turkey_2024_count = 0
                for obs in observations:
                    obs_key = obs.find('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsKey')
                    if obs_key is not None:
                        # Extract dimensions
                        dimensions = {}
                        for value in obs_key.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Value'):
                            dim_id = value.get('id')
                            dim_value = value.get('value')
                            dimensions[dim_id] = dim_value
                        
                        # Check if this is Turkey 2024 data
                        if (dimensions.get('REF_AREA') == 'TUR' and 
                            dimensions.get('TIME_PERIOD', '').startswith('2024')):
                            turkey_2024_count += 1
                
                print(f"Found {turkey_2024_count} Turkey 2024 observations")
                
                if turkey_2024_count > 0:
                    print("✅ Turkey 2024 data is available!")
                else:
                    print("❌ No Turkey 2024 data found")
                    
            except ET.ParseError as e:
                print(f"❌ XML parsing error: {e}")
                print("Response preview:")
                print(response.text[:500])
                
        else:
            print(f"❌ API request failed: {response.status_code}")
            print("Response preview:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_2024_data()
