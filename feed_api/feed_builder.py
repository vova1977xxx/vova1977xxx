import time, json, os
FSM_DIR="/srv/memory/fsm/items"
OUT="/srv/memory/feed/index.json"
while True:
    feed=[]
    for n in os.listdir(FSM_DIR):
        p=os.path.join(FSM_DIR,n)
        if not p.endswith(".json"): continue
        with open(p) as f: item=json.load(f)
        if item.get("state")=="ranked": feed.append(item)
    feed.sort(key=lambda x: x.get("rank_score",0), reverse=True)
    with open(OUT,"w") as f: json.dump({"feed":feed[:50]},f)
    time.sleep(10)
