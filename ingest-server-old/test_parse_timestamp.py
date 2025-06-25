from datetime import datetime

def parse_timestamp(timestamp_str):
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        print(f"✅ Parsed: {timestamp} ({type(timestamp)})")
        return timestamp
    except Exception as e:
        print(f"❌ Failed to parse '{timestamp_str}': {e}")
        return None

# Test cases
parse_timestamp("2025-06-24T21:01:00Z")               # UTC Zulu time
parse_timestamp("2025-06-24T21:01:00+00:00")          # already tz-aware
parse_timestamp("2025-06-24 21:01:00")                # space instead of 'T'
parse_timestamp("invalid-time")                       # junk
