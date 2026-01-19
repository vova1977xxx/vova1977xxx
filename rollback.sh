#!/usr/bin/env bash
set -e
cd /srv/gemivas-platform
echo "[GEMIVAS] rollback"

git reset --hard HEAD~1

systemctl restart gemivas-orchestrator.service 2>/dev/null || true
nginx -t && systemctl reload nginx

echo "OK"
