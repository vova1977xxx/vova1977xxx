#!/usr/bin/env bash
set -euo pipefail

DB="/srv/gemivas_platform/data/gemivas.db"

for i in 1 2 3; do
  sqlite3 "$DB" "SELECT 1;" >/dev/null 2>&1 && break
  echo "DB locked, retry $i/3..."
  sleep 2
done

if sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='trigger' AND name='trg_videos_defaults';" | grep -q trg_videos_defaults; then
  echo "OK: trg_videos_defaults already installed"
  exit 0
fi

sqlite3 "$DB" <<'SQL'
CREATE TRIGGER trg_videos_defaults
AFTER INSERT ON videos
FOR EACH ROW
BEGIN
  UPDATE videos
  SET
    interest_score = COALESCE(interest_score, 0.0),
    viral_score = COALESCE(viral_score, 0.0),
    popularity_score = COALESCE(popularity_score, 0.0),
    pipeline_status = COALESCE(pipeline_status, 'new')
  WHERE id = NEW.id;
END;
SQL

echo "OK: trg_videos_defaults installed"
