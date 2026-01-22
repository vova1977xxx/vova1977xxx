#!/usr/bin/env python3
import sys
import json
import sqlite3
import time

DB = "/srv/gemivas_platform/data/gemivas.db"

def main():
    if len(sys.argv) < 4:
        print("usage: log_event.py KIND REF_ID MSG [DATA_JSON]", file=sys.stderr)
        return 2

    kind = sys.argv[1].strip()
    ref_id = sys.argv[2].strip()
    msg = sys.argv[3].strip()
    data = None

    if len(sys.argv) >= 5:
        try:
            data = json.loads(sys.argv[4])
        except Exception:
            data = {"raw": sys.argv[4]}

    ts = int(time.time())

    con = sqlite3.connect(DB)
    cur = con.cursor()

    # existing canonical table (legacy-compatible)
    cur.execute(
        "INSERT INTO events(ts, kind, ref_id, msg, data_json) VALUES (?,?,?,?,?)",
        (ts, kind, ref_id, msg, json.dumps(data, ensure_ascii=False) if data is not None else None),
    )

    con.commit()
    con.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
