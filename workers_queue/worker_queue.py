from tasks_analyze_rank import analyze as _analyze, rank as _rank
from tasks_thumbnail import make_thumbnail as _thumb
import json, time, traceback, os, shutil, pathlib, sqlite3, subprocess
import redis

R = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)

Q_TASKS = "q:tasks"
Q_DLQ   = "q:dlq"

DB="/srv/gemivas_platform/data/gemivas.db"
UPLOAD_DIR="/srv/uploads/feed"
WEB_ROOT="/srv/web/feed/videos"

MAX_TRY = 3

def db():
    con=sqlite3.connect(DB, timeout=30)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA busy_timeout=30000")
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
            "INSERT INTO videos(id,title,url,src,ts,tags_json,pipeline_status,local_file_path,source_id,popularity_score) VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET url=excluded.url, src=excluded.src, ts=excluded.ts, pipeline_status=excluded.pipeline_status, local_file_path=excluded.local_file_path, source_id=excluded.source_id",
            (vid, vid, rel, src, int(time.time()), "", "published", out_path, None, 0)
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


    if t == "thumbnail":
        return _thumb(db, p.get("id","") or p.get("video_id",""))

    if t == "analyze":
        return _analyze(db, p.get("id","") or p.get("video_id",""))

    if t == "rank":
        return _rank(db, p.get("id","") or p.get("video_id",""))


    if t == "publish_upload":
        return {"ok": True, "ignored": True, "reason": "legacy_publish_upload_disabled"}


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

    cmd=["curl","-f","-sS","-L","--connect-timeout","20","--max-time","600","-A","GEMIVAS","-o",tmp,url]; r=subprocess.run(cmd, capture_output=True, text=True); print("curl",r.returncode,url,flush=True); 0 if r.returncode==0 else print(r.stderr[:300],flush=True)

    if not os.path.exists(tmp) or os.path.getsize(tmp) < 50000:
        try:
            os.remove(tmp)
        except Exception:
            pass
        source_fail(url, source_id)
        return {"ok": False, "error": "download_failed"}

    shutil.move(tmp, out)

    # publish immediately (avoid uploads cleanup race)
    pub = publish_file(out, src="download")
    source_ok(source_id)
    return pub




def source_fail(url:str, source_id=None):
    for _ in range(3):
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
            return
        except Exception:
            try:
                con.close()
            except Exception:
                pass
            time.sleep(1)

def source_ok(source_id:str):
    if not source_id:
        return
    for _ in range(3):
        try:
            con=db()
            con.execute("UPDATE sources SET fail_count=0,last_ok=? WHERE id=? AND kind='video'",(int(time.time()),source_id))
            con.commit()
            con.close()
            return
        except Exception:
            try:
                con.close()
            except Exception:
                pass
            time.sleep(1)



if __name__ == "__main__":
    main()
