import os,json,pathlib,time,random
FSM_DIR="/srv/memory/fsm/items"
OUT="/srv/memory/feed/index.json"
def load_ranked():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try:
            i=json.load(open(f))
            if i.get("state")=="ranked": yield i
        except: continue
def score_items(items):
    now=time.time()
    for i in items:
        age=now-i.get("ranked_at",now)
        fresh=max(0,1-(age/86400))
        i["final_score"]=i.get("score",0)+fresh
        i["trend"]=i["final_score"]/(1+(age/3600))
    return items
def diversify(items):
    out=[]; seen=set()
    for i in sorted(items,key=lambda x:x.get("trend",0),reverse=True):
        key=i.get("aspect_ratio")
        if key in seen: out.insert(random.randint(0,len(out)),i)
        else: out.append(i); seen.add(key)
    return out
def build():
    os.makedirs("/srv/memory/feed",exist_ok=True)
    items=list(load_ranked())
    items=score_items(items)
    items=diversify(items)
    feed=[{
        "id":i["id"],
        "url":i["download_path"].replace("/srv/web",""),
        "score":i["trend"],
        "duration":i.get("duration")
    } for i in items]
    json.dump({"feed":feed},open(OUT,"w"))
if __name__=="__main__": build()
