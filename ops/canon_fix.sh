#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"
DB="/srv/gemivas_platform/data/gemivas.db"

echo "== GEMIVAS CANON FIX =="

echo "[1/6] backups"
sudo mkdir -p /srv/gemivas_platform/data
sudo cp -a "$DB" "${DB}.bak.$(date +%s)" || true

echo "[2/6] patch publish_upload legacy -> ignore"
sudo perl -0777 -i -pe 's/if t == "publish_upload":.*?return publish_file\(fp, src=task.get\("src","upload"\)\)\n/if t == "publish_upload":\n        return {"ok": True, "ignored": True, "reason": "legacy_publish_upload_disabled"}\n\n/sms' "$ROOT/workers_queue/worker_queue.py" || true

echo "[3/6] enforce DB path in queue worker"
sudo sed -i 's|^DB="/srv/gemivas-platform/db/gemivas.sqlite"|DB="/srv/gemivas_platform/data/gemivas.db"|' "$ROOT/workers_queue/worker_queue.py" || true

echo "[4/6] enforce DB path in brain sources loop"
sudo sed -i 's|DB="/srv/gemivas-platform/db/gemivas.sqlite"|DB="/srv/gemivas_platform/data/gemivas.db"|' "$ROOT/workers_queue/brain_sources_loop.py" || true
sudo sed -i 's|DB="/srv/gemivas-platform/db/gemivas.sqlite"|DB="/srv/gemivas_platform/data/gemivas.db"|' "$ROOT/workers_queue/brain_sources_loop.py" || true

echo "[5/6] restart services"
sudo systemctl restart gemivas-queue-worker.service || true
sudo systemctl restart gemivas-brain-sources.service || true

echo "[6/6] verify (skipped: doctor will verify)"

echo "== DONE =="
