#!/usr/bin/env bash
set -e
cd /srv/gemivas-platform
echo "[GEMIVAS] update"

git pull --rebase 2>/dev/null || true

# deploy web
cp -a /srv/gemivas-platform/web/frontend/public/* /srv/web/frontend/public/ 2>/dev/null || true

# runtime dirs
mkdir -p /srv/downloads
chmod 777 /srv/downloads || true

# install systemd units (canon)
cp -a /srv/gemivas-platform/systemd/*.service /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload || true
systemctl restart gemivas-queue-worker.service gemivas-brain-sources.service 2>/dev/null || true
systemctl restart gemivas-orchestrator.service 2>/dev/null || true

nginx -t && systemctl reload nginx

echo "OK"
