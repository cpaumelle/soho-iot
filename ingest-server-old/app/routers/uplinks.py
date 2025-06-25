from fastapi import APIRouter, Request, HTTPException
from starlette.responses import JSONResponse
from datetime import datetime
import asyncpg
import logging
import json

from app.utils import parse_timestamp  # ✅ Use shared utility

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uplink-router")

# Database credentials
DB_USER = "ingestuser"
DB_PASS = "ingestpass"
DB_HOST = "postgres"
DB_NAME = "ingest"
DB_PORT = "5432"

async def save_uplink_to_db(data: dict):
    logger.info("🔌 Connecting to PostgreSQL...")
    try:
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
    except Exception as conn_error:
        logger.error(f"❌ Database connection failed: {conn_error}")
        raise

    try:
        deveui = data.get("DevEUI") or data.get("LrnDevEui")
        timestamp = parse_timestamp(data.get("Time"))
        received_at = datetime.utcnow()

        logger.info(f"📥 Inserting into raw_uplinks: deveui={deveui}, timestamp={timestamp}, received_at={received_at}")
        await conn.execute(
            """
            INSERT INTO public.raw_uplinks (deveui, timestamp, payload, received_at)
            VALUES ($1, $2, $3, $4)
            """,
            deveui,
            timestamp,
            data,
            received_at
        )
    except Exception as insert_error:
        logger.error(f"❌ Insert failed: {insert_error}")
        raise
    finally:
        await conn.close()
        logger.info("🔒 PostgreSQL connection closed")

@router.api_route("/uplink", methods=["GET", "POST"])
async def receive_uplink(request: Request):
    try:
        try:
            payload = await request.json()
            logger.info("📨 Parsed JSON body")
        except Exception:
            payload = dict(request.query_params)
            logger.info("📨 Parsed query parameters")

        deveui = payload.get("DevEUI") or payload.get("LrnDevEui")
        if not deveui:
            logger.warning("⚠️ Missing DevEUI or LrnDevEui")
            raise HTTPException(status_code=400, detail="Missing DevEUI - required in either JSON body or LrnDevEui query parameter")

        await save_uplink_to_db(payload)
        logger.info(f"✅ Successfully stored uplink for {deveui}")
        return JSONResponse(status_code=200, content={"status": "stored-and-forwarded", "device_eui": deveui})

    except Exception as e:
        logger.error(f"❌ Uplink processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
