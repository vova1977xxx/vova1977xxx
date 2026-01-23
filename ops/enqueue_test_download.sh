#!/usr/bin/env bash
set -euo pipefail
ID="dl_test_$(date +%s)"
URL="https://samplelib.com/lib/preview/mp4/sample-5s.mp4"
redis-cli LPUSH q:tasks "{\"id\":\"$ID\",\"type\":\"download\",\"payload\":{\"url\":\"$URL\",\"source_id\":\"samplelib\"},\"try\":0,\"ts\":$(date +%s)}" >/dev/null
echo "enqueued: $ID"
