import os
import httpx
import logging

DEVICE_MANAGER_URL = os.getenv("DEVICE_MANAGER_URL", "http://device-manager:9000/process-uplink")
DEVICE_MANAGER_API_KEY = os.getenv("DEVICE_MANAGER_API_KEY", "supersecrettoken123")

async def forward_uplink_to_device_manager(data: dict) -> bool:
    """
    Forward a JSON uplink payload to the device-manager service.
    Returns True if forwarding succeeds, False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                DEVICE_MANAGER_URL,
                headers={"x-api-key": DEVICE_MANAGER_API_KEY},
                json=data
            )
            response.raise_for_status()
            logging.info(f"Successfully forwarded uplink for device {data.get('deveui')}")
            return True
    except Exception as e:
        logging.warning(f"Failed to forward uplink for {data.get('deveui')}: {e}")
        return False
