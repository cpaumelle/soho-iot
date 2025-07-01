# Service: API Gateway

## Overview
The **API Gateway** sits at the edge, routing traffic to upstream services (ingest-server, device-manager, adminer, frontend) and handling TLS termination via Caddy.

## Components
- **unified-caddyfile** – Caddy configuration defining site blocks and reverse proxies

## Runtime & Dependencies
- **Image**: `caddy:latest` (automatic TLS via Let's Encrypt)  
- **Features**: HTTP/2, HTTP/3, static file serving, path matching

## Configuration
| File               | Path                                 | Purpose                                    |
|--------------------|--------------------------------------|--------------------------------------------|
| `unified-caddyfile`| `/etc/caddy/Caddyfile`               | Combined site definitions for all services |

Routes:
- `ingest.sensemy.cloud` → `ingest-service:8000`
- `api.sensemy.cloud` & `devices.sensemy.cloud` → `device-manager:9000`
- `adminer.sensemy.cloud` → `adminer-ui:8080`
- `app.sensemy.cloud` → static files at `/var/www/frontend`, with `/v1/*` proxy to `api.sensemy.cloud`

## Build & Deployment

### Docker Compose excerpt
```yaml
services:
  reverse-proxy:
    image: caddy:latest
    container_name: iot-reverse-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./unified-caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
      - ./refactor-frontend/src:/var/www/frontend:ro
    networks:
      - iot-network
    depends_on:
      - device-manager
      - ingest-service
      - adminer
    restart: unless-stopped
    Logging & Monitoring
  • Caddy logs: stdout (Docker logs)
  • Access logs: default Caddy access logging (enable via Caddyfile if needed)

Commands & Snippets
# Tail gateway logs
docker logs -f iot-reverse-proxy

# Test route to ingest
curl https://ingest.sensemy.cloud/health

# Test route to API
curl https://api.sensemy.cloud/v1/status

# Test static site
curl https://app.sensemy.cloud/index.html
