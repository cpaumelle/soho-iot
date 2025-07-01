from .base import BaseDecoder
import struct

class UtilitiesDecoder(BaseDecoder):
   """Decoder for utility/infrastructure devices"""
   
   def decode(self, device_model: str, payload: bytes) -> dict:
       """Convert hex payload to readable JSON for utility devices"""
       if not self.validate_payload(payload):
           return {"error": "Invalid payload", "raw": payload.hex()}
       
       device_model = device_model.upper()
       
       if device_model == 'ALW8':
           return self._decode_alw8(payload)
       else:
           return {"error": f"Unknown device model: {device_model}", "raw": payload.hex()}
   
   def _decode_alw8(self, payload: bytes) -> dict:
       """Atim LoRaWAN Network Tester decoder"""
       if len(payload) < 4:
           return {"error": "Payload too short for ALW8", "raw": payload.hex()}
       
       try:
           rssi, snr, battery, status = struct.unpack('>bbBB', payload[:4])
           
           result = {
               "rssi_dbm": rssi,
               "snr_db": snr,
               "battery_voltage": battery / 10.0,
               "gps_fix": bool(status & 0x01),
               "network_status": bool(status & 0x02),
               "status_byte": status
           }
           
           # Add GPS coordinates if payload is long enough and GPS fix is available
           if len(payload) >= 12 and result["gps_fix"]:
               lat_raw, lon_raw = struct.unpack('>ii', payload[4:12])
               result["latitude"] = lat_raw / 1e6
               result["longitude"] = lon_raw / 1e6
           
           return result
           
       except struct.error:
           return {"error": "Failed to decode ALW8 payload", "raw": payload.hex()}
