from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app=FastAPI()

def read(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            d=json.load(f)
        return d.get("feed",[])
    except:
        return []

@app.get("/api/feed")
def feed():
    return JSONResponse(content={"feed": read("/srv/web/feed/feed.json")})

@app.get("/api/feed/shorts")
def feed_shorts():
    return JSONResponse(content={"feed": read("/srv/memory/feed/shorts.json")})

@app.get("/api/feed/long")
def feed_long():
    return JSONResponse(content={"feed": read("/srv/memory/feed/long.json")})
