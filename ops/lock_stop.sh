#!/usr/bin/env bash
set -euo pipefail
systemctl stop gemivas-queue-worker.service 2>/dev/null || true
systemctl stop gemivas-brain-policy.timer 2>/dev/null || true
systemctl stop gemivas-brain-policy.service 2>/dev/null || true
