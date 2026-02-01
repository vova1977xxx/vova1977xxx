import time, json, os
FSM_DIR="/srv/memory/fsm/items"
def rank_item(path):
    with open(path) as f: item=json.load(f)
    ai=item.get("ai_score",50)
    freshness=item.get("freshness",50)
    item["rank_score"]=int(ai*0.7 + freshness*0.3)
    item["state"]="ranked"
    with open(path,"w") as f: json.dump(item,f)
while True:
    for name in os.listdir(FSM_DIR):
        p=os.path.join(FSM_DIR,name)
        if not p.endswith(".json"): continue
        with open(p) as f: item=json.load(f)
        if item.get("state")=="analyzed": rank_item(p)
    time.sleep(5)
