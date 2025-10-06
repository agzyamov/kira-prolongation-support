#!/usr/bin/env python3
"""
Examine OECD XML response structure
"""

import requests
import xml.etree.ElementTree as ET

def examine_xml():
    """Examine the XML structure"""
    
    url = "https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/PRICES_CPI/A.TUR.CPALTT01.M/all?startTime=2024-01&endTime=2024-12"
    
    try:
        response = requests.get(url, timeout=30)
        root = ET.fromstring(response.text)
        
        print("🔍 Examining XML structure...")
        print()
        
        # Print the root element and its children
        print(f"Root element: {root.tag}")
        print(f"Root attributes: {root.attrib}")
        print()
        
        # Find all elements with 'Series' in the tag
        series_elements = []
        for elem in root.iter():
            if 'Series' in elem.tag:
                series_elements.append(elem)
        
        print(f"Found {len(series_elements)} Series elements")
        
        # Look for any elements containing 'TUR' or 'Turkey'
        tur_elements = []
        for elem in root.iter():
            if elem.text and ('TUR' in elem.text or 'Turkey' in elem.text):
                tur_elements.append(elem)
        
        print(f"Found {len(tur_elements)} elements containing 'TUR' or 'Turkey'")
        
        # Look for data elements
        data_elements = []
        for elem in root.iter():
            if 'Obs' in elem.tag or 'Data' in elem.tag:
                data_elements.append(elem)
        
        print(f"Found {len(data_elements)} data elements")
        
        # Print first few elements to understand structure
        print("\n📊 First few elements:")
        count = 0
        for elem in root.iter():
            if count < 20:
                print(f"  {elem.tag}: {elem.attrib}")
                if elem.text and len(elem.text.strip()) > 0:
                    print(f"    Text: {elem.text[:100]}...")
                count += 1
            else:
                break
        
        # Try to find any numeric values
        print("\n🔢 Looking for numeric values...")
        numeric_values = []
        for elem in root.iter():
            if elem.text and elem.text.strip().replace('.', '').replace('-', '').isdigit():
                numeric_values.append(elem.text)
                if len(numeric_values) >= 10:
                    break
        
        print(f"Found numeric values: {numeric_values}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    examine_xml()
