# pi3-fr-dnr Ingest Deployment

This document describes the setup and deployment of the ingest service running on the `pi3-fr-dnr` Raspberry Pi. The stack is responsible for ingesting uplink messages via HTTP and storing them in PostgreSQL.

## 📦 Stack Components

- **ingest-service** (FastAPI app)
  - Endpoint: `POST /uplink`
  - Extracts LoRaWAN query parameters and stores raw uplinks in the database.
  - Docker image: `ghcr.io/cpaumelle/ingest-server:latest`

- **PostgreSQL**
  - Container name: `ingest-database`
  - Credentials:
    - Database: `ingest_db`
    - User: `ingestuser`
    - Password: `ingestpass`
  - Data volume: `ingest_db_data`

- **Caddy reverse proxy**
  - Serves HTTP(S) on ports `80` and `443`
  - Config file: `caddy_config/Caddyfile`
  - Docker image: `caddy:latest`

- **Adminer (optional)**
  - UI for inspecting the DB at `http://<pi-ip>:8080`

## 🧪 Test Commands

Test uplink ingest with:

```bash
curl -X POST "http://localhost:8000/uplink?LrnDevEui=0004A30B00FB6713&LrnFPort=1&LrnInfos=test&AS_ID=test&Time=2025-06-24T10:00:00Z&Token=dummytoken" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Check database with:

```bash
docker exec -it ingest-database psql -U ingestuser -d ingest_db -c "SELECT * FROM raw_uplinks;"
```

## 🗃️ Database Schema

### `raw_uplinks`

```sql
CREATE TABLE IF NOT EXISTS raw_uplinks (
    id SERIAL PRIMARY KEY,
    deveui TEXT NOT NULL,
    received_at TIMESTAMPTZ DEFAULT now(),
    payload JSONB NOT NULL
);
```

Located in: `ingest-server/init_raw_uplinks.sql`

## 🐳 Docker Compose

See `docker-compose.yml` for full config.

Volumes:
- `caddy_config/` must be a directory containing `Caddyfile`
- `caddy_data`, `caddy_internal_config`, `ingest_db_data`

Network:
- Custom: `verdegris-iot-network-pi3-fr-dnr`

## 🏷️ Git Tag

This version was tagged as:

```
pi3-fr-dnr-20250625
```

Use this tag for future reference or redeployment.
