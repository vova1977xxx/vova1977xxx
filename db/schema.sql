PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  src TEXT NOT NULL,
  ts INTEGER NOT NULL,
  tags TEXT DEFAULT '',
  local_file_path TEXT DEFAULT NULL,
  duration_sec REAL DEFAULT NULL,
  width INTEGER DEFAULT NULL,
  height INTEGER DEFAULT NULL,
  has_audio INTEGER DEFAULT NULL,
  language TEXT DEFAULT NULL,
  safety_score REAL DEFAULT NULL,
  nsfw_flag INTEGER DEFAULT 0,
  interest_score REAL DEFAULT NULL,
  viral_score REAL DEFAULT NULL,
  popularity_score REAL DEFAULT 0,
  pipeline_status TEXT DEFAULT 'new',
  last_seen INTEGER DEFAULT NULL,
  last_checked INTEGER DEFAULT NULL,
  created_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_videos_ts ON videos(ts);
CREATE INDEX IF NOT EXISTS idx_videos_pop ON videos(popularity_score);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(pipeline_status);

CREATE TABLE IF NOT EXISTS video_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  value REAL DEFAULT NULL,
  meta TEXT DEFAULT NULL,
  ts INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_events_video_ts ON video_events(video_id, ts);

CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  url TEXT NOT NULL,
  title TEXT DEFAULT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  fail_count INTEGER NOT NULL DEFAULT 0,
  last_ok INTEGER DEFAULT NULL,
  last_fail INTEGER DEFAULT NULL,
  created_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled);

CREATE TABLE IF NOT EXISTS news_items (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  published_ts INTEGER DEFAULT NULL,
  created_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_items(published_ts);

CREATE TABLE IF NOT EXISTS radio_stations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  stream_url TEXT NOT NULL,
  country TEXT DEFAULT NULL,
  city TEXT DEFAULT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  fail_count INTEGER NOT NULL DEFAULT 0,
  last_ok INTEGER DEFAULT NULL,
  last_fail INTEGER DEFAULT NULL,
  created_at INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_radio_enabled ON radio_stations(enabled);
