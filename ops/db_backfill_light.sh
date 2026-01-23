#!/usr/bin/env bash
set -euo pipefail
DB="/srv/gemivas_platform/data/gemivas.db"
sqlite3 "$DB" "UPDATE videos SET src='legacy' WHERE src IS NULL OR src='';"
sqlite3 "$DB" "UPDATE videos SET pipeline_status='published' WHERE pipeline_status IS NULL OR pipeline_status='';"
sqlite3 "$DB" "UPDATE videos SET ts=CAST(strftime('%s', added_at) AS INTEGER) WHERE (ts IS NULL OR ts=0) AND added_at IS NOT NULL;"
