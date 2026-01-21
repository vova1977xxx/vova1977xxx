import json, time, traceback, os, shutil, pathlib, sqlite3
import redis

R = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

Q_TASKS = "q:tasks"
Q_DLQ   = "q:dlq"

DB="/srv/gemivas-platform/db/gemivas.sqlite"
UPLOAD_DIR="/srv/uploads/feed"
WEB_ROOT="/srv/web/feed/videos"

MAX_TRY = 3

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def requeue(task: dict):
    task["try"] = int(task.get("try", 0)) + 1
    if task["try"] >= MAX_TRY:
        R.lpush(Q_DLQ, json.dumps(task))
        return False
    time.sleep(5 * task["try"])
    R.lpush(Q_TASKS, json.dumps(task))
    return True

def publish_file(src_path: str, src="upload"):
    p = pathlib.Path(src_path)
    vid = p.stem
    y = time.strftime("%Y")
    m = time.strftime("%m")
    out_dir = f"{WEB_ROOT}/{y}/{m}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{vid}.mp4"

    if not os.path.exists(out_path):
        shutil.copy2(src_path, out_path)

    rel = f"/feed/videos/{y}/{m}/{vid}.mp4"

    con=db()
    try:
        con.execute(
            "INSERT OR IGNORE INTO videos(id,title,url,src,ts,tags,pipeline_status) VALUES (?,?,?,?,?,?,?)",
            (vid, vid, rel, src, int(time.time()), "", "published")
        )
        con.commit()
    finally:
        con.close()

    return {"ok": True, "id": vid, "url": rel}

def handle(task: dict):
    t = task.get("type")
    p = task.get("payload") or {}

    if t == "ping":
        return {"ok": True}

    if t == "download":
        url = p.get("url","")
        if not url:
            return {"ok": False, "error": "missing url"}
        return download_url(url, p.get("source_id"))


    if t == "publish_upload":
        fp = p.get("path","")
        if not fp:
            return {"ok": False, "error": "missing path"}
        if not fp.startswith(UPLOAD_DIR + "/"):
            return {"ok": False, "error": "bad path"}
        if not os.path.exists(fp):
            return {"ok": False, "error": "not found"}
        return publish_file(fp, src=task.get("src","upload"))

    return {"ok": False, "error": "unknown_task_type", "type": t}

def main():
    while True:
        x = R.brpop(Q_TASKS, timeout=5)
        if not x:
            continue
        _, raw = x
        try:
            task = json.loads(raw)
            res = handle(task)
            if not (res or {}).get("ok", True):
                requeue(task)
                continue
            R.setex(f"task:res:{task.get('id')}", 3600, json.dumps(res))
        except Exception:
            try:
                requeue(task)
            except Exception:
                R.lpush(Q_DLQ, raw)


# --- download task ---
def download_url(url: str, source_id=None):
    vid = str(int(time.time()*1000))
    tmp = f"/srv/downloads/{vid}.mp4"
    out = f"{UPLOAD_DIR}/{vid}.mp4"

    os.system(f"curl -L --connect-timeout 20 --max-time 600 -A 'GEMIVAS' -o '{tmp}' '{url}'")

    if not os.path.exists(tmp) or os.path.getsize(tmp) < 50000:
        try:
            os.remove(tmp)
        except Exception:
            pass
        source_fail(url, source_id)
        return {"ok": False, "error": "download_failed"}

    shutil.move(tmp, out)
    source_ok(source_id)

    # next step -> publish
    R.lpush(Q_TASKS, json.dumps({
        "id": f"{int(time.time()*1000)}",
        "type": "publish_upload",
        "src": "download",
        "prio": 100,
        "payload": {"path": out},
        "try": 0,
        "ts": int(time.time()),
    }))

    return {"ok": True, "id": vid, "path": out}

if __name__ == "__main__":
    main()


def source_fail(url:str, source_id=None):
    try:
        con=db()
        if source_id:
            con.execute("UPDATE sources SET fail_count=fail_count+1,last_fail=? WHERE id=? AND kind='video'",(int(time.time()),source_id))
            con.execute("UPDATE sources SET enabled=0 WHERE id=? AND kind='video' AND fail_count>=3",(source_id,))
        else:
            con.execute("UPDATE sources SET fail_count=fail_count+1,last_fail=? WHERE url=? AND kind='video'",(int(time.time()),url))
            con.execute("UPDATE sources SET enabled=0 WHERE url=? AND kind='video' AND fail_count>=3",(url,))
        con.commit()
        con.close()
    except Exception:
        pass


def source_ok(source_id:str):
    try:
        if not source_id:
            return
        con=db()
        con.execute("UPDATE sources SET fail_count=0,last_ok=? WHERE id=? AND kind='video'",(int(time.time()),source_id))
        con.commit()
        con.close()
    except Exception:
        pass
