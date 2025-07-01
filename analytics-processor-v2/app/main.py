"""
New Analytics Processor - HTTP-Based Architecture
Real-time analytics processing via HTTP endpoints
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from typing import Dict, Any

from app.api.analytics import router as analytics_router
from app.database.connections import get_analytics_db, get_ingest_db
from app.services.analytics_service import AnalyticsService
from app.models.requests import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("analytics-processor-v2")

# Global services
analytics_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global analytics_service
    
    logger.info("🚀 Starting Analytics Processor v2")
    
    try:
        # Initialize database connections
        analytics_db = get_analytics_db()
        ingest_db = get_ingest_db()
        
        # Initialize analytics service
        analytics_service = AnalyticsService(analytics_db, ingest_db)
        await analytics_service.initialize()
        
        logger.info("✅ Analytics Processor v2 initialized successfully")
        logger.info("📊 Ready to process uplinks via HTTP endpoints")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Analytics Processor: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔄 Shutting down Analytics Processor v2")
        if analytics_service:
            await analytics_service.cleanup()
        logger.info("✅ Analytics Processor v2 shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="IoT Analytics Processor v2",
    description="HTTP-based real-time analytics processing for IoT uplinks",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(analytics_router, prefix="/v1/analytics", tags=["analytics"])

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check analytics service health
        if analytics_service:
            service_health = await analytics_service.health_check()
            return HealthResponse(
                status="healthy",
                timestamp=datetime.utcnow(),
                version="2.0.0",
                services=service_health
            )
        else:
            return HealthResponse(
                status="starting",
                timestamp=datetime.utcnow(),
                version="2.0.0"
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "IoT Analytics Processor v2",
        "version": "2.0.0",
        "description": "HTTP-based real-time analytics processing",
        "endpoints": {
            "health": "/health",
            "process_uplink": "/v1/analytics/process-uplink",
            "batch_process": "/v1/analytics/batch-process",
            "statistics": "/v1/analytics/statistics"
        },
        "improvements": [
            "Real-time HTTP processing",
            "No database polling",
            "Better error handling", 
            "Structured logging",
            "Comprehensive monitoring"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error tracking"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {"error": "Internal server error", "message": str(exc)}

# Make analytics service available to routes
def get_analytics_service() -> AnalyticsService:
    """Get the global analytics service instance"""
    if analytics_service is None:
        raise HTTPException(status_code=503, detail="Analytics service not initialized")
    return analytics_service
