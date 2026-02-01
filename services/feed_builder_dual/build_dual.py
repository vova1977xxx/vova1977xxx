import json, pathlib

OUT="/srv/web/feed/feed.json"
FSM="/srv/memory/fsm/items"

feed=[]

for f in pathlib.Path(FSM).glob("*.json"):
    try:
        d=json.load(open(f))
        if d.get("state")=="published" and "download_path" in d:
            feed.append({
                "id":d["id"],
                "video":d["download_path"].replace("/srv/web",""),
                "w":d.get("width",0),
                "h":d.get("height",0),
                "dur":d.get("duration",0)
            })
    except: pass

json.dump({"feed":feed},open(OUT,"w"))
print("FEED BUILT:",len(feed))
