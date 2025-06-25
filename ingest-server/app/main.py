from fastapi import FastAPI, HTTPException, Request
import psycopg2
import os
import json
import logging
import httpx  # Added for clean forwarding
from datetime import datetime
#from app.routers import uplinks

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
#app.include_router(uplinks.router)

# Database config from environment variables
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_NAME = os.environ.get("POSTGRES_DB", "ingest")
DB_USER = os.environ.get("POSTGRES_USER", "ingestuser")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "ingestpass")

# Device manager config
DEVICE_MANAGER_URL = os.environ.get("DEVICE_MANAGER_URL", "http://device-manager:9000/process-uplink")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

async def forward_to_device_manager(uplink_data: dict) -> bool:
    """
    Clean, simple forwarding to device manager
    Based on our investigation of what device manager expects
    """
    try:
        # Extract exactly what device manager expects
        payload = {
            "DevEUI": uplink_data.get("DevEUI"),
            "Time": uplink_data.get("Time")
        }
        
        # Add optional fields if present
        if uplink_data.get("LrnFPort"):
            payload["LrnFPort"] = uplink_data.get("LrnFPort")
        if uplink_data.get("payload_hex"):
            payload["payload_hex"] = uplink_data.get("payload_hex")
        
        # Include raw payload for device manager processing
        payload["raw_payload"] = uplink_data
        
        logger.info(f"Forwarding uplink for device {payload['DevEUI']} to {DEVICE_MANAGER_URL}")
        
        # Simple, reliable HTTP POST
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                DEVICE_MANAGER_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info("Successfully forwarded to device manager")
                return True
            else:
                logger.error(f"Device manager returned {response.status_code}: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Forwarding error: {e}")
        return False

@app.post("/uplink")
async def receive_uplink(req: Request):
    try:
        logger.info(f"Received uplink request from {req.client.host if req.client else 'unknown'}")
        logger.info(f"Query params: {dict(req.query_params)}")

        # Try to read JSON body first (old format)
        try:
            body = await req.json()
            uplink = body.get("DevEUI_uplink", body)
            deveui = uplink.get("DevEUI")
            timestamp = uplink.get("Time")
            logger.info(f"JSON format - DevEUI: {deveui}, Time: {timestamp}")
        except Exception as json_error:
            logger.info(f"No JSON body, checking query parameters: {json_error}")
            body = {}
            uplink = {}
            deveui = None
            timestamp = None

        # Fall back to query parameters (Actility format)
        if not deveui:
            query_params = dict(req.query_params)
            deveui = query_params.get("LrnDevEui") or query_params.get("DevEUI")
            timestamp = query_params.get("Time")

            # Build uplink object from query parameters
            uplink = {
                "DevEUI": deveui,
                "Time": timestamp,
                "LrnFPort": query_params.get("LrnFPort"),
                "LrnInfos": query_params.get("LrnInfos"),
                "AS_ID": query_params.get("AS_ID"),
                "Token": query_params.get("Token"),
                "query_params": query_params
            }
            logger.info(f"Query param format - DevEUI: {deveui}, Time: {timestamp}")

        # Validate required fields
        if not deveui:
            logger.error("Missing DevEUI in both JSON body and query parameters")
            raise ValueError("Missing DevEUI - required in either JSON body or LrnDevEui query parameter")

        # Use current time if no timestamp provided
        if not timestamp:
            timestamp = datetime.utcnow().isoformat() + "+00:00"
            logger.info(f"No timestamp provided, using current time: {timestamp}")

        # Parse timestamp safely
        try:
            if timestamp.endswith('Z'):
                received_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            elif '+' in timestamp or timestamp.endswith('+00:00'):
                received_at = datetime.fromisoformat(timestamp)
            else:
                received_at = datetime.fromisoformat(timestamp + "+00:00")
        except Exception as time_error:
            logger.warning(f"Could not parse timestamp '{timestamp}': {time_error}")
            received_at = datetime.utcnow()

        # Store the entire uplink JSON
        logger.info(f"Storing uplink for device {deveui}")
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO raw_uplinks (deveui, received_at, payload) VALUES (%s, %s, %s)",
                    (deveui, received_at, json.dumps(uplink))
                )

        logger.info(f"Successfully stored uplink for device {deveui}")

        # CLEAN FORWARDING - Replace broken code
        try:
            success = await forward_to_device_manager(uplink)
            if success:
                logger.info("Successfully forwarded to device manager")
            else:
                logger.warning("Forwarding to device manager failed")
        except Exception as fe:
            logger.warning(f"Forwarding error: {fe}")

        return {"status": "stored-and-forwarded", "device_eui": deveui}

    except Exception as e:
        logger.error(f"Error processing uplink: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/uplink/raw/{deveui}")
async def get_raw_uplink(deveui: str):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, received_at, payload FROM raw_uplinks WHERE deveui = %s ORDER BY received_at DESC LIMIT 100",
                    (deveui,)
                )
                rows = cur.fetchall()
        return [
            {"id": r[0], "received_at": r[1].isoformat(), "payload": r[2]}
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ingest-server"}
