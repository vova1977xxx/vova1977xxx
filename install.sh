#!/usr/bin/env bash
set -e

echo "[GEMIVAS] install.sh starting..."

# 1) dirs
mkdir -p /srv/gemivas-platform/workers
mkdir -p /srv/memory/{radio,news}
mkdir -p /srv/logs

# 2) initial data
if [ ! -s /srv/memory/radio/stations.json ]; then
  printf '{"stations":[{"id":"ur1","name":"Українське Радіо","country":"UA","stream_url":"https://radio.ukr.radio/ur1-mp3","tags":["ua","talk"]},{"id":"ur2","name":"Радіо Промінь","country":"UA","stream_url":"https://radio.ukr.radio/ur2-mp3","tags":["ua","music"]},{"id":"ur3","name":"Радіо Культура","country":"UA","stream_url":"https://radio.ukr.radio/ur3-mp3","tags":["ua","culture"]}]}\n' > /srv/memory/radio/stations.json
fi
if [ ! -s /srv/memory/news/items.json ]; then
  printf '{"items":[]}\n' > /srv/memory/news/items.json
fi

# 3) workers (files already in repo usually)
chmod +x /srv/gemivas-platform/status.sh || true

# 4) cron
( crontab -l 2>/dev/null; echo "*/10 * * * * python3 /srv/gemivas-platform/workers/news_fetch_worker.py >> /srv/logs/news_worker.log 2>&1" ) | crontab -
( crontab -l 2>/dev/null; echo "*/10 * * * * python3 /srv/gemivas-platform/workers/radio_health_worker.py >> /srv/logs/radio_worker.log 2>&1" ) | crontab -

# 5) restart orchestrator (if exists)
systemctl restart gemivas-orchestrator.service 2>/dev/null || true

# 6) nginx reload
nginx -t && systemctl reload nginx

echo "[GEMIVAS] install.sh DONE"
echo "URLs:"
echo " - https://gemivas.com/feed/"
echo " - https://gemivas.com/radio/"
echo " - https://gemivas.com/news/"
