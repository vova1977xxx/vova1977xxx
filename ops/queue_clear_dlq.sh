#!/usr/bin/env bash
set -euo pipefail
redis-cli DEL q:dlq
