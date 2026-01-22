#!/usr/bin/env bash
set -euo pipefail

echo "== GEMIVAS AUTOPATCH =="

cd /srv/gemivas-platform

echo "[1/5] git fetch"
git fetch --all --prune || true

echo "[2/5] git pull (best-effort)"
git pull || true

echo "[3/5] apply_patch"
./ops/apply_patch.sh

echo "[4/5] status"
./status.sh

echo "[5/5] quick health (doctor if needed)"
if ! ./ops/canon_verify.sh >/dev/null 2>&1; then
  echo "[autopatch] verify failed -> doctor"
  ./ops/doctor.sh || true
fi

echo "== AUTOPATCH DONE =="
