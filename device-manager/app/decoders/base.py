from abc import ABC, abstractmethod
from typing import Dict, Any
import struct

class BaseDecoder(ABC):
    """Base class for payload decoders"""
    
    @abstractmethod
    def decode(self, device_model: str, payload: bytes) -> Dict[str, Any]:
        """Decode raw payload bytes into structured JSON data"""
        pass
    
    def validate_payload(self, payload: bytes) -> bool:
        """Basic payload validation"""
        return len(payload) > 0
