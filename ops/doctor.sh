#!/usr/bin/env bash
set -euo pipefail

ROOT="/srv/gemivas-platform"

echo "== GEMIVAS DOCTOR =="
python3 $ROOT/scripts/log_event.py doctor start "doctor started" "{}" || true

echo "[1/4] canon_fix"
sudo $ROOT/ops/canon_fix.sh || true

echo "[2/4] canon_migrate"
sudo $ROOT/ops/canon_migrate.sh

echo "[3/4] canon_verify"
sudo $ROOT/ops/canon_verify.sh

echo "[4/4] force_refill"
sudo $ROOT/ops/force_refill.sh || true

echo "== DOCTOR DONE =="

echo
echo "== POST-DOCTOR STATUS =="

echo "published mp4:" $(find /srv/web/feed/videos -type f -name "*.mp4" 2>/dev/null | wc -l) || true

curl -fsS https://gemivas.com/api/feed >/dev/null && echo "feed: OK" || echo "feed: FAIL"
curl -fsS https://gemivas.com/api/radio >/dev/null && echo "radio: OK" || echo "radio: FAIL"
curl -fsS https://gemivas.com/api/news >/dev/null && echo "news: OK" || echo "news: FAIL"

echo "queue tasks: $(redis-cli -h 127.0.0.1 llen q:tasks 2>/dev/null || echo -)"
echo "queue dlq:   $(redis-cli -h 127.0.0.1 llen q:dlq 2>/dev/null || echo -)"

systemctl --no-pager --full status gemivas-brain-policy.timer 2>/dev/null | head -n 6 || true

echo
echo "== QUEUE DRAIN CHECK =="
sleep 12
echo "queue tasks (after 12s): $(redis-cli -h 127.0.0.1 llen q:tasks 2>/dev/null || echo -)"
echo "queue dlq   (after 12s): $(redis-cli -h 127.0.0.1 llen q:dlq 2>/dev/null || echo -)"

python3 $ROOT/scripts/log_event.py doctor done "doctor finished" "{\"published\":$(find /srv/web/feed/videos -type f -name \"*.mp4\" 2>/dev/null | wc -l),\"q_tasks\":$(redis-cli -h 127.0.0.1 llen q:tasks 2>/dev/null || echo -),\"q_dlq\":$(redis-cli -h 127.0.0.1 llen q:dlq 2>/dev/null || echo -)}" || true
