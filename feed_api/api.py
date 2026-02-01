from fastapi import FastAPI
import json, os

app = FastAPI()
FEED_FILE = "/srv/memory/feed/index.json"

@app.get("/api/feed")
def get_feed():
    if os.path.exists(FEED_FILE):
        with open(FEED_FILE) as f:
            return json.load(f)
    return {"feed":[]}
