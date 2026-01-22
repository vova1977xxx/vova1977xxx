#!/usr/bin/env bash
set -euo pipefail

echo "== INSTALL SYSTEMD UNITS ==" 

# install/refresh units from repo
cp -f systemd/*.service /etc/systemd/system/ 2>/dev/null || true
cp -f systemd/*.timer   /etc/systemd/system/ 2>/dev/null || true

systemctl daemon-reload

# enable timers/services (best-effort)
systemctl enable --now gemivas-brain-policy.timer 2>/dev/null || true
systemctl enable --now gemivas-queue-worker.service 2>/dev/null || true

echo "== DONE ==" 
