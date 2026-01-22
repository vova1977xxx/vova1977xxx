#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"
DB="/srv/gemivas_platform/data/gemivas.db"

echo "== GEMIVAS CANON VERIFY =="

cd "$ROOT"

echo "[verify] wait api"
for i in {1..20}; do
  curl -fsS -s http://127.0.0.1:9002/feed >/dev/null 2>/dev/null && break || true
  sleep 1
done
sudo ./status.sh | tail -n 60 || true

echo
echo "db tables:"
sudo sqlite3 "$DB" ".tables"

echo
echo "queue:"
redis-cli -h 127.0.0.1 llen q:tasks || true
redis-cli -h 127.0.0.1 llen q:dlq || true

echo
echo "missing fields:"
sudo sqlite3 "$DB" "SELECT COUNT(*) FROM videos WHERE src IS NULL OR pipeline_status IS NULL OR ts IS NULL OR src='' OR pipeline_status='';"

echo "== DONE =="
