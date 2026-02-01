import time, json, os, httpx
FSM_DIR = "/srv/memory/fsm/items"
def analyze_item(item_path):
    with open(item_path) as f:
        item = json.load(f)
    title = item.get("title", "unknown")
    prompt = f"Rate this video title 0-100: {title}"
    try:
        r = httpx.post("http://127.0.0.1:11434/api/generate",
            json={"model":"llama3.1:8b-instruct-q4_K_M","prompt":prompt,"stream":False}, timeout=60)
        resp = r.json().get("response","50").strip()
        score = int("".join(c for c in resp if c.isdigit())[:3] or 50)
        item["ai_score"] = max(0, min(score, 100))
        item["state"] = "analyzed"
    except Exception:
        item["ai_score"] = 50
        item["state"] = "analyzed"
    with open(item_path, "w") as f: json.dump(item, f)
while True:
    for name in os.listdir(FSM_DIR):
        path = os.path.join(FSM_DIR, name)
        if not path.endswith(".json"): continue
        with open(path) as f: item = json.load(f)
        if item.get("state") == "probed": analyze_item(path)
    time.sleep(5)
