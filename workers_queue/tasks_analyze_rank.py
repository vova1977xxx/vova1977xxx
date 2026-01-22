def analyze(db_fn, video_id: str):
    if not video_id:
        return {"ok": False, "error": "missing id"}
    # TODO: real analyze
    return {"ok": True, "stub": True, "id": video_id}

def rank(db_fn, video_id: str):
    if not video_id:
        return {"ok": False, "error": "missing id"}
    # TODO: real rank
    return {"ok": True, "stub": True, "id": video_id}
