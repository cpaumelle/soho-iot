#!/usr/bin/env python3
"""
consumer.py

One-shot (or loop) poller from ingest.raw_uplinks → devices.uplinks.
Persists last_id in last_id.txt so cron runs only do new rows.
"""

import time
import argparse
import os
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

# —————————————————————————————
# CONFIG
INGEST_DB_URL   = "postgresql://ingestuser:ingestpass@127.0.0.1:5432/ingest"
# DEVICE_DB_URL   = "postgresql://iot:secret@127.0.0.1:5433/device_db"
STATE_FILE      = "last_id.txt"  # in same folder as this script
POLL_INTERVAL   = 5              # seconds, if you ever run continuous

# —————————————————————————————
# DB SETUP
ingest_engine = create_engine(INGEST_DB_URL)
device_engine = create_engine(DEVICE_DB_URL)
IngestSession = sessionmaker(bind=ingest_engine)
DeviceSession = sessionmaker(bind=device_engine)

# Reflect tables
ingest_meta = MetaData()
raw_uplinks = Table("raw_uplinks", ingest_meta, autoload_with=ingest_engine, schema="public")

device_meta = MetaData()
device_defs = Table("devices", device_meta, autoload_with=device_engine, schema="devices")
uplinks     = Table("uplinks",  device_meta, autoload_with=device_engine, schema="devices")

# —————————————————————————————
def load_last_id():
    if os.path.isfile(STATE_FILE):
        try:
            return int(open(STATE_FILE).read().strip())
        except ValueError:
            pass
    return 0

def save_last_id(last_id):
    with open(STATE_FILE, "w") as f:
        f.write(str(last_id))

def run_worker(run_once=False):
    last_id = load_last_id()

    while True:
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] Polling (last_id={last_id})", flush=True)

        # fetch new raw uplinks
        with IngestSession() as ingest_s:
            rows = ingest_s.execute(
                select(raw_uplinks)
                .where(raw_uplinks.c.id > last_id)
                .order_by(raw_uplinks.c.id)
            ).fetchall()

        if rows:
            print(f"[{ts}]   → Found {len(rows)} new", flush=True)
            with DeviceSession() as device_s:
                for row in rows:
                    # ensure device record exists
                    device_s.execute(
                        insert(device_defs)
                        .values(deveui=row.deveui)
                        .on_conflict_do_nothing(index_elements=["deveui"])
                    )
                    # insert uplink record
                    device_s.execute(
                        insert(uplinks)
                        .values(
                            id=row.id,
                            deveui=row.deveui,
                            received_at=row.received_at,
                            payload=row.payload,
                        )
                        .on_conflict_do_nothing(index_elements=["id"])
                    )
                    last_id = max(last_id, row.id)

                device_s.commit()
            print(f"[{ts}]   → Inserted up to id {last_id}", flush=True)

            # persist state
            save_last_id(last_id)

        if run_once:
            print(f"[{ts}] Exiting after one pass (--once)", flush=True)
            break

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="do one pass then exit")
    args = parser.parse_args()
    run_worker(run_once=args.once)
