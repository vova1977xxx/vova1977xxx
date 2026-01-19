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

# 4) systemd timers
mkdir -p /etc/systemd/system
cp -f /srv/gemivas-platform/systemd/gemivas-*.service /etc/systemd/system/ 2>/dev/null || true
cp -f /srv/gemivas-platform/systemd/gemivas-*.timer /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload
systemctl enable --now gemivas-news-worker.timer gemivas-radio-worker.timer gemivas-video-download-worker.timer gemivas-video-probe-worker.timer gemivas-video-publish-worker.timer gemivas-video-cleanup-worker.timer 2>/dev/null || true

# 5) restart orchestrator (if exists)
systemctl restart gemivas-orchestrator.service 2>/dev/null || true

# 6) nginx reload
nginx -t && systemctl reload nginx

echo "[GEMIVAS] install.sh DONE"
echo "URLs:"
echo " - https://gemivas.com/feed/"
echo " - https://gemivas.com/radio/"
echo " - https://gemivas.com/news/"
