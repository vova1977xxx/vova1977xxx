import json,pathlib,time
from fastapi import FastAPI, Request

FSM_DIR="/srv/memory/fsm/items"
SRC_DB="/srv/memory/brain/source_scores.json"
app=FastAPI()

def load_sources():
    if not pathlib.Path(SRC_DB).exists(): return {}
    return json.load(open(SRC_DB))

def save_sources(d):
    json.dump(d,open(SRC_DB,"w"))
def apply_rules(item):
    dur=item.get("duration",0)
    ai=item.get("ai_score",0.5)
    score=item.get("score",0)

    if dur>300: score-=1
    if ai<0.3: score-=1
    if ai>0.7: score+=1

    age=time.time()-item.get("ranked_at",time.time())
    if age>3600: score+=0.5
    if age>21600: score+=1

    if score<0: item["state"]="dropped"
    item["score"]=score
    return item
def update_source(item):
    src=item.get("src","unknown")
    db=load_sources()
    s=db.get(src,0)

    if item.get("state")=="dropped": s-=1
    if item.get("state")=="ranked": s+=0.5

    if s<-5: db[src]="DISABLED"
    else: db[src]=s

    save_sources(db)
def run_brain():
    for f in pathlib.Path(FSM_DIR).glob("*.json"):
        try:
            item=json.load(open(f))
            if item.get("state")=="ranked":
                item=apply_rules(item)
                update_source(item)
                json.dump(item,open(f,"w"))
        except: pass
@app.post("/api/like")
async def like(req: Request):
    run_brain()
    return {"ok":True}

@app.post("/api/brain")
def brain():
    run_brain()
    return {"brain":"done"}
