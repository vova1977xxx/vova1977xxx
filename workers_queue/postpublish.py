import json

def enqueue_postpublish(R, Q_TASKS: str, video_id: str):
    try:
        for t in ("thumbnail","analyze","rank"):
            R.lpush(Q_TASKS, json.dumps({"id": f"{t}-{video_id}", "type": t, "payload": {"id": video_id}}))
    except Exception:
        pass
