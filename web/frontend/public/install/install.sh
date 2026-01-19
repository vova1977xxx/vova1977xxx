#!/usr/bin/env bash
set -euo pipefail
apt-get update -y
apt-get install -y ca-certificates curl git nginx ufw jq ffmpeg python3 python3-pip
if ! command -v docker >/dev/null 2>&1; then apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; systemctl enable --now docker; fi
mkdir -p /srv/gemivas_platform/{data,logs,tmp,postgres} /srv/web/feed/videos /srv/web/feed/thumbs
if [ ! -f /srv/gemivas-platform/.env ]; then echo DOMAIN=gemivas.com > /srv/gemivas-platform/.env; echo POSTGRES_PASSWORD=9f1b653e8012afe76d4aaddf5705a572 >> /srv/gemivas-platform/.env; fi
