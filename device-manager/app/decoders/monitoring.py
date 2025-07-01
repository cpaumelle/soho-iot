from .base import BaseDecoder
import struct

class MonitoringDecoder(BaseDecoder):
    """Decoder for monitoring/safety devices"""
    
    def decode(self, device_model: str, payload: bytes) -> dict:
        """Convert hex payload to readable JSON for monitoring devices"""
        if not self.validate_payload(payload):
            return {"error": "Invalid payload", "raw": payload.hex()}
        
        device_model = device_model.upper()
        
        if device_model == 'WISD':
            return self._decode_wisd(payload)
        else:
            return {"error": f"Unknown device model: {device_model}", "raw": payload.hex()}
    
    def _decode_wisd(self, payload: bytes) -> dict:
        """Winext Smoke Detector decoder"""
        if len(payload) < 4:
            return {"error": "Payload too short for WISD", "raw": payload.hex()}
        
        try:
            status, battery, smoke_level, temp_raw = struct.unpack('>BBBB', payload[:4])
            
            return {
                "smoke_detected": bool(status & 0x01),
                "alarm_active": bool(status & 0x02),
                "test_mode": bool(status & 0x04),
                "battery_low": bool(status & 0x08),
                "battery_percent": battery,
                "smoke_level": smoke_level,
                "temperature_celsius": temp_raw - 50,
                "status_byte": status
            }
        except struct.error:
            return {"error": "Failed to decode WISD payload", "raw": payload.hex()}
