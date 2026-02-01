import time, json, uuid
OUT="/srv/memory/fsm/items"
while True:
    vid=str(uuid.uuid4())[:8]
    item = {}
    item["id"]=vid
    item["title"]=f"Viral Video {vid}"
    item["url"]="https://example.com/video.mp4"
    item["state"]="probed"
    item["freshness"]=70
    with open(f"{OUT}/{vid}.json","w") as f: json.dump(item,f)
    time.sleep(30)
