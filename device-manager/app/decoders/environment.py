from .base import BaseDecoder
import struct

class EnvironmentDecoder(BaseDecoder):
    """Decoder for environment monitoring devices"""
    
    def decode(self, device_model: str, payload: bytes) -> dict:
        """Convert hex payload to readable JSON for environment devices"""
        if not self.validate_payload(payload):
            return {"error": "Invalid payload", "raw": payload.hex()}
        
        device_model = device_model.upper()
        
        if device_model == 'TBHH100':
            return self._decode_tbhh100(payload)
        elif device_model == 'TBHV110':
            return self._decode_tbhv110(payload)
        else:
            return {"error": f"Unknown device model: {device_model}", "raw": payload.hex()}
    
    def _decode_tbhh100(self, payload: bytes) -> dict:
        """Browan Tabs Health Home decoder"""
        if len(payload) < 8:
            return {"error": "Payload too short for TBHH100", "raw": payload.hex()}
        
        try:
            temp_raw, hum_raw, press_raw, battery, status = struct.unpack('>HHHBB', payload[:8])
            
            return {
                "temperature_celsius": (temp_raw - 5000) / 100.0,
                "humidity_percent": hum_raw / 100.0,
                "pressure_hpa": press_raw / 10.0,
                "battery_voltage": battery / 10.0,
                "status_code": status
            }
        except struct.error:
            return {"error": "Failed to decode TBHH100 payload", "raw": payload.hex()}
    
    def _decode_tbhv110(self, payload: bytes) -> dict:
        """Browan IAQ sensor decoder"""
        if len(payload) < 9:
            return {"error": "Payload too short for TBHV110", "raw": payload.hex()}
        
        try:
            co2, tvoc, temp_raw, hum_raw, battery = struct.unpack('>HHHHB', payload[:9])
            
            return {
                "co2_ppm": co2,
                "tvoc_ppb": tvoc,
                "temperature_celsius": (temp_raw - 5000) / 100.0,
                "humidity_percent": hum_raw / 100.0,
                "battery_voltage": battery / 10.0
            }
        except struct.error:
            return {"error": "Failed to decode TBHV110 payload", "raw": payload.hex()}
