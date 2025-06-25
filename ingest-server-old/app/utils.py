from datetime import datetime
import logging

logger = logging.getLogger("uplink-utils")

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parses ISO 8601 timestamp, handling Zulu time"""
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except Exception as e:
        logger.error(f"❌ Invalid timestamp format: '{timestamp_str}' - {e}")
        raise
