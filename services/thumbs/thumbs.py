import os,json,glob,subprocess
FSM_DIR="/srv/memory/fsm/items"
OUT_DIR="/srv/web/feed/thumbs"
os.makedirs(OUT_DIR,exist_ok=True)

def load(p): return json.load(open(p))
def save(p,o):
    t=p+".tmp"; json.dump(o,open(t,"w"),ensure_ascii=False,indent=2); os.replace(t,p)

def mk(s,o): subprocess.run(["ffmpeg","-y","-movflags","+faststart","-ss","1","-i",s,"-vframes","1","-q:v","4",o],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

for p in glob.glob(FSM_DIR+"/*.json"):
    it=load(p)
    if it.get("state")!="ranked": continue
    vid=str(it.get("id") or os.path.basename(p).replace(".json",""))
    if it.get("thumb_url"): continue
    mp4=it.get("publish_path") or it.get("download_path")
    if not mp4 or not os.path.exists(mp4): continue
    out=f"{OUT_DIR}/{vid}.jpg"
    if not os.path.exists(out): mk(mp4,out)
    if os.path.exists(out):
        it["thumb_url"]=f"/feed/thumbs/{vid}.jpg"
        save(p,it)
