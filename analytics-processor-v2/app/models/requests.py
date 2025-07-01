"""
Data models for analytics processing requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class DeviceContext(BaseModel):
    """Device context information"""
    deveui: str
    name: str
    device_type_id: int
    zone_id: int
    device_type_name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None

class UplinkData(BaseModel):
    """Uplink data structure"""
    id: str
    timestamp: str
    payload_json: Dict[str, Any]
    device_id: str
    processing_status: Optional[str] = None

class UplinkAnalyticsRequest(BaseModel):
    """Request for processing a single uplink"""
    uplink: UplinkData
    device: DeviceContext
    processing_timestamp: str

class BatchProcessRequest(BaseModel):
    """Request for batch processing multiple uplinks"""
    uplinks: List[UplinkAnalyticsRequest]
    batch_id: Optional[str] = None

class AnalyticsResult(BaseModel):
    """Analytics processing result"""
    device_id: str
    decoded_data: Dict[str, Any]
    normalized_data: Dict[str, Any]
    analytics_id: str
    processing_stage: str

class AnalyticsResponse(BaseModel):
    """Response from analytics processing"""
    status: str
    processing_time_ms: int
    analytics_results: Optional[AnalyticsResult] = None
    error_message: Optional[str] = None
    timestamp: datetime

class StatisticsData(BaseModel):
    """Processing statistics data"""
    total_processed: int
    successful: int
    failed: int
    avg_processing_time_ms: float
    max_processing_time_ms: int
    last_processing_time: Optional[datetime] = None

class StatisticsResponse(BaseModel):
    """Response with processing statistics"""
    period_hours: int
    statistics: StatisticsData
    timestamp: datetime

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Optional[Dict[str, Any]] = None
