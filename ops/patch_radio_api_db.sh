#!/usr/bin/env bash
set -euo pipefail

echo "== PATCH RADIO API -> DB =="

ROOT="/srv/gemivas-platform"
DB="/srv/gemivas_platform/data/gemivas.db"

# detect backend file
API_FILE=""
for f in \
  "$ROOT/gemivas_brain_api.py" \
  "$ROOT/brain_api.py" \
  "$ROOT/app.py" \
  "$ROOT/main.py" \
  "$ROOT/server.py" \
  "$ROOT/brain/server.py" \
  "$ROOT/brain/api.py" \
  "$ROOT/gemivas/brain_api.py"
do
  if [ -f "$f" ]; then API_FILE="$f"; break; fi
done

if [ -z "${API_FILE}" ]; then
  echo "ERROR: cannot find backend API python file"
  exit 1
fi

echo "[patch] backend file: $API_FILE"
cp -f "$API_FILE" "$API_FILE.bak.$(date +%s)"

# ensure sqlite3 import exists
python3 - <<PY
import re,sys
p="${API_FILE}"
s=open(p,"r",encoding="utf-8").read()
if "import sqlite3" not in s:
  s=re.sub(r'^(import [^\n]+)\n', r'\\1,sqlite3\\n', s, count=1, flags=re.M)
open(p,"w",encoding="utf-8").write(s)
print("OK import sqlite3")
PY

# inject DB radio loader helper (idempotent)
python3 - <<PY
import re,sys
p="${API_FILE}"
s=open(p,"r",encoding="utf-8").read()

if "def _radio_from_db(" in s:
  print("OK helper already exists")
  sys.exit(0)

helper = r'''
def _radio_from_db(db_path="/srv/gemivas_platform/data/gemivas.db"):
  import sqlite3,time,json
  conn=sqlite3.connect(db_path)
  conn.row_factory=sqlite3.Row
  rows=conn.execute("SELECT id,name,country,city,language,tags,stream_url,is_enabled,last_checked_ts FROM radio_stations WHERE is_enabled=1 ORDER BY id").fetchall()
  now=int(time.time())
  stations=[]
  for r in rows:
    tags=(r["tags"] or "").split(",") if r["tags"] else []
    stations.append({
      "id": f"db{r['id']}",
      "name": r["name"],
      "country": r["country"] or "UA",
      "stream_url": r["stream_url"],
      "tags": [t for t in tags if t],
      "alive": True,
      "checked_ts": int(r["last_checked_ts"] or now),
    })
  conn.close()
  return {"ok": True, "stations": stations}
'''
# place helper near top (after imports)
s=re.sub(r'(\n)(\s*def\s+)', r'\n'+helper+r'\n\2', s, count=1)
open(p,"w",encoding="utf-8").write(s)
print("OK helper injected")
PY

# patch /api/radio handler to use DB (best-effort patterns)
python3 - <<PY
import re,sys
p="${API_FILE}"
s=open(p,"r",encoding="utf-8").read()
changed=False

patterns=[
  r'(@app\.get\(\"/api/radio\"\)[\s\S]*?return [^\n]+\n)',
  r'(@app\.route\(\"/api/radio\"[\s\S]*?return [^\n]+\n)',
]
for pat in patterns:
  m=re.search(pat,s)
  if not m: continue
  block=m.group(1)
  if "_radio_from_db" in block:
    print("OK handler already patched")
    sys.exit(0)
  # replace any return line inside that handler with db call return
  block2=re.sub(r'return[^\n]+\n', '  return _radio_from_db()\n', block, count=1)
  s=s.replace(block,block2)
  changed=True
  break

if not changed:
  print("WARN: handler pattern not found (manual follow-up needed)")
else:
  open(p,"w",encoding="utf-8").write(s)
  print("OK handler patched")
PY

# restart brain api
echo "[patch] restart brain"
systemctl restart gemivas-brain.service 2>/dev/null || true
docker restart gemivas-brain 2>/dev/null || true

echo "[patch] quick test"
curl -s https://gemivas.com/api/radio | head -n 50

echo "== DONE =="
