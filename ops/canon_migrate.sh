#!/usr/bin/env bash
set -euo pipefail

DB="/srv/gemivas_platform/data/gemivas.db"
echo "== GEMIVAS CANON MIGRATE =="

echo "[1/5] backup"
sudo cp -a "$DB" "${DB}.bak.$(date +%s)" || true

echo "[2/5] create tables"
sudo sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY,kind TEXT NOT NULL,url TEXT NOT NULL,title TEXT,enabled INTEGER NOT NULL DEFAULT 1,fail_count INTEGER NOT NULL DEFAULT 0,last_ok INTEGER,last_fail INTEGER,created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')));"
sudo sqlite3 "$DB" "CREATE UNIQUE INDEX IF NOT EXISTS idx_sources_kind_url ON sources(kind,url);"
sudo sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT,ts INTEGER NOT NULL DEFAULT (strftime('%s','now')),kind TEXT NOT NULL,ref_id TEXT,msg TEXT,data_json TEXT);"
sudo sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);"
sudo sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_events_kind_ts ON events(kind,ts);"

echo "[3/5] videos columns (best-effort)"
for col in "src TEXT" "ts INTEGER" "title TEXT" "tags_json TEXT" "local_file_path TEXT" "duration_sec INTEGER" "width INTEGER" "height INTEGER" "aspect_ratio REAL" "has_audio INTEGER" "language TEXT" "safety_score REAL" "nsfw_flag INTEGER" "interest_score REAL" "viral_score REAL" "popularity_score REAL" "last_seen INTEGER" "last_checked INTEGER" "pipeline_status TEXT" "source_id TEXT"
do
  name=$(echo "$col" | awk "{print \$1}")
  sudo sqlite3 "$DB" "ALTER TABLE videos ADD COLUMN $col;" 2>/dev/null || true
done

echo "[4/5] indexes"
sudo sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_videos_ts ON videos(ts);"
sudo sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_videos_src_ts ON videos(src,ts);"
sudo sqlite3 "$DB" "CREATE INDEX IF NOT EXISTS idx_videos_pipeline_status ON videos(pipeline_status);"

echo "[5/5] backfill"
sudo sqlite3 "$DB" "UPDATE videos SET src='legacy' WHERE src IS NULL OR src='';"
sudo sqlite3 "$DB" "UPDATE videos SET pipeline_status='published' WHERE pipeline_status IS NULL OR pipeline_status='';"
sudo sqlite3 "$DB" "UPDATE videos SET ts=CAST(strftime('%s', added_at) AS INTEGER) WHERE (ts IS NULL OR ts=0) AND added_at IS NOT NULL;"

bash ./ops/patch_videos_defaults.sh || true

echo "missing_fields:"
sudo sqlite3 "$DB" "SELECT COUNT(*) FROM videos WHERE src IS NULL OR pipeline_status IS NULL OR ts IS NULL OR src='' OR pipeline_status='';"

echo "== DONE =="
