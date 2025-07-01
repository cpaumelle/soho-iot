import psycopg2
import json
import os
from app.forwarder import forward_uplink_to_device_manager

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "ingest")
DB_USER = os.getenv("POSTGRES_USER", "ingestuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "ingestpass")
LAST_ID_FILE = "last_id.txt"

def get_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_last_id(last_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(last_id))

def forward_new_uplinks():
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()

    last_id = get_last_id()
    cur.execute("SELECT id, deveui, payload FROM raw_uplinks WHERE id > %s ORDER BY id ASC", (last_id,))
    rows = cur.fetchall()

    print(f"📡 Found {len(rows)} new uplinks to forward...")

    for row in rows:
        id, deveui, payload_json = row
        print(f"→ Forwarding ID {id} for device {deveui}")
        success = False
        try:
            success = asyncio.run(forward_uplink_to_device_manager(deveui, payload_json))
        except Exception as e:
            print(f"❌ Error forwarding ID {id}: {e}")
        if success:
            save_last_id(id)

    cur.close()
    conn.close()

if __name__ == "__main__":
    import asyncio
    forward_new_uplinks()
