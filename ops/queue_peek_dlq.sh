#!/usr/bin/env bash
set -euo pipefail
redis-cli LRANGE q:dlq 0 20 | nl -ba
