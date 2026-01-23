#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"

echo "== GEMIVAS MASTER FAST ==" 

echo "[1/6] stop lock services"
systemctl stop gemivas-queue-worker.service 2>/dev/null || true
systemctl stop gemivas-brain-policy.timer 2>/dev/null || true
systemctl stop gemivas-brain-policy.service 2>/dev/null || true

echo "[2/6] autopatch (includes migrate+verify)"
cd "$ROOT" && ./ops/autopatch.sh || true

echo "[3/6] start services"
systemctl start gemivas-queue-worker.service 2>/dev/null || true
systemctl enable --now gemivas-brain-policy.timer 2>/dev/null || true

echo "[4/6] doctor (self-repair + refill)"
cd "$ROOT" && ./ops/doctor.sh || true

echo "[5/6] queue drain check"
sleep 10
echo "q:tasks=$(redis-cli -h 127.0.0.1 LLEN q:tasks 2>/dev/null || echo -)"
echo "q:dlq=$(redis-cli -h 127.0.0.1 LLEN q:dlq 2>/dev/null || echo -)"

echo "[6/6] DONE"
