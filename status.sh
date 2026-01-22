#!/usr/bin/env bash
set -e
cd /srv/gemivas-platform

echo "GEMIVAS PLATFORM PACK"
echo "Version: $(cat VERSION 2>/dev/null || echo n/a)"
echo

echo "== SYSTEMD =="
systemctl --no-pager --full status nginx 2>/dev/null | head -n 12 || true
echo

echo "== DOCKER =="
docker ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}" || true
echo

echo "== DISK =="
df -h / | tail -n 1
echo

echo "== MEMORY =="
echo "uploads mp4:" $(ls -1 /srv/uploads/feed/*.mp4 2>/dev/null | wc -l) || true
echo "published mp4:" $(find /srv/web/feed/videos -type f -name "*.mp4" 2>/dev/null | wc -l) || true
echo
python3 - <<'PY2'
import json,os
def load(p, key):
  try:
    j=json.load(open(p,"r",encoding="utf-8"))
    return len(j.get(key,[]))
  except Exception:
    return -1
print("radio stations:", load("/srv/memory/radio/stations.json","stations"))
print("news items:", load("/srv/memory/news/items.json","items"))
PY2
echo

echo "== API QUICKCHECK =="
curl -fsS https://gemivas.com/api/feed >/dev/null && echo "feed: OK" || echo "feed: FAIL"
curl -fsS https://gemivas.com/api/radio >/dev/null && echo "radio: OK" || echo "radio: FAIL"
curl -fsS https://gemivas.com/api/news >/dev/null && echo "news: OK" || echo "news: FAIL"

echo "queue tasks: $(redis-cli -h 127.0.0.1 llen q:tasks 2>/dev/null || echo -)"
echo "queue dlq:   $(redis-cli -h 127.0.0.1 llen q:dlq 2>/dev/null || echo -)"

echo
echo "== BRAIN POLICY =="
systemctl --no-pager --full status gemivas-brain-policy.timer 2>/dev/null | head -n 8 || true

echo
echo "== EVENTS (last 12) =="
sqlite3 /srv/gemivas_platform/data/gemivas.db "select id,ts,kind,ref_id,msg from events order by id desc limit 12;" 2>/dev/null || true
