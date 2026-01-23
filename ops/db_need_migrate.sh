#!/usr/bin/env bash
set -euo pipefail

DB="/srv/gemivas_platform/data/gemivas.db"
NEED=0

# schema checks
sqlite3 "$DB" "SELECT 1 FROM sqlite_master WHERE type='table' AND name='videos';" | grep -q 1 || NEED=1
sqlite3 "$DB" "PRAGMA table_info(videos);" | grep -q interest_score || NEED=1
sqlite3 "$DB" "PRAGMA table_info(videos);" | grep -q pipeline_status || NEED=1

# backfill checks (CRITICAL)
if [ "$NEED" = "0" ]; then
  NULLS="$(sqlite3 "$DB" "SELECT COUNT(*) FROM videos WHERE interest_score IS NULL OR pipeline_status IS NULL;" 2>/dev/null || echo 0)"
  [ "${NULLS:-0}" = "0" ] || NEED=1
fi

exit $NEED
