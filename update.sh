#!/usr/bin/env bash
set -e
cd /srv/gemivas-platform
echo "[GEMIVAS] update"

cp -a /srv/gemivas-platform/web/frontend/public/* /srv/web/frontend/public/ 2>/dev/null || true

git add -A || true
git commit -m "update" >/dev/null 2>&1 || true

systemctl restart gemivas-orchestrator.service 2>/dev/null || true
nginx -t && systemctl reload nginx

echo "OK"
