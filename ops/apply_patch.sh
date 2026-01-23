#!/usr/bin/env bash
set -euo pipefail

echo "== GEMIVAS APPLY PATCH ==" 
echo "[apply_patch] START"

echo "[apply_patch] migrate"
./ops/db_backfill_light.sh || true
./ops/db_need_migrate.sh && echo "-> migrate: SKIP (DB ready)" || bash ./ops/canon_migrate.sh

echo "[apply_patch] systemd units"
bash ./ops/install_systemd_units.sh

echo "[apply_patch] patch_thumbnail_analyze_rank"
./ops/patch_thumbnail_analyze_rank.sh

echo "[apply_patch] nginx"
bash ./ops/deploy_nginx.sh


echo "[apply_patch] restart services"
bash ./ops/restart_services.sh

echo "[apply_patch] verify"
bash ./ops/canon_verify.sh

echo "[apply_patch] status"
bash ./status.sh

echo "[apply_patch] DONE"
