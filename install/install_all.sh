#!/bin/bash
set -e
BASE=/srv/gemivas-platform
python3 -m venv $BASE/venv
python3 -m venv $BASE/venv
$BASE/venv/bin/pip install httpx
bash $BASE/ops/generate_units.sh
cp $BASE/services/generated/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable probe analyze rank feedbuilder selfheal
systemctl restart probe analyze rank feedbuilder selfheal
touch /srv/memory/LOCK_PUBLISH
bash $BASE/ops/generate_units.sh
cp $BASE/services/generated/*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable probe analyze rank feedbuilder
systemctl restart probe analyze rank feedbuilder
systemctl start selfheal.timer
mkdir -p /srv/memory
touch /srv/memory/LOCK_PUBLISH
echo INSTALL STARTED
BASE=/srv/gemivas-platform
$BASE/venv/bin/pip install --upgrade pip >/dev/null 2>&1
$BASE/venv/bin/pip install httpx >/dev/null 2>&1
echo FSM SERVICES READY
systemctl status probe --no-pager || true
systemctl status analyze --no-pager || true
systemctl status rank --no-pager || true
systemctl status feedbuilder --no-pager || true
echo INSTALL COMPLETE
systemctl enable selfheal.timer
systemctl start selfheal.timer
bash /srv/gemivas-platform/install/install_base.sh
echo BASE LAYER OK
bash $BASE/ops/generate_units.sh
systemctl daemon-reload
echo SYSTEMD LAYER OK
echo SPEC LAYER OK
bash /srv/gemivas-platform/install/install_ai_models.sh
echo AI LAYER OK
bash /srv/gemivas-platform/install/install_docker_stack.sh
echo DOCKER LAYER OK
echo DOCKER LAYER OK
bash /srv/gemivas-platform/ops/product/generate_product_units.sh
echo OPS LAYER OK
bash /srv/gemivas-platform/install/install_frontend.sh
echo UI LAYER OK
bash /srv/gemivas-platform/install/install_autoupdate.sh
echo AUTOUPDATE LAYER OK
