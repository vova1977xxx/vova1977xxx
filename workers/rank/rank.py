import json
import json,pathlib,time
FSM_DIR="/srv/memory/fsm/items"
def load_items():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try: yield f,json.load(open(f))
        except: continue
def save_item(p,d):
    t=str(p)+".tmp"; json.dump(d,open(t,"w")); pathlib.Path(t).replace(p)
def compute_score(item):
    base=item.get("score",0)
    ai=item.get("ai_score",0.5)
    dur=item.get("duration",0)
    dur_bonus=1 if 5<dur<180 else 0
    return base + ai + dur_bonus + source_bonus(item.get("src",""))
def main():
    for path,item in load_items():
        if item.get("state")!="analyzed": continue
        item["score"]=compute_score(item)
        item["ranked_at"]=int(time.time())
        item["state"]="ranked"
        save_item(path,item)
if __name__=="__main__": main()
def source_bonus(src):
    try:
        db=json.load(open(SRC_DB))
        return db.get(src,0)*0.1
    except:
        return 0
