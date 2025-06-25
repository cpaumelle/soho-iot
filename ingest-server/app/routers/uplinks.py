from fastapi import APIRouter, Request, HTTPException
import httpx
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

DEVICE_MANAGER_URL = os.environ.get("DEVICE_MANAGER_URL", "http://device-manager:9000/process-uplink")
DEVICE_MANAGER_API_KEY = os.environ.get("DEVICE_MANAGER_API_KEY", "supersecrettoken123")

@router.post("/forward-uplink")
async def forward_uplink(request: Request):
    """Forward uplink data to the device manager service"""
    try:
        logger.info("Forwarding uplink to device manager")
        
        # Try to get JSON data
        try:
            data = await request.json()
            uplink = data.get("DevEUI_uplink", data)
        except Exception:
            # If no JSON, create from query parameters
            query_params = dict(request.query_params)
            uplink = {
                "DevEUI": query_params.get("LrnDevEui") or query_params.get("DevEUI"),
                "Time": query_params.get("Time"),
                "LrnFPort": query_params.get("LrnFPort"),
                "LrnInfos": query_params.get("LrnInfos"),
                "AS_ID": query_params.get("AS_ID"),
                "Token": query_params.get("Token")
            }
        
        deveui = uplink.get("DevEUI")
        if not deveui:
            raise ValueError("Missing DevEUI in payload")
        
        logger.info(f"Forwarding uplink for device {deveui} to {DEVICE_MANAGER_URL}")
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                DEVICE_MANAGER_URL,
                headers={"x-api-key": DEVICE_MANAGER_API_KEY},
                json=uplink
            )
            resp.raise_for_status()
            
        logger.info(f"Successfully forwarded uplink for device {deveui}")
        return {"status": "forwarded", "device_eui": deveui}
        
    except Exception as e:
        logger.error(f"Forwarding error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def router_health_check():
    return {"status": "healthy", "service": "uplinks-router"}
