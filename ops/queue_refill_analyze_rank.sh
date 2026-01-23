#!/usr/bin/env bash
set -euo pipefail
LIM=${1:-200}
/srv/ai_core/orchestrator/venv/bin/python /srv/gemivas-platform/ops/queue_refill_analyze_rank.py "$LIM"
