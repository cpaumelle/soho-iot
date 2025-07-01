"""
Analytics API Endpoints - HTTP-based processing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.models.requests import (
    UplinkAnalyticsRequest,
    BatchProcessRequest,
    AnalyticsResponse,
    StatisticsResponse
)
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger("analytics.api")
router = APIRouter()

def get_analytics_service():
    """Dependency injection for analytics service"""
    from app.main import get_analytics_service
    return get_analytics_service()

@router.post("/process-uplink", response_model=AnalyticsResponse)
async def process_uplink(
    request: UplinkAnalyticsRequest,
    background_tasks: BackgroundTasks,
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Process a single uplink for analytics
    Real-time endpoint called by device manager
    """
    start_time = datetime.utcnow()

    try:
        logger.info(f"📊 Processing uplink analytics for device: {request.device.deveui}")

        # Process the uplink analytics
        result = await analytics_service.process_uplink(request)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"✅ Analytics processed in {processing_time:.2f}ms for {request.device.deveui}")

        return AnalyticsResponse(
            status="success",
            processing_time_ms=int(processing_time),
            analytics_results=result,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"❌ Analytics processing failed for {request.device.deveui}: {e}")

        # Return error response but don't block device processing
        return AnalyticsResponse(
            status="error",
            processing_time_ms=int(processing_time),
            error_message=str(e),
            timestamp=datetime.utcnow()
        )

@router.get("/health")
async def analytics_health_check(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Detailed health check for analytics service"""
    try:
        health = await analytics_service.detailed_health_check()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "details": health
        }
    except Exception as e:
        logger.error(f"❌ Analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.post("/test-processing")
async def test_analytics_processing(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Test endpoint for validating analytics processing with sample data - FIXED"""
    try:
        # Create test uplink data with PROPER timestamp formatting
        now = datetime.utcnow()
        timestamp_str = now.isoformat() + "+00:00"  # Proper timezone format
        
        test_uplink = UplinkAnalyticsRequest(
            uplink={
                "id": "test-uplink-001",
                "timestamp": timestamp_str,  # FIXED: No duplicate +00:00
                "payload_json": {"temperature": 23.5, "humidity": 65.2},
                "device_id": "test-device-001"
            },
            device={
                "deveui": "0000000000000001",
                "name": "Test Device",
                "device_type_id": 1,
                "zone_id": 1
            },
            processing_timestamp=timestamp_str  # FIXED: Consistent format
        )

        # Process test uplink
        result = await analytics_service.process_uplink(test_uplink)

        return {
            "status": "success",
            "message": "Analytics processing test completed",
            "test_result": result.dict(),
            "timestamp_used": timestamp_str
        }

    except Exception as e:
        logger.error(f"❌ Analytics test failed: {e}")
        return {
            "status": "error",
            "message": f"Analytics test failed: {str(e)}"
        }
