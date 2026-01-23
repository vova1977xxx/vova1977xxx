#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"

echo "== GEMIVAS MASTER FINAL ==" 

cd "$ROOT"

echo "[1/9] lock_stop"
bash ./ops/lock_stop.sh || true

echo "[2/9] git pull"
git fetch --all --prune || true
git pull || true

echo "[3/9] apply_patch (smart migrate included)"
bash ./ops/apply_patch.sh || true

echo "[4/9] doctor (self-repair + refill)"
bash ./ops/doctor.sh || true

echo "[5/9] lock_start"
bash ./ops/lock_start.sh || true

echo "[6/9] quick status"
bash ./ops/status.sh || true

echo "[7/9] queue drain check"
sleep 10
echo "q:tasks=$(redis-cli -h 127.0.0.1 LLEN q:tasks 2>/dev/null || echo -)"
echo "q:dlq=$(redis-cli -h 127.0.0.1 LLEN q:dlq 2>/dev/null || echo -)"

echo "[8-pre] light backfill"
bash ./ops/db_backfill_light.sh || true

echo "[8/9] final verify"
bash ./ops/canon_verify.sh || true

echo "[9/9] DONE"
