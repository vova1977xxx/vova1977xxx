#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"

echo "== GEMIVAS MASTER ==" 

echo "[1/9] stop lock services"
systemctl stop gemivas-queue-worker.service 2>/dev/null || true
systemctl stop gemivas-brain-policy.timer 2>/dev/null || true
systemctl stop gemivas-brain-policy.service 2>/dev/null || true

echo "[2/9] autopatch"
cd "$ROOT" && ./ops/autopatch.sh || true

echo "[3/9] migrate (safe)"
cd "$ROOT" && ./ops/canon_migrate.sh || true

echo "[4/9] start services"
systemctl start gemivas-queue-worker.service 2>/dev/null || true
systemctl enable --now gemivas-brain-policy.timer 2>/dev/null || true

echo "[5/9] doctor"
cd "$ROOT" && ./ops/doctor.sh || true

echo "[6/9] refill analyze/rank"
cd "$ROOT" && ./ops/queue_refill_analyze_rank.sh 2000 2>/dev/null || true

echo "[7/9] queue drain check"
sleep 10
echo "q:tasks=$(redis-cli -h 127.0.0.1 LLEN q:tasks 2>/dev/null || echo -)"
echo "q:dlq=$(redis-cli -h 127.0.0.1 LLEN q:dlq 2>/dev/null || echo -)"

echo "[8/9] status"
cd "$ROOT" && ./ops/status.sh || true

echo "[9/9] DONE"
