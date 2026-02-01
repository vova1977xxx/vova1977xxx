from fastapi import FastAPI
import httpx

app = FastAPI()

@app.post("/api/brain")
async def brain_loop():
    try:
        timeout = httpx.Timeout(180.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post("http://127.0.0.1:11434/api/generate", json={
                "model":"llama3:70b-instruct-q2_K",
                "prompt":"System check. Respond OK.",
                "stream":False
            })
        return {"ai": r.json()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/like")
def like_video(data: dict):
    return {"status":"ok"}
