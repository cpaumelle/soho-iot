"""
Analytics Forwarder for Device Manager
Forwards processed uplinks to Analytics Processor v2 via HTTP
Version: 1.0.1
Updated: 2025-07-01T16:27:00Z (UTC)
"""

import httpx
import os
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import time

logger = logging.getLogger("device_manager.analytics_forwarder")

class AnalyticsForwarder:
    """Forwards processed uplinks to Analytics Processor v2 via HTTP"""
    
    def __init__(self, analytics_url: str = None):
        if analytics_url is None:
            analytics_url = os.getenv("ANALYTICS_URL", "http://analytics-processor:7000")
        self.analytics_url = analytics_url
        self.endpoint = f"{self.analytics_url}/v1/analytics/process-uplink"
        self.health_endpoint = f"{self.analytics_url}/health"
                
        # Forwarding statistics
        self.stats = {
            "total_forwarded": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time_ms": 0,
            "last_success": None,
            "last_failure": None
        }
        
        # HTTP client configuration
        self.http_client = None
        self.timeout = httpx.Timeout(5.0, connect=2.0)
        
    async def initialize(self):
        """Initialize the analytics forwarder"""
        logger.info("🔗 Initializing Analytics Forwarder")
        
        try:
            # Create HTTP client with connection pooling
            self.http_client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
            
            # Skip connectivity test during startup - will test during actual forwarding
            logger.info("📝 Skipping connectivity test during startup")
            
            logger.info("✅ Analytics forwarder initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Analytics connectivity test failed: {e}")
            logger.info("📝 Analytics forwarder will continue without initial connectivity test")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("🔄 Analytics Forwarder cleanup complete")
    
    async def test_connectivity(self):
        """Test connectivity to Analytics Processor v2"""
        try:
            response = await self.http_client.get(self.health_endpoint)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Analytics Processor health: {health_data.get('status', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️ Analytics Processor responded with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Analytics Processor connectivity test failed: {e}")
            return False
    
    async def forward_uplink(self, uplink_data: Dict[str, Any], device_context: Dict[str, Any]) -> bool:
        """Forward processed uplink to Analytics Processor v2"""
        start_time = time.time()
        
        try:
            # Prepare analytics payload
            analytics_payload = {
                "uplink": {
                    "id": uplink_data.get("id", "unknown"),
                    "timestamp": uplink_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
                    "payload_json": uplink_data.get("payload_json", uplink_data.get("decoded_data", {})),
                    "device_id": uplink_data.get("device_id", device_context.get("deveui", "unknown"))
                },
                "device": {
                    "deveui": device_context.get("deveui", "unknown"),
                    "name": device_context.get("name", "Unknown Device"),
                    "device_type_id": device_context.get("device_type_id", 1),
                    "zone_id": device_context.get("zone_id", 1),
                    "device_type_name": device_context.get("device_type_name"),
                    "manufacturer": device_context.get("manufacturer"),
                    "model": device_context.get("model")
                },
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            # Forward to analytics processor
            response = await self.http_client.post(
                self.endpoint,
                json=analytics_payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats["total_forwarded"] += 1
            
            if response.status_code == 200:
                self.stats["successful"] += 1
                self.stats["last_success"] = datetime.utcnow()
                self._update_avg_response_time(response_time)
                
                logger.debug(f"✅ Analytics forwarded successfully for {device_context.get('deveui')} in {response_time:.1f}ms")
                return True
                
            else:
                self.stats["failed"] += 1
                self.stats["last_failure"] = datetime.utcnow()
                
                logger.warning(f"⚠️ Analytics forwarding failed for {device_context.get('deveui')}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.stats["failed"] += 1
            self.stats["last_failure"] = datetime.utcnow()
            
            logger.error(f"❌ Analytics forwarding error for {device_context.get('deveui')}: {e}")
            return False
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time with exponential moving average"""
        if self.stats["avg_response_time_ms"] == 0:
            self.stats["avg_response_time_ms"] = response_time
        else:
            self.stats["avg_response_time_ms"] = (
                0.9 * self.stats["avg_response_time_ms"] + 
                0.1 * response_time
            )
    
    async def forward_uplink_background(self, uplink_data: Dict[str, Any], device_context: Dict[str, Any]):
        """Forward uplink in background task - non-blocking"""
        try:
            await self.forward_uplink(uplink_data, device_context)
        except Exception as e:
            logger.error(f"Background analytics forwarding failed: {e}")
            # Swallow exception to prevent affecting device processing
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get forwarding statistics"""
        stats = self.stats.copy()
        
        if stats["total_forwarded"] > 0:
            stats["success_rate"] = (stats["successful"] / stats["total_forwarded"]) * 100
        else:
            stats["success_rate"] = 0
            
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            analytics_healthy = await self.test_connectivity()
            
            return {
                "analytics_processor_healthy": analytics_healthy,
                "http_client_active": self.http_client is not None,
                "statistics": self.get_statistics()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "statistics": self.get_statistics()
            }
