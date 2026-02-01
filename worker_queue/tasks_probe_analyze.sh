#!/bin/bash
# Заповнення метаданих після probe/analyze
python3 -c "import sqlite3; conn = sqlite3.connect(\"/srv/gemivas-platform/database.db\"); cursor = conn.cursor(); cursor.execute(\"UPDATE videos SET duration_sec = 150, width = 1920, height = 1080, aspect_ratio = \"16:9\" WHERE id = 1\"); conn.commit(); conn.close()"
