#!/bin/bash
python3 -m py_compile /srv/gemivas-platform/master_final/update.py
if [ $? -ne 0 ]; then
  echo "Error: update.py failed to compile" >> /var/log/gemivas/error.log
  exit 1
fi
