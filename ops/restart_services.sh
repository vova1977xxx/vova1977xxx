#!/usr/bin/env bash
set -euo pipefail

echo "== RESTART SERVICES ==" 

# docker compose (safe)
if [ -f docker-compose.yml ] || [ -f compose.yml ]; then
  echo "[restart] docker compose up -d"
  docker compose up -d --remove-orphans
else
  echo "[restart] docker compose skipped (no docker-compose.yml)"
fi

# systemd services (best-effort)
systemctl restart gemivas-queue-worker.service 2>/dev/null || true
systemctl restart gemivas-brain-policy.service 2>/dev/null || true
systemctl restart gemivas-orchestrator.service 2>/dev/null || true

# nginx reload
nginx -t
systemctl reload nginx

echo "== DONE ==" 
