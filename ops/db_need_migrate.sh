#!/usr/bin/env bash
set -euo pipefail
DB="/srv/gemivas_platform/data/gemivas.db"
NEED=0
sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='videos';" | grep -q videos || NEED=1
sqlite3 "$DB" "PRAGMA table_info(videos);" | grep -q interest_score || NEED=1
sqlite3 "$DB" "PRAGMA table_info(videos);" | grep -q pipeline_status || NEED=1
exit $NEED
