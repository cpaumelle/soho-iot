from typing import Dict, Optional
from .environment import EnvironmentDecoder
from .monitoring import MonitoringDecoder
from .utilities import UtilitiesDecoder

class DecoderRegistry:
    """Registry for device type decoders"""
    
    def __init__(self):
        self._decoders = {
            'environment': EnvironmentDecoder(),
            'monitoring': MonitoringDecoder(), 
            'utilities': UtilitiesDecoder()
        }
    
    def decode_payload(self, device_type: str, device_model: str, payload: bytes) -> dict:
        """Decode payload using appropriate decoder for device type"""
        device_type = device_type.lower()
        
        if device_type not in self._decoders:
            return {
                "error": f"No decoder for device type: {device_type}",
                "raw": payload.hex()
            }
        
        decoder = self._decoders[device_type]
        return decoder.decode(device_model, payload)
    
    def get_supported_types(self) -> list:
        """Return list of supported device types"""
        return list(self._decoders.keys())
