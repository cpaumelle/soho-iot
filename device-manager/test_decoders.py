#!/usr/bin/env python3
"""
Test script for the decoder system
"""
import sys
sys.path.append('.')

from app.decoders import decoder_registry

def test_decoders():
    print("Testing IoT Device Decoders")
    print("=" * 40)
    
    # Test cases with sample hex payloads
    test_cases = [
        {
            "name": "Environment - TBHH100",
            "device_type": "environment",
            "device_model": "TBHH100", 
            "hex_payload": "1388271005dc640a00"  # 8 bytes minimum
        },
        {
            "name": "Environment - TBHV110", 
            "device_type": "environment",
            "device_model": "TBHV110",
            "hex_payload": "019001f41388271064"  # 9 bytes minimum
        },
        {
            "name": "Monitoring - WISD",
            "device_type": "monitoring", 
            "device_model": "WISD",
            "hex_payload": "01506432"  # 4 bytes minimum
        },
        {
            "name": "Utilities - ALW8",
            "device_type": "utilities",
            "device_model": "ALW8", 
            "hex_payload": "b8051e01"  # 4 bytes minimum
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"  Input: {test_case['hex_payload']}")
        
        try:
            # Convert hex to bytes
            payload_bytes = bytes.fromhex(test_case['hex_payload'])
            
            # Decode using registry
            result = decoder_registry.decode_payload(
                device_type=test_case['device_type'],
                device_model=test_case['device_model'], 
                payload=payload_bytes
            )
            
            print(f"  Result: {result}")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    print("\n" + "=" * 40)
    print("Supported device types:", decoder_registry.get_supported_types())

if __name__ == "__main__":
    test_decoders()
