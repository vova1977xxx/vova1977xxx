#!/usr/bin/env bash
set -euo pipefail

echo "== GEMIVAS FORCE REFILL =="

echo "[1/3] clear cooldown keys"
redis-cli -h 127.0.0.1 --scan --pattern "src:seen:*" | xargs -r redis-cli -h 127.0.0.1 del >/dev/null || true

echo "[2/3] restart brain sources"
sudo systemctl restart gemivas-brain-sources.service || true

sleep 2

echo "[3/3] queue status"
echo -n "q:tasks="; redis-cli -h 127.0.0.1 llen q:tasks || true
echo -n "q:dlq=";   redis-cli -h 127.0.0.1 llen q:dlq   || true

echo "== DONE =="
