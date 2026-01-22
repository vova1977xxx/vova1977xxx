#!/usr/bin/env bash
set -euo pipefail

echo "== DEPLOY NGINX ==" 

cp -f nginx/gemivas.conf /etc/nginx/sites-available/gemivas
nginx -t
systemctl reload nginx

echo "== DONE ==" 
