import time
import sqlite3

def _con(db_fn):
    if callable(db_fn):
        return db_fn()
    return sqlite3.connect(db_fn)

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

