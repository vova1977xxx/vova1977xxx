import time
import sqlite3
import json, subprocess, os

def _con(db_fn):
    if callable(db_fn):
        return db_fn()
    return sqlite3.connect(db_fn)
def _ffprobe(path: str):
    cmd=["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height","-of","json",path]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: return None
    try: data=json.loads(r.stdout or "{}")
    except Exception: return None
    dur=None
    try: dur=float(((data.get("format") or {}).get("duration")) or 0) or None
    except Exception: dur=None
    w=h=None; has_audio=0
    for s in (data.get("streams") or []):
        ct=(s.get("codec_type") or "").lower()
        if ct=="video" and not w and not h:
            w=int(s.get("width") or 0) or None
            h=int(s.get("height") or 0) or None
        if ct=="audio": has_audio=1
    return {"duration_sec":dur,"width":w,"height":h,"has_audio":has_audio}

def analyze(db_fn, video_id: str):
    if not video_id:
        return {"ok": False, "error": "missing id"}

    now = int(time.time())

    duration_sec = None
    width = None
    height = None
    has_audio = None
    aspect_ratio = None

    interest_score = 0.50
    safety_score = 1.00
    nsfw_flag = 0

    try:
        con = _con(db_fn)
        # load local path + ffprobe
        row = con.execute("SELECT local_file_path FROM videos WHERE id=?", (video_id,)).fetchone()
        local_path = (row[0] if row else None)
        if local_path and os.path.exists(local_path):
            meta = _ffprobe(local_path) or {}
            duration_sec = meta.get("duration_sec")
            width = meta.get("width")
            height = meta.get("height")
            has_audio = meta.get("has_audio")
            if width and height:
                aspect_ratio = round(float(width) / float(height), 4)
        con.execute("""
            UPDATE videos
            SET last_checked=?,
                duration_sec=COALESCE(duration_sec, ?),
                width=COALESCE(width, ?),
                height=COALESCE(height, ?),
                aspect_ratio=COALESCE(aspect_ratio, ?),
                has_audio=COALESCE(has_audio, ?),
                safety_score=COALESCE(safety_score, ?),
                nsfw_flag=COALESCE(nsfw_flag, ?),
                interest_score=COALESCE(interest_score, ?),
                pipeline_status=CASE
                    WHEN pipeline_status IS NULL OR pipeline_status=" " OR pipeline_status="" OR pipeline_status="published" THEN "analyzed"
                    ELSE pipeline_status
                END
            WHERE id=?
        """, (now, duration_sec, width, height, aspect_ratio, has_audio, safety_score, nsfw_flag, interest_score, video_id))

        con.commit()
        con.close()
        return {"ok": True, "id": video_id, "interest_score": interest_score}
    except Exception as e:
        try:
            con.close()
        except Exception:
            pass
        return {"ok": False, "error": "analyze_db_fail", "detail": str(e), "id": video_id}

def rank(db_fn, video_id: str):
    if not video_id:
        return {"ok": False, "error": "missing id"}

    now = int(time.time())

    try:
        con = _con(db_fn)

        row = con.execute("SELECT interest_score, safety_score, nsfw_flag FROM videos WHERE id=?", (video_id,)).fetchone()
        if not row:
            con.close()
            return {"ok": False, "error": "not_found", "id": video_id}

        interest_score, safety_score, nsfw_flag = row
        interest_score = float(interest_score or 0.5)
        safety_score = float(safety_score or 1.0)
        nsfw_flag = int(nsfw_flag or 0)

        viral_score = interest_score
        if nsfw_flag:
            viral_score *= 0.2
        viral_score *= max(0.0, min(1.0, safety_score))

        popularity_score = max(0.0, min(1.0, viral_score))

        con.execute("""
            UPDATE videos
            SET viral_score=?,
                popularity_score=?,
                last_seen=?,
                pipeline_status="ranked"
            WHERE id=?
        """, (viral_score, popularity_score, now, video_id))

        con.commit()
        con.close()
        return {"ok": True, "id": video_id, "viral_score": viral_score, "popularity_score": popularity_score}
    except Exception as e:
        try:
            con.close()
        except Exception:
            pass
        return {"ok": False, "error": "rank_db_fail", "detail": str(e), "id": video_id}

