import os, time, subprocess

def make_thumbnail(db_fn, video_id: str):
    if not video_id:
        return {"ok": False, "error": "missing id"}

    con = db_fn()
    try:
        row = con.execute("SELECT local_file_path FROM videos WHERE id=? LIMIT 1", (video_id,)).fetchone()
    finally:
        con.close()

    if not row or not row[0]:
        return {"ok": False, "error": "no local_file_path", "id": video_id}

    src = row[0]
    if not os.path.exists(src):
        return {"ok": False, "error": "file_missing", "path": src}

    now = time.gmtime()
    out_dir = f"/srv/web/feed/thumbs/{now.tm_year}/{now.tm_mon:02d}"
    os.makedirs(out_dir, exist_ok=True)

    out = f"{out_dir}/{video_id}.jpg"
    tmp = f"{out}.tmp.jpg"

    cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error","-ss","1","-i",src,"-frames:v","1","-q:v","4",tmp]
    r = subprocess.run(cmd, capture_output=True, text=True)

    if r.returncode != 0 or (not os.path.exists(tmp)) or os.path.getsize(tmp) < 2000:
        try: os.remove(tmp)
        except Exception: pass
        return {"ok": False, "error": "ffmpeg_failed", "stderr": (r.stderr or "")[:200]}

    os.replace(tmp, out)
    return {"ok": True, "thumb": out.replace("/srv/web", "")}
