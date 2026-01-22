#!/usr/bin/env bash
set -euo pipefail

echo "== PATCH: THUMBNAIL + ANALYZE + RANK =="

# [1] task_types (add thumbnail, rank)
TT="/srv/ai_core/orchestrator/task_types.json"
if [ -f "$TT" ]; then
  if ! grep -q '"thumbnail"' "$TT"; then
    sudo sed -i 's/"probe", "analyze"/"probe", "thumbnail", "analyze"/' "$TT" || true
  fi
  if ! grep -q '"rank"' "$TT"; then
    sudo sed -i 's/"analyze", "publish"/"analyze", "rank", "publish"/' "$TT" || true
  fi
fi

# [2] worker_queue handlers (safe stub)
WQ="/srv/gemivas-platform/workers_queue/worker_queue.py"
if [ -f "$WQ" ]; then
  if ! grep -q 'if t == "thumbnail"' "$WQ"; then
    sudo sed -i '/if t == "publish_upload":/c\
    if t == "publish_upload":\
        return {"ok": True, "ignored": True, "reason": "legacy_publish_upload_disabled"}\
\
    if t == "thumbnail":\
        return {"ok": True, "stub": True}\
\
    if t == "analyze":\
        return {"ok": True, "stub": True}\
\
    if t == "rank":\
        return {"ok": True, "stub": True}\
' "$WQ"
  fi
fi

# [3] restart queue worker
sudo systemctl restart gemivas-queue-worker.service || true

echo "== PATCH DONE =="
