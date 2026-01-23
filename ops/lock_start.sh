#!/usr/bin/env bash
set -euo pipefail
systemctl start gemivas-queue-worker.service 2>/dev/null || true
systemctl enable --now gemivas-brain-policy.timer 2>/dev/null || true
